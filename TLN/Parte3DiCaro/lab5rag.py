import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ============================================================
# LAB-5: Sistema RAG su articoli scientifici NLP
# Tecnologie del Linguaggio Naturale - Prof. Di Caro
# A.A. 2025/2026
#
# Configurazione scelta:
#   - Dataset:   MaartenGr/arxiv_nlp (campione casuale, dimensione variabile)
#   - Embedding: SciBERT (allenai/scibert_scivocab_uncased)
#   - FAISS:     IndexFlatIP (ricerca esatta, CPU)
#   - LLM:       microsoft/Phi-3.5-mini-instruct
#   - Temp:      0.3
#
# Esperimento (risposta alle domande del Prof. Di Caro):
#   per ogni N_DOCS in N_DOCS_LIST si confrontano diversi
#   valori di k su 7 query eterogenee, misurando Precision@k,
#   Context Relevance, Answer Relevance e Faithfulness proxy.
#   Questo permette di vedere se la qualità del retrieval
#   semantico puro (senza BM25/hybrid) cambia con la dimensione
#   del corpus, oltre che con k.
# ============================================================

import re
import torch
import faiss
import numpy as np
import pandas as pd
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

print("=" * 60)
print("LAB-5: Sistema RAG - TLN 2025/2026")
print("=" * 60)
print(f"Device: {'CUDA (GPU)' if torch.cuda.is_available() else 'CPU'}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

try:
    from nltk.corpus import stopwords as nltk_sw
    STOPWORDS = set(nltk_sw.words('english'))
except Exception:
    STOPWORDS = set()

# ============================================================
# CONFIGURAZIONE ESPERIMENTO
# ============================================================
N_DOCS_LIST = [1000, 5000, 15000, 25000, 44949]  # valori da testare
K_VALUES    = [3, 5, 10, 15]
RANDOM_STATE = 42

EMBEDDING_MODEL = "allenai/scibert_scivocab_uncased"
LLM_MODEL       = "microsoft/Phi-3.5-mini-instruct"

GOLD_STANDARD = {
    "What is BERT and how does self-attention work?": [
        "bert", "attention", "transformer", "language model", "pre-training"
    ],
    "How does word2vec represent word meaning?": [
        "word2vec", "skip-gram", "word embedding", "word representation"
    ],
    "What are the main challenges in machine translation?": [
        "machine translation", "neural machine translation", "nmt"
    ],
    "How does topic modeling work?": [
        "topic model", "lda", "bertopic", "topic", "clustering"
    ],
    "What is named entity recognition?": [
        "named entity", "ner", "entity recognition", "sequence labeling"
    ],
    "How is sentiment analysis performed on text?": [
        "sentiment", "sentiment analysis", "opinion mining", "polarity"
    ],
    "What is dependency parsing in NLP?": [
        "dependency parsing", "syntactic parsing", "parse tree", "treebank"
    ],
}

# ============================================================
# STEP 1: Caricamento dataset completo (una volta sola)
# ============================================================
print("\n[STEP 1] Caricamento dataset arXiv NLP completo...")

dataset = load_dataset("MaartenGr/arxiv_nlp")
df_full = pd.DataFrame(dataset['train'])
print(f"Documenti totali disponibili: {len(df_full)}")

title_col    = next((c for c in df_full.columns if 'title'    in c.lower()), df_full.columns[0])
abstract_col = next((c for c in df_full.columns if 'abstract' in c.lower()
                     or 'summar' in c.lower()), df_full.columns[1])
year_col     = next((c for c in df_full.columns if 'year'     in c.lower()), None)


def build_corpus(df, n):
    """Campiona n documenti (riproducibile) e costruisce documenti/metadata."""
    df_s = df.sample(n=n, random_state=RANDOM_STATE).reset_index(drop=True)
    docs, meta = [], []
    for _, row in df_s.iterrows():
        title    = str(row[title_col])    if pd.notna(row[title_col])    else 'No Title'
        abstract = str(row[abstract_col]) if pd.notna(row[abstract_col]) else 'No Abstract'
        year     = str(row[year_col])     if year_col and pd.notna(row[year_col]) else 'Unknown'
        docs.append(f"Title: {title}\n\nAbstract: {abstract}")
        meta.append({'title': title, 'year': year})
    return docs, meta


# ============================================================
# STEP 2: Caricamento modello embedding (una volta sola)
# ============================================================
# Scelta: SciBERT (allenai/scibert_scivocab_uncased)
# Motivazione: pre-addestrato su 1.14M paper scientifici,
# vocabolario specializzato per il dominio — molto più adatto
# di MiniLM su un corpus di abstract NLP.
# ============================================================
print("\n[STEP 2] Caricamento SciBERT...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
print("SciBERT caricato.")


def build_faiss_index(documents):
    """Genera gli embeddings SciBERT e costruisce l'indice FAISS (IndexFlatIP)."""
    embeddings = embedding_model.encode(
        documents,
        show_progress_bar=True,
        batch_size=64,
        convert_to_numpy=True,
        normalize_embeddings=True   # obbligatorio per IndexFlatIP (cosine similarity)
    )
    idx = faiss.IndexFlatIP(embeddings.shape[1])  # 768 per SciBERT
    idx.add(embeddings.astype(np.float32))
    return idx


# ============================================================
# STEP 3: Retriever e pipeline RAG
# ============================================================
def retrieve(query, faiss_index, documents, metadata, k=5):
    """Recupera i k documenti più rilevanti per la query (FAISS + SciBERT)."""
    query_emb = embedding_model.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)
    similarities, indices = faiss_index.search(query_emb, k)
    return [
        {
            'rank':       i + 1,
            'similarity': float(sim),
            'document':   documents[idx],
            'metadata':   metadata[idx]
        }
        for i, (sim, idx) in enumerate(zip(similarities[0], indices[0]))
    ]


def rag_answer(query, results):
    """Costruisce il prompt dai documenti recuperati e genera la risposta con Phi-3.5-mini."""
    context_parts = [
        f"[Paper {r['rank']}] {r['metadata']['title']}\n{r['document']}"
        for r in results
    ]
    context = "\n\n".join(context_parts)

    # Limita contesto: teniamo il prompt ragionevole per velocità di generazione su CPU
    MAX_CONTEXT = 3000
    if len(context) > MAX_CONTEXT:
        context = context[:MAX_CONTEXT] + "\n[...truncated...]"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant specialized in NLP research. "
                "Answer questions based only on the provided research papers. "
                "Always cite the paper numbers [Paper X] you used in your answer. "
                "If the context does not contain enough information, say so clearly."
            )
        },
        {
            "role": "user",
            "content": (
                f"Context from research papers:\n\n{context}\n\n"
                f"Question: {query}\n\n"
                f"Answer based on the context above, citing paper numbers:"
            )
        }
    ]

    prompt    = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    output    = llm(prompt)
    full_text = output[0]['generated_text']
    return full_text[len(prompt):].strip() if full_text.startswith(prompt) else full_text


# ============================================================
# STEP 4: Caricamento LLM - Phi-3.5-mini-instruct (una volta sola)
# ============================================================
# Scelta: microsoft/Phi-3.5-mini-instruct (3.8B parametri), float16 su
# GPU / float32 su CPU. Temperatura bassa (0.3) per risposte deterministiche.
# ============================================================
print("\n[STEP 4] Caricamento LLM: Phi-3.5-mini-instruct...")
print("(prima volta scarica ~7.6GB, poi usa la cache)")

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
model = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    low_cpu_mem_usage=True
)
llm = pipeline(
    'text-generation',
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=300,
    do_sample=True,
    temperature=0.3,
    pad_token_id=tokenizer.eos_token_id,
    clean_up_tokenization_spaces=False
)
print(f"Modello caricato su {device}")


# ============================================================
# METRICHE DI VALUTAZIONE
# ============================================================
def precision_at_k(results, relevant_keywords):
    return sum(
        1 for r in results
        if any(kw in r['document'].lower() for kw in relevant_keywords)
    ) / len(results)


def context_relevance(query, results):
    qe   = embedding_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    snip = [r['document'][:200] for r in results]
    de   = embedding_model.encode(snip, convert_to_numpy=True, normalize_embeddings=True)
    return float(np.mean(de @ qe.T))


def answer_relevance(query, answer):
    embs = embedding_model.encode([query, answer], convert_to_numpy=True, normalize_embeddings=True)
    return float(embs[0] @ embs[1])


def faithfulness_proxy(answer, results):
    context_text  = ' '.join(r['document'][:500] for r in results).lower()
    words         = re.findall(r'\b[a-z]{4,}\b', answer.lower())
    content_words = [w for w in words if w not in STOPWORDS]
    if not content_words:
        return 0.0
    return sum(1 for w in content_words if w in context_text) / len(content_words)


# ============================================================
# ESPERIMENTO PRINCIPALE: variazione di N_DOCS e di k
# ============================================================
BERT_QUERY = "What is BERT and how does self-attention work?"
all_results = []  # un dict per ogni N_DOCS

for N_DOCS in N_DOCS_LIST:

    print(f"\n{'=' * 60}")
    print(f"  ESPERIMENTO  N_DOCS = {N_DOCS:,}")
    print('=' * 60)

    print(f"\n[1/3] Costruzione corpus ({N_DOCS:,} documenti)...")
    documents, metadata = build_corpus(df_full, N_DOCS)

    print("[2/3] Generazione embeddings e indice FAISS...")
    faiss_index = build_faiss_index(documents)
    print(f"Indice FAISS creato con {faiss_index.ntotal} vettori")

    print("[3/3] Confronto k su 7 query eterogenee...")
    k_summary = []
    for k in K_VALUES:
        p_list, cr_list, p_bert = [], [], None
        for query, keywords in GOLD_STANDARD.items():
            results = retrieve(query, faiss_index, documents, metadata, k=k)
            p = precision_at_k(results, keywords)
            p_list.append(p)
            cr_list.append(context_relevance(query, results))
            if query == BERT_QUERY:
                p_bert = p
        k_summary.append({
            'k': k,
            'precision': float(np.mean(p_list)),
            'context_relevance': float(np.mean(cr_list)),
            'precision_bert': p_bert,
        })

    print(f"\n  {'k':>4} {'Precision@k':>12} {'Context Rel.':>14} {'P@k (BERT)':>12}")
    print(f"  {'-' * 46}")
    for row in k_summary:
        print(f"  {row['k']:>4} {row['precision']:>12.3f} {row['context_relevance']:>14.3f} {row['precision_bert']:>12.3f}")

    best_k = max(k_summary, key=lambda r: r['precision'])['k']
    print(f"\n  k con Precision@k migliore: {best_k}")

    # Valutazione qualitativa con generazione: Answer Relevance e Faithfulness
    print(f"\n  Generazione risposte per valutazione qualitativa (k={best_k})...")
    ar_list, ff_list = [], []
    for query, keywords in GOLD_STANDARD.items():
        results = retrieve(query, faiss_index, documents, metadata, k=best_k)
        answer  = rag_answer(query, results)
        ar_list.append(answer_relevance(query, answer))
        ff_list.append(faithfulness_proxy(answer, results))

    all_results.append({
        'n_docs':       N_DOCS,
        'best_k':       best_k,
        'k_summary':    k_summary,
        'precision':    next(r['precision'] for r in k_summary if r['k'] == best_k),
        'precision_bert': next(r['precision_bert'] for r in k_summary if r['k'] == best_k),
        'answer_relevance': float(np.mean(ar_list)),
        'faithfulness':     float(np.mean(ff_list)),
    })

    print(f"  Answer Relevance media: {np.mean(ar_list):.3f}")
    print(f"  Faithfulness media:     {np.mean(ff_list):.3f}")

# ============================================================
# RIEPILOGO COMPARATIVO FINALE
# ============================================================
print(f"\n\n{'=' * 60}")
print("  RIEPILOGO COMPARATIVO — variazione di N_DOCS")
print('=' * 60)

print(f"\n  {'N_DOCS':<10} {'best_k':>7} {'P@k':>8} {'P@k (BERT)':>12} {'AnsRel':>8} {'Faith':>8}")
print(f"  {'-' * 56}")
for r in all_results:
    print(f"  {r['n_docs']:<10,} {r['best_k']:>7} {r['precision']:>8.3f} "
          f"{r['precision_bert']:>12.3f} {r['answer_relevance']:>8.3f} {r['faithfulness']:>8.3f}")

print("\n  Nota: 'P@k (BERT)' è la Precision@k sulla sola query "
      "\"What is BERT and how does self-attention work?\" al k migliore di "
      "ciascuna configurazione — utile per capire se il retrieval semantico "
      "puro continua a perdere questo paper specifico al variare della "
      "dimensione del corpus (limite già osservato e motivante l'approccio "
      "ibrido di lab5_hybrid.py).")
