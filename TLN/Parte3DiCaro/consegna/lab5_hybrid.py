import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Hybrid Search RAG: confronto RAG base (SciBERT + FAISS) vs ibrido (+ BM25,
# fuso con Reciprocal Rank Fusion) al variare di N_DOCS e di k.
# TLN 2025/2026 - Prof. Di Caro.
#
# I corpus a N_DOCS diversi sono sovrainsiemi annidati (il dataset e' mischiato
# una sola volta e ogni N_DOCS prende i primi N di quell'ordine fisso):
# altrimenti un paper potrebbe comparire in un campione e non nell'altro per
# puro caso di campionamento, invalidando il confronto al variare di N_DOCS.

import re
import torch
import faiss
import numpy as np
import pandas as pd
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from rank_bm25 import BM25Okapi
import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    from nltk.corpus import stopwords as nltk_sw
    try:
        STOPWORDS = set(nltk_sw.words('english'))
    except LookupError:
        import nltk
        nltk.download('stopwords', quiet=True)
        STOPWORDS = set(nltk_sw.words('english'))
except Exception as e:
    print(f"[WARN] Stopwords NLTK non disponibili ({e}): faithfulness_proxy "
          "conterà anche le function word (that, with, this, ...).")
    STOPWORDS = set()

N_DOCS_LIST   = [1000, 5000, 15000, 25000]  # il dataset completo si aggiunge sotto
K_VALUES      = [3, 10, 15]  # valori di k diversi da 5 (confrontato a parte piu' sotto)
RANDOM_STATE  = 42
PER_DOC_CHARS = 800  # per singolo paper nel contesto, non sul blocco intero:
                      # cosi' tutti i k paper entrano nel prompt anche per k grandi
EMBEDDING_MODEL = "allenai/scibert_scivocab_uncased"
LLM_MODEL       = "microsoft/Phi-3.5-mini-instruct"

GOLD_STANDARD = {
    "What is BERT and how does self-attention work?": [
        "bert", "attention", "transformer", "language model", "pre-training"
    ],
    "How does word2vec represent word meaning?": [
        "word2vec", "skip-gram", "word embedding", "word representation", "word vector"
    ],
    "What are the main challenges in machine translation?": [
        "machine translation", "neural machine translation", "translation", "nmt"
    ],
    "How does topic modeling work?": [
        "topic model", "lda", "bertopic", "topic", "clustering"
    ],
    "What is named entity recognition?": [
        "named entity", "ner", "entity recognition", "sequence labeling"
    ]
}

PARAPHRASES = {
    "What is BERT and how does self-attention work?": [
        "Explain the BERT model and its attention mechanism",
        "How does the transformer attention operate in BERT?",
    ],
    "How does word2vec represent word meaning?": [
        "What technique does word2vec use to learn word embeddings?",
        "Explain skip-gram and CBOW in word representation",
    ],
    "What are the main challenges in machine translation?": [
        "What makes neural machine translation difficult?",
        "Describe the open problems in NMT systems",
    ],
}

EVAL_QUERIES = list(GOLD_STANDARD.keys())


def match_kw(text, keywords):
    """Match per parola intera: un semplice 'kw in text' farebbe matchare
    'ner' con 'corner' o 'bert' con 'roberta'."""
    text = text.lower()
    return any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in keywords)


def tok(text):
    """Tokenizzazione per BM25 basata su \\w+: split() lascerebbe la punteggiatura
    attaccata ai token (es. 'BERT,' o 'work?'), che non matchano mai le query pulite."""
    return re.findall(r'\w+', text.lower())


def sep(char="=", n=70): print(char * n)
def header(title): sep(); print(f"  {title}"); sep()

def print_table(headers, rows, col_widths):
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + 2 * (len(col_widths) - 1)))
    for row in rows:
        print(fmt.format(*[str(x) for x in row]))

header("STEP 1 — Caricamento dataset completo")

dataset = load_dataset("MaartenGr/arxiv_nlp")
df_full = pd.DataFrame(dataset['train'])
print(f"  Documenti totali disponibili: {len(df_full)}")

if len(df_full) not in N_DOCS_LIST:
    N_DOCS_LIST.append(len(df_full))

# generazione per ogni k solo sul corpus piu' piccolo (costosa su CPU); sugli
# altri N_DOCS si misura solo il retrieval (Precision@k, Context Relevance)
GEN_N_DOCS = {min(N_DOCS_LIST)}

title_col    = next((c for c in df_full.columns if 'title'    in c.lower()), df_full.columns[0])
abstract_col = next((c for c in df_full.columns if 'abstract' in c.lower()
                     or 'summar' in c.lower()), df_full.columns[1])
year_col     = next((c for c in df_full.columns if 'year'     in c.lower()), None)

df_shuffled = df_full.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
MAX_N_DOCS  = max(N_DOCS_LIST)


def build_corpus(df, n):
    """Prende i primi n documenti di un dataframe già mischiato una volta sola."""
    df_s = df.head(n).reset_index(drop=True)
    docs, meta = [], []
    for _, row in df_s.iterrows():
        title    = str(row[title_col])    if pd.notna(row[title_col])    else 'No Title'
        abstract = str(row[abstract_col]) if pd.notna(row[abstract_col]) else 'No Abstract'
        year     = str(row[year_col])     if year_col and pd.notna(row[year_col]) else 'Unknown'
        docs.append(f"Title: {title}\n\nAbstract: {abstract}")
        meta.append({'title': title, 'year': year})
    return docs, meta

header("STEP 2 — Caricamento SciBERT")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
print("  SciBERT caricato.")


def build_faiss_index(embeddings):
    """Costruisce l'indice FAISS (IndexFlatIP) da embeddings già calcolati."""
    idx = faiss.IndexFlatIP(embeddings.shape[1])
    idx.add(embeddings.astype(np.float32))
    return idx


# corpus ed embeddings calcolati una sola volta sul corpus piu' grande: i corpus
# piu' piccoli si ottengono per slicing, senza ricodificare a ogni N_DOCS
print(f"  Costruzione corpus completo ({MAX_N_DOCS:,} documenti) ed embeddings...")
all_documents, all_metadata = build_corpus(df_shuffled, MAX_N_DOCS)

# cache su disco taggata col modello (condivisa con lab5rag.py a parita' di
# shuffle/corpus/modello): evita di ricodificare 44.949 abstract ad ogni run
model_tag = EMBEDDING_MODEL.split('/')[-1]
EMB_CACHE_PATH = f"embeddings_{model_tag}_{MAX_N_DOCS}.npy"
EMB_CACHE_META_PATH = f"embeddings_{model_tag}_{MAX_N_DOCS}.meta.txt"
emb_signature = f"{MAX_N_DOCS}|{RANDOM_STATE}|{EMBEDDING_MODEL}|{all_documents[0][:80]}|{all_documents[-1][:80]}"

if (os.path.exists(EMB_CACHE_PATH) and os.path.exists(EMB_CACHE_META_PATH)
        and open(EMB_CACHE_META_PATH, encoding="utf-8").read() == emb_signature):
    print(f"  Embeddings trovati in cache ({EMB_CACHE_PATH}), li ricarico...")
    all_embeddings = np.load(EMB_CACHE_PATH)
else:
    all_embeddings = embedding_model.encode(
        all_documents, show_progress_bar=True,
        batch_size=64, convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)
    np.save(EMB_CACHE_PATH, all_embeddings)
    with open(EMB_CACHE_META_PATH, "w", encoding="utf-8") as f:
        f.write(emb_signature)
print(f"  Embeddings disponibili: {all_embeddings.shape}")

header("STEP 3 — Caricamento Phi-3.5-mini-instruct")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"  Device: {'CUDA (GPU)' if torch.cuda.is_available() else 'CPU'}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
model     = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    low_cpu_mem_usage=True
)
llm = pipeline(
    'text-generation', model=model, tokenizer=tokenizer,
    max_new_tokens=300, do_sample=False,   # greedy: riproducibile fra run
    return_full_text=False,                # solo il testo generato, non prompt+testo
    pad_token_id=tokenizer.eos_token_id,
    clean_up_tokenization_spaces=False
)
print("  Modello caricato.")


def build_bm25_index(documents):
    tokenized = [tok(doc) for doc in documents]
    return BM25Okapi(tokenized), tokenized


def retrieve_semantic(query, faiss_index, documents, metadata, k=10):
    qe = embedding_model.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)
    sims, idxs = faiss_index.search(qe, k)
    return [
        {'rank': i+1, 'score': float(s), 'idx': int(ix),
         'document': documents[ix], 'metadata': metadata[ix]}
        for i, (s, ix) in enumerate(zip(sims[0], idxs[0]))
    ]


def retrieve_bm25(query, bm25, documents, metadata, k=10):
    scores = bm25.get_scores(tok(query))
    top    = np.argsort(scores)[::-1][:k]
    return [
        {'rank': i+1, 'score': float(scores[ix]), 'idx': int(ix),
         'document': documents[ix], 'metadata': metadata[ix]}
        for i, ix in enumerate(top)
    ]


def reciprocal_rank_fusion(results_list, k=60):
    rrf_scores, doc_map = {}, {}
    for results in results_list:
        for item in results:
            ix = item['idx']
            rrf_scores[ix] = rrf_scores.get(ix, 0) + 1 / (k + item['rank'])
            doc_map[ix]    = item
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {'rank': i+1, 'rrf_score': score, 'idx': ix,
         'document': doc_map[ix]['document'], 'metadata': doc_map[ix]['metadata']}
        for i, (ix, score) in enumerate(sorted_docs)
    ]


def retrieve_hybrid(query, faiss_index, bm25, documents, metadata, k=5):
    sem = retrieve_semantic(query, faiss_index, documents, metadata, k=20)
    bm  = retrieve_bm25(query, bm25, documents, metadata, k=20)
    return reciprocal_rank_fusion([sem, bm])[:k]


def rag_answer(query, results):
    # niente titolo anteposto: r['document'] inizia gia' con "Title: ...", altrimenti
    # il titolo comparirebbe due volte nel prompt
    context_parts = [
        f"[Paper {r['rank']}]\n{r['document'][:PER_DOC_CHARS]}"
        for r in results
    ]
    context = "\n\n".join(context_parts)
    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant specialized in NLP research. "
            "Answer questions based only on the provided research papers. "
            "Always cite the paper numbers [Paper X] you used. "
            "If the context is insufficient, say so clearly."
        )},
        {"role": "user", "content": (
            f"Context from research papers:\n\n{context}\n\nQuestion: {query}\n\nAnswer based on the context above, citing paper numbers:"
        )}
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    output = llm(prompt)
    return output[0]['generated_text'].strip()


def precision_at_k(results, relevant_keywords, k=5):
    return sum(
        1 for r in results[:k] if match_kw(r['document'], relevant_keywords)
    ) / k


def context_relevance(query, results):
    qe   = embedding_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    snip = [r['document'][:200] for r in results]
    de   = embedding_model.encode(snip, convert_to_numpy=True, normalize_embeddings=True)
    return float(np.mean(de @ qe.T))


def answer_relevance(query, answer):
    embs = embedding_model.encode([query, answer], convert_to_numpy=True, normalize_embeddings=True)
    return float(embs[0] @ embs[1])


def faithfulness_proxy(answer, results):
    # stessa finestra di rag_answer (PER_DOC_CHARS), altrimenti la faithfulness
    # sarebbe sottostimata rispetto al contesto che l'LLM ha visto davvero.
    # Match per insieme di parole, non substring ("that" altrimenti matcherebbe
    # "mathematical"); "paper" escluso perche' compare sempre nelle citazioni,
    # a prescindere da quanto la risposta sia davvero fondata sul contesto.
    context_text  = ' '.join(r['document'][:PER_DOC_CHARS] for r in results).lower()
    context_words = set(re.findall(r'\b[a-z]{4,}\b', context_text)) - {'paper'}
    words         = re.findall(r'\b[a-z]{4,}\b', answer.lower())
    content_words = [w for w in words if w not in STOPWORDS and w != 'paper']
    if not content_words:
        return 0.0
    return sum(1 for w in content_words if w in context_words) / len(content_words)


def robustness_test(query, paraphrases, retrieve_fn, k=5):
    """Overlap fra i top-k di una query e delle sue parafrasi, secondo la funzione
    di retrieval passata (cosi' si puo' confrontare la robustezza base vs ibrido)."""
    base_titles = {r['metadata']['title'] for r in retrieve_fn(query, k)}
    overlaps = []
    for para in paraphrases:
        para_titles = {r['metadata']['title'] for r in retrieve_fn(para, k)}
        overlaps.append(len(base_titles & para_titles) / k)
    return float(np.mean(overlaps))


all_results   = []   # un dict per N_DOCS (metriche a k=5)
qa_rows       = []   # risposte base/ibrido a k=5, per esempi qualitativi nel report
k_detail_rows = []   # Precision@k / Context Relevance per (n_docs, k in K_VALUES)
k_gen_rows    = []   # Answer Relevance / Faithfulness per k, solo per N_DOCS in GEN_N_DOCS
k_gen_qa_rows = []   # risposte della variazione di k, per esempi qualitativi nel report

for N_DOCS in N_DOCS_LIST:

    header(f"ESPERIMENTO  N_DOCS = {N_DOCS:,}")

    print(f"\n  [1/3] Corpus per N_DOCS={N_DOCS:,} (slice del corpus completo)...")
    documents   = all_documents[:N_DOCS]
    metadata    = all_metadata[:N_DOCS]
    faiss_index = build_faiss_index(all_embeddings[:N_DOCS])

    print(f"  [2/3] Costruzione indice BM25...")
    bm25_index, _ = build_bm25_index(documents)

    print(f"\n  [3/3] Valutazione Precision@5...")
    p5_base_list, p5_hyb_list = [], []

    for query, keywords in GOLD_STANDARD.items():
        base_res  = retrieve_semantic(query, faiss_index, documents, metadata, k=5)
        hybrid_res = retrieve_hybrid(query, faiss_index, bm25_index, documents, metadata, k=5)
        p5_base_list.append(precision_at_k(base_res,   keywords))
        p5_hyb_list.append(precision_at_k(hybrid_res, keywords))

    avg_p5_base = np.mean(p5_base_list)
    avg_p5_hyb  = np.mean(p5_hyb_list)

    cr_base_list, cr_hyb_list = [], []
    ar_base_list, ar_hyb_list = [], []
    ff_base_list, ff_hyb_list = [], []

    for query in EVAL_QUERIES:
        base_res   = retrieve_semantic(query, faiss_index, documents, metadata, k=5)
        hybrid_res = retrieve_hybrid(query, faiss_index, bm25_index, documents, metadata, k=5)
        ans_base   = rag_answer(query, base_res)
        ans_hybrid = rag_answer(query, hybrid_res)

        cr_base_list.append(context_relevance(query, base_res))
        cr_hyb_list.append(context_relevance(query, hybrid_res))
        ar_base_list.append(answer_relevance(query, ans_base))
        ar_hyb_list.append(answer_relevance(query, ans_hybrid))
        ff_base_list.append(faithfulness_proxy(ans_base,   base_res))
        ff_hyb_list.append(faithfulness_proxy(ans_hybrid, hybrid_res))

        qa_rows.append({
            'n_docs': N_DOCS, 'query': query,
            'answer_base': ans_base, 'answer_hybrid': ans_hybrid,
            'answer_relevance_base': ar_base_list[-1], 'answer_relevance_hybrid': ar_hyb_list[-1],
            'faithfulness_base': ff_base_list[-1], 'faithfulness_hybrid': ff_hyb_list[-1],
        })

    # overlap@5 fra query e parafrasi: vede se la fusione con BM25 stabilizza il retrieval
    rob_base_scores, rob_hyb_scores = [], []
    for query, paras in PARAPHRASES.items():
        rob_base_scores.append(robustness_test(
            query, paras,
            lambda q, k: retrieve_semantic(q, faiss_index, documents, metadata, k=k)
        ))
        rob_hyb_scores.append(robustness_test(
            query, paras,
            lambda q, k: retrieve_hybrid(q, faiss_index, bm25_index, documents, metadata, k=k)
        ))
    avg_rob_base = float(np.mean(rob_base_scores))
    avg_rob_hyb  = float(np.mean(rob_hyb_scores))

    # variazione di k: Precision@k/Context Relevance per ogni N_DOCS (economico,
    # solo retrieval); Answer Relevance/Faithfulness (generazione, costosa su
    # CPU) solo per i corpus in GEN_N_DOCS
    print(f"\n  [4/4] Confronto k={K_VALUES} (base vs ibrido)...")
    for k in K_VALUES:
        pk_base_list, pk_hyb_list = [], []
        crk_base_list, crk_hyb_list = [], []
        for query, keywords in GOLD_STANDARD.items():
            base_res_k   = retrieve_semantic(query, faiss_index, documents, metadata, k=k)
            hybrid_res_k = retrieve_hybrid(query, faiss_index, bm25_index, documents, metadata, k=k)
            pk_base_list.append(precision_at_k(base_res_k, keywords, k=k))
            pk_hyb_list.append(precision_at_k(hybrid_res_k, keywords, k=k))
            crk_base_list.append(context_relevance(query, base_res_k))
            crk_hyb_list.append(context_relevance(query, hybrid_res_k))

        k_detail_rows.append({
            'n_docs': N_DOCS, 'k': k,
            'p_base':  float(np.mean(pk_base_list)),  'p_hyb':  float(np.mean(pk_hyb_list)),
            'cr_base': float(np.mean(crk_base_list)), 'cr_hyb': float(np.mean(crk_hyb_list)),
        })

    print(f"\n  {'k':>4} {'P@k Base':>10} {'P@k Hyb':>10} {'CR Base':>10} {'CR Hyb':>10}")
    print(f"  {'-' * 48}")
    for row in k_detail_rows:
        if row['n_docs'] != N_DOCS:
            continue
        print(f"  {row['k']:>4} {row['p_base']:>10.3f} {row['p_hyb']:>10.3f} "
              f"{row['cr_base']:>10.3f} {row['cr_hyb']:>10.3f}")

    if N_DOCS in GEN_N_DOCS:
        print(f"\n  Generazione risposte per k={K_VALUES} (N_DOCS={N_DOCS:,}, in GEN_N_DOCS)...")
        for k in K_VALUES:
            ar_base_k, ar_hyb_k, ff_base_k, ff_hyb_k = [], [], [], []
            for query in EVAL_QUERIES:
                base_res_k   = retrieve_semantic(query, faiss_index, documents, metadata, k=k)
                hybrid_res_k = retrieve_hybrid(query, faiss_index, bm25_index, documents, metadata, k=k)
                ans_base_k   = rag_answer(query, base_res_k)
                ans_hybrid_k = rag_answer(query, hybrid_res_k)

                ar_base_k.append(answer_relevance(query, ans_base_k))
                ar_hyb_k.append(answer_relevance(query, ans_hybrid_k))
                ff_base_k.append(faithfulness_proxy(ans_base_k, base_res_k))
                ff_hyb_k.append(faithfulness_proxy(ans_hybrid_k, hybrid_res_k))

                k_gen_qa_rows.append({
                    'n_docs': N_DOCS, 'k': k, 'query': query,
                    'answer_base': ans_base_k, 'answer_hybrid': ans_hybrid_k,
                    'answer_relevance_base': ar_base_k[-1], 'answer_relevance_hybrid': ar_hyb_k[-1],
                    'faithfulness_base': ff_base_k[-1], 'faithfulness_hybrid': ff_hyb_k[-1],
                })

            k_gen_rows.append({
                'n_docs': N_DOCS, 'k': k,
                'ar_base': float(np.mean(ar_base_k)), 'ar_hyb': float(np.mean(ar_hyb_k)),
                'ff_base': float(np.mean(ff_base_k)), 'ff_hyb': float(np.mean(ff_hyb_k)),
            })
            print(f"    k={k:>2}: AR base={np.mean(ar_base_k):.3f} hyb={np.mean(ar_hyb_k):.3f}  "
                  f"FF base={np.mean(ff_base_k):.3f} hyb={np.mean(ff_hyb_k):.3f}")

    all_results.append({
        'n_docs':     N_DOCS,
        'p5_base':    avg_p5_base,
        'p5_hyb':     avg_p5_hyb,
        'cr_base':    np.mean(cr_base_list),
        'cr_hyb':     np.mean(cr_hyb_list),
        'ar_base':    np.mean(ar_base_list),
        'ar_hyb':     np.mean(ar_hyb_list),
        'ff_base':    np.mean(ff_base_list),
        'ff_hyb':     np.mean(ff_hyb_list),
        'robustness_base': avg_rob_base,
        'robustness_hyb':  avg_rob_hyb,
        'p5_base_detail': dict(zip(GOLD_STANDARD.keys(), p5_base_list)),
        'p5_hyb_detail':  dict(zip(GOLD_STANDARD.keys(), p5_hyb_list)),
    })

    print(f"\n  Risultati N_DOCS={N_DOCS:,}")
    print(f"  {'Metrica':<25} {'Base':>8} {'Ibrido':>8} {'Delta':>8}")
    print(f"  {'-'*52}")
    for label, kb, kh in [
        ("Precision@5",       'p5_base',  'p5_hyb'),
        ("Context Relevance", 'cr_base',  'cr_hyb'),
        ("Answer Relevance",  'ar_base',  'ar_hyb'),
        ("Faithfulness",      'ff_base',  'ff_hyb'),
        ("Robustezza",        'robustness_base', 'robustness_hyb'),
    ]:
        b = all_results[-1][kb]
        h = all_results[-1][kh]
        print(f"  {label:<25} {b:>8.3f} {h:>8.3f} {h-b:>+8.3f}")

header("RIEPILOGO COMPARATIVO — variazione di N_DOCS")

print("\n  PRECISION@5 (media su 5 query)")
print(f"\n  {'N_DOCS':<10} {'Base':>8} {'Ibrido':>8} {'Delta':>8} {'Miglioramento':>15}")
print(f"  {'-'*54}")
for r in all_results:
    delta = r['p5_hyb'] - r['p5_base']
    pct   = (delta / max(r['p5_base'], 0.001)) * 100
    print(f"  {r['n_docs']:<10,} {r['p5_base']:>8.3f} {r['p5_hyb']:>8.3f} {delta:>+8.3f} {pct:>+14.1f}%")

print("\n\n  METRICHE COMPLETE PER N_DOCS")
metrics = [
    ("Precision@5", 'p5_base',  'p5_hyb'),
    ("CR",          'cr_base',  'cr_hyb'),
    ("AR",          'ar_base',  'ar_hyb'),
    ("FF",          'ff_base',  'ff_hyb'),
    ("Rob",         'robustness_base', 'robustness_hyb'),
]
header_cols = ["N_DOCS"] + [f"{m}_B" for m, *_ in metrics] + [f"{m}_H" for m, *_ in metrics]
col_w = [8] + [7] * (len(metrics) * 2)
print("\n  " + "  ".join(f"{h:>{w}}" for h, w in zip(header_cols, col_w)))
print(f"  {'-' * (sum(col_w) + 2 * len(col_w))}")
for r in all_results:
    vals = [f"{r['n_docs']:,}"]
    for _, kb, _ in metrics:
        vals.append(f"{r[kb]:.3f}")
    for _, _, kh in metrics:
        vals.append(f"{r[kh]:.3f}")
    print("  " + "  ".join(f"{v:>{w}}" for v, w in zip(vals, col_w)))

print("\n\n  PRECISION@5 IBRIDO — dettaglio per query al variare di N_DOCS")
col_w2 = [37] + [8] * len(N_DOCS_LIST)
print("\n  " + f"{'Query':<37}" + "  ".join(f"{'N='+str(n):>{8}}" for n in N_DOCS_LIST))
print(f"  {'-' * (37 + 10 * len(N_DOCS_LIST))}")
for i, q in enumerate(GOLD_STANDARD.keys()):
    row = f"  {q[:36]:<37}"
    for r in all_results:
        row += f"  {r['p5_hyb_detail'][q]:>6.2f}  "
    print(row)

print("\n\n  ROBUSTEZZA (overlap@5 su query parafrasate): base vs ibrido")
print(f"\n  {'N_DOCS':<10} {'Base':>8} {'Ibrido':>8}")
print(f"  {'-'*28}")
for r in all_results:
    print(f"  {r['n_docs']:<10,} {r['robustness_base']:>8.3f} {r['robustness_hyb']:>8.3f}")

print(f"\n\n  VARIAZIONE DI k (k={K_VALUES}, oltre al k=5 già confrontato sopra) — "
      "Precision@k e Context Relevance")
print(f"\n  {'N_DOCS':<10} {'k':>4} {'P@k Base':>10} {'P@k Hyb':>10} {'CR Base':>10} {'CR Hyb':>10}")
print(f"  {'-'*56}")
for row in k_detail_rows:
    print(f"  {row['n_docs']:<10,} {row['k']:>4} {row['p_base']:>10.3f} {row['p_hyb']:>10.3f} "
          f"{row['cr_base']:>10.3f} {row['cr_hyb']:>10.3f}")

print(f"\n\n  VARIAZIONE DI k — Answer Relevance e Faithfulness "
      f"(solo N_DOCS in GEN_N_DOCS={sorted(GEN_N_DOCS)}, generazione costosa su CPU)")
print(f"\n  {'N_DOCS':<10} {'k':>4} {'AR Base':>10} {'AR Hyb':>10} {'FF Base':>10} {'FF Hyb':>10}")
print(f"  {'-'*56}")
for row in k_gen_rows:
    print(f"  {row['n_docs']:<10,} {row['k']:>4} {row['ar_base']:>10.3f} {row['ar_hyb']:>10.3f} "
          f"{row['ff_base']:>10.3f} {row['ff_hyb']:>10.3f}")

# salva su CSV cosi' i numeri/risposte per la relazione non vanno ricopiati a
# mano dallo stdout, ne' richiedono di rilanciare l'intero esperimento
detail_rows = [
    {'n_docs': r['n_docs'], 'query': q,
     'p5_base': r['p5_base_detail'][q], 'p5_hyb': r['p5_hyb_detail'][q]}
    for r in all_results for q in r['p5_base_detail']
]
summary_df = pd.DataFrame([
    {k: v for k, v in r.items() if k not in ('p5_base_detail', 'p5_hyb_detail')}
    for r in all_results
])
summary_df.to_csv('risultati_hybrid_ndocs.csv', index=False)
pd.DataFrame(detail_rows).to_csv('risultati_hybrid_p5_detail.csv', index=False)
pd.DataFrame(k_detail_rows).to_csv('risultati_hybrid_k_detail.csv', index=False)
pd.DataFrame(k_gen_rows).to_csv('risultati_hybrid_k_gen_detail.csv', index=False)
pd.DataFrame(k_gen_qa_rows).to_csv('risultati_hybrid_k_gen_risposte.csv', index=False)
pd.DataFrame(qa_rows).to_csv('risultati_hybrid_risposte.csv', index=False)

print("\n  Salvati: risultati_hybrid_ndocs.csv, risultati_hybrid_p5_detail.csv, "
      "risultati_hybrid_k_detail.csv, risultati_hybrid_k_gen_detail.csv, "
      "risultati_hybrid_k_gen_risposte.csv, risultati_hybrid_risposte.csv")

header("ESPERIMENTO COMPLETATO")
