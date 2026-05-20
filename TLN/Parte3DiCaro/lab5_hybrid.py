import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ============================================================
# PROGETTO ESTESO - Hybrid Search RAG (Esperimento N_DOCS)
# Tecnologie del Linguaggio Naturale - Prof. Di Caro
# A.A. 2025/2026
#
# Esperimento: confronto RAG base vs ibrido al variare
# della dimensione del corpus (N_DOCS).
# ============================================================

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

# ============================================================
# CONFIGURAZIONE ESPERIMENTO
# ============================================================

N_DOCS_LIST   = [1000, 5000, 15000,25000,44949]  # valori da testare
RANDOM_STATE  = 42
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

# ============================================================
# UTILITY: stampa separatori e tabelle
# ============================================================

def sep(char="=", n=70): print(char * n)
def header(title): sep(); print(f"  {title}"); sep()

def print_table(headers, rows, col_widths):
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + 2 * (len(col_widths) - 1)))
    for row in rows:
        print(fmt.format(*[str(x) for x in row]))

# ============================================================
# STEP 1: Caricamento dataset completo (una volta sola)
# ============================================================
header("STEP 1 — Caricamento dataset completo")

dataset = load_dataset("MaartenGr/arxiv_nlp")
df_full = pd.DataFrame(dataset['train'])
print(f"  Documenti totali disponibili: {len(df_full)}")

title_col    = next((c for c in df_full.columns if 'title'    in c.lower()), df_full.columns[0])
abstract_col = next((c for c in df_full.columns if 'abstract' in c.lower()
                     or 'summar' in c.lower()), df_full.columns[1])
year_col     = next((c for c in df_full.columns if 'year'     in c.lower()), None)

# ============================================================
# STEP 2: Caricamento modello embedding (una volta sola)
# ============================================================
header("STEP 2 — Caricamento SciBERT")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
print("  SciBERT caricato.")

# ============================================================
# STEP 3: Caricamento LLM (una volta sola)
# ============================================================
header("STEP 3 — Caricamento Phi-3.5-mini-instruct")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"  Device: {'CUDA (GPU)' if torch.cuda.is_available() else 'CPU'}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
model     = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    low_cpu_mem_usage=True
)
llm = pipeline(
    'text-generation', model=model, tokenizer=tokenizer,
    max_new_tokens=300, do_sample=True, temperature=0.3,
    pad_token_id=tokenizer.eos_token_id,
    clean_up_tokenization_spaces=False
)
print("  Modello caricato.")

# ============================================================
# FUNZIONI DI RETRIEVAL E VALUTAZIONE
# ============================================================

def build_corpus(df, n):
    """Campiona n documenti e costruisce liste documenti/metadata."""
    df_s = df.sample(n=n, random_state=RANDOM_STATE).reset_index(drop=True)
    docs, meta = [], []
    for _, row in df_s.iterrows():
        title    = str(row[title_col])    if pd.notna(row[title_col])    else 'No Title'
        abstract = str(row[abstract_col]) if pd.notna(row[abstract_col]) else 'No Abstract'
        year     = str(row[year_col])     if year_col and pd.notna(row[year_col]) else 'Unknown'
        docs.append(f"Title: {title}\n\nAbstract: {abstract}")
        meta.append({'title': title, 'year': year})
    return docs, meta


def build_faiss_index(documents):
    embeddings = embedding_model.encode(
        documents, show_progress_bar=True,
        batch_size=64, convert_to_numpy=True, normalize_embeddings=True
    )
    idx = faiss.IndexFlatIP(embeddings.shape[1])
    idx.add(embeddings.astype(np.float32))
    return idx


def build_bm25_index(documents):
    tokenized = [doc.lower().split() for doc in documents]
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
    scores = bm25.get_scores(query.lower().split())
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
    context_parts = [
        f"[Paper {r['rank']}] {r['metadata']['title']}\n{r['document']}"
        for r in results
    ]
    context = "\n\n".join(context_parts)
    if len(context) > 3000:
        context = context[:3000] + "\n[...truncated...]"
    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant specialized in NLP research. "
            "Answer questions based only on the provided research papers. "
            "Always cite the paper numbers [Paper X] you used. "
            "If the context is insufficient, say so clearly."
        )},
        {"role": "user", "content": (
            f"Context from research papers:\n\n{context}\n\n"
            f"Question: {query}\n\nAnswer based on the context above, citing paper numbers:"
        )}
    ]
    prompt    = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    output    = llm(prompt)
    full_text = output[0]['generated_text']
    return full_text[len(prompt):].strip() if full_text.startswith(prompt) else full_text


def precision_at_k(results, relevant_keywords, k=5):
    return sum(
        1 for r in results[:k]
        if any(kw in r['metadata']['title'].lower() for kw in relevant_keywords)
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
    import re
    try:
        from nltk.corpus import stopwords as nltk_sw
        sw = set(nltk_sw.words('english'))
    except Exception:
        sw = set()
    context_text  = ' '.join(r['document'][:500] for r in results).lower()
    words         = re.findall(r'\b[a-z]{4,}\b', answer.lower())
    content_words = [w for w in words if w not in sw]
    if not content_words:
        return 0.0
    return sum(1 for w in content_words if w in context_text) / len(content_words)


def robustness_test(query, paraphrases, faiss_index, bm25, documents, metadata, k=5):
    base_titles = {r['metadata']['title']
                   for r in retrieve_hybrid(query, faiss_index, bm25, documents, metadata, k)}
    overlaps = []
    for para in paraphrases:
        para_titles = {r['metadata']['title']
                       for r in retrieve_hybrid(para, faiss_index, bm25, documents, metadata, k)}
        overlaps.append(len(base_titles & para_titles) / k)
    return float(np.mean(overlaps))


# ============================================================
# ESPERIMENTO PRINCIPALE
# ============================================================

# Struttura per raccogliere tutti i risultati
all_results = []   # lista di dict, uno per N_DOCS

for N_DOCS in N_DOCS_LIST:

    sep("=")
    print(f"  ESPERIMENTO  N_DOCS = {N_DOCS:,}")
    sep("=")

    # --- Costruzione corpus e indici ---
    print(f"\n  [1/4] Costruzione corpus ({N_DOCS:,} documenti)...")
    documents, metadata = build_corpus(df_full, N_DOCS)

    print(f"  [2/4] Costruzione indice FAISS...")
    faiss_index = build_faiss_index(documents)

    print(f"  [3/4] Costruzione indice BM25...")
    bm25_index, _ = build_bm25_index(documents)

    # --- Precision@5 ---
    print(f"\n  [4/4] Valutazione Precision@5...")
    p5_base_list, p5_hyb_list = [], []

    for query, keywords in GOLD_STANDARD.items():
        base_res  = retrieve_semantic(query, faiss_index, documents, metadata, k=5)
        hybrid_res = retrieve_hybrid(query, faiss_index, bm25_index, documents, metadata, k=5)
        p5_base_list.append(precision_at_k(base_res,   keywords))
        p5_hyb_list.append(precision_at_k(hybrid_res, keywords))

    avg_p5_base = np.mean(p5_base_list)
    avg_p5_hyb  = np.mean(p5_hyb_list)

    # --- Metriche LLM-based ---
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

    # --- Robustezza ---
    rob_scores = []
    for query, paras in PARAPHRASES.items():
        rob_scores.append(
            robustness_test(query, paras, faiss_index, bm25_index, documents, metadata)
        )
    avg_rob = float(np.mean(rob_scores))

    # --- Salva risultati ---
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
        'robustness': avg_rob,
        # dettaglio P@5 per query
        'p5_base_detail': dict(zip(GOLD_STANDARD.keys(), p5_base_list)),
        'p5_hyb_detail':  dict(zip(GOLD_STANDARD.keys(), p5_hyb_list)),
    })

    # --- Output intermedio per questo N_DOCS ---
    print(f"\n  Risultati N_DOCS={N_DOCS:,}")
    print(f"  {'Metrica':<25} {'Base':>8} {'Ibrido':>8} {'Delta':>8}")
    print(f"  {'-'*52}")
    for label, kb, kh in [
        ("Precision@5",       'p5_base',  'p5_hyb'),
        ("Context Relevance", 'cr_base',  'cr_hyb'),
        ("Answer Relevance",  'ar_base',  'ar_hyb'),
        ("Faithfulness",      'ff_base',  'ff_hyb'),
    ]:
        b = all_results[-1][kb]
        h = all_results[-1][kh]
        print(f"  {label:<25} {b:>8.3f} {h:>8.3f} {h-b:>+8.3f}")
    print(f"  {'Robustezza':<25} {'':>8} {avg_rob:>8.3f}")

# ============================================================
# RIEPILOGO FINALE COMPARATIVO
# ============================================================

sep("=")
print("  RIEPILOGO COMPARATIVO — variazione di N_DOCS")
sep("=")

# --- Precision@5 ---
print("\n  PRECISION@5 (media su 5 query)")
print(f"\n  {'N_DOCS':<10} {'Base':>8} {'Ibrido':>8} {'Delta':>8} {'Miglioramento':>15}")
print(f"  {'-'*54}")
for r in all_results:
    delta = r['p5_hyb'] - r['p5_base']
    pct   = (delta / max(r['p5_base'], 0.001)) * 100
    print(f"  {r['n_docs']:<10,} {r['p5_base']:>8.3f} {r['p5_hyb']:>8.3f} {delta:>+8.3f} {pct:>+14.1f}%")

# --- Tutte le metriche ---
print("\n\n  METRICHE COMPLETE PER N_DOCS")
metrics = [
    ("Precision@5", 'p5_base',  'p5_hyb'),
    ("CR",          'cr_base',  'cr_hyb'),
    ("AR",          'ar_base',  'ar_hyb'),
    ("FF",          'ff_base',  'ff_hyb'),
]
# Header
header_cols = ["N_DOCS"] + [f"{m}_B" for m, *_ in metrics] + [f"{m}_H" for m, *_ in metrics] + ["Rob"]
col_w = [8] + [7] * (len(metrics) * 2) + [6]
fmt = "  " + "  ".join(f"{{:>{w}}}" for w in col_w)
print("\n  " + "  ".join(f"{h:>{w}}" for h, w in zip(header_cols, col_w)))
print(f"  {'-' * (sum(col_w) + 2 * len(col_w))}")
for r in all_results:
    vals = [f"{r['n_docs']:,}"]
    for _, kb, _ in metrics:
        vals.append(f"{r[kb]:.3f}")
    for _, _, kh in metrics:
        vals.append(f"{r[kh]:.3f}")
    vals.append(f"{r['robustness']:.3f}")
    print("  " + "  ".join(f"{v:>{w}}" for v, w in zip(vals, col_w)))

# --- Dettaglio P@5 per query ---
print("\n\n  PRECISION@5 IBRIDO — dettaglio per query al variare di N_DOCS")
queries_short = [q[:35] for q in GOLD_STANDARD.keys()]
col_w2 = [37] + [8] * len(N_DOCS_LIST)
print("\n  " + "  ".join(f"{'N='+str(n):>{8}}" for n in ["Query"] + N_DOCS_LIST))
print(f"  {'-' * (37 + 10 * len(N_DOCS_LIST))}")
for i, q in enumerate(GOLD_STANDARD.keys()):
    row = f"  {q[:36]:<37}"
    for r in all_results:
        row += f"  {r['p5_hyb_detail'][q]:>6.2f}  "
    print(row)

# --- Robustezza ---
print("\n\n  ROBUSTEZZA (overlap@5 su query parafrasate)")
print(f"\n  {'N_DOCS':<10} {'Robustezza':>12}")
print(f"  {'-'*25}")
for r in all_results:
    print(f"  {r['n_docs']:<10,} {r['robustness']:>12.3f}")

sep("=")
print("  ESPERIMENTO COMPLETATO")
sep("=")