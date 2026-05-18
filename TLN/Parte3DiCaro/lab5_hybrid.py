import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ============================================================
# PROGETTO ESTESO - Hybrid Search RAG
# Tecnologie del Linguaggio Naturale - Prof. Di Caro
# A.A. 2025/2026
#
# Estende il LAB-5 con:
#   - BM25 (retrieval lessicale) accanto a FAISS (semantico)
#   - Reciprocal Rank Fusion (RRF) per combinare i risultati
#   - Confronto quantitativo RAG base vs RAG ibrido
#   - Valutazione Precision@k
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
print("=" * 60)
print("PROGETTO ESTESO: Hybrid Search RAG - TLN 2025/2026")
print("=" * 60)
print(f"Device: {'CUDA (GPU)' if torch.cuda.is_available() else 'CPU'}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# ============================================================
# STEP 1: Ricarica dataset (stesso seed del LAB-5)
# ============================================================
print("\n[STEP 1] Caricamento dataset...")

N_DOCS    = 15000
INDEX_PATH = "arxiv_nlp_scibert_faiss.index"

dataset = load_dataset("MaartenGr/arxiv_nlp")
df = pd.DataFrame(dataset['train'])
df = df.sample(n=N_DOCS, random_state=42).reset_index(drop=True)

title_col    = next((c for c in df.columns if 'title'    in c.lower()), df.columns[0])
abstract_col = next((c for c in df.columns if 'abstract' in c.lower()
                     or 'summar' in c.lower()), df.columns[1])
year_col     = next((c for c in df.columns if 'year'     in c.lower()), None)

documents = []
metadata  = []
for _, row in df.iterrows():
    title    = str(row[title_col])    if pd.notna(row[title_col])    else 'No Title'
    abstract = str(row[abstract_col]) if pd.notna(row[abstract_col]) else 'No Abstract'
    year     = str(row[year_col])     if year_col and pd.notna(row[year_col]) else 'Unknown'
    documents.append(f"Title: {title}\n\nAbstract: {abstract}")
    metadata.append({'title': title, 'year': year})

print(f"Documenti caricati: {len(documents)}")

# ============================================================
# STEP 2: Carica modello embedding e indice FAISS
# ============================================================
print("\n[STEP 2] Caricamento SciBERT e indice FAISS...")

EMBEDDING_MODEL = "allenai/scibert_scivocab_uncased"
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# Ricarica indice salvato dal LAB-5 — niente ricalcolo
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    print(f"Indice FAISS caricato da disco ({index.ntotal} vettori)")
else:
    print("Indice non trovato, ricalcolo...")
    embeddings = embedding_model.encode(
        documents, show_progress_bar=True,
        batch_size=64, convert_to_numpy=True, normalize_embeddings=True
    )
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype(np.float32))
    faiss.write_index(index, INDEX_PATH)
    print(f"Indice creato e salvato ({index.ntotal} vettori)")

# ============================================================
# STEP 3: Costruzione indice BM25
# ============================================================
# BM25 lavora su token (parole esatte), non su vettori.
# Tokenizziamo ogni documento semplicemente con split().
# Motivazione: BM25 è complementare agli embeddings —
# cattura corrispondenze lessicali precise che SciBERT
# a volte manca (es. acronimi, nomi propri, termini tecnici).
# ============================================================
print("\n[STEP 3] Costruzione indice BM25...")

tokenized_docs = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)
print(f"Indice BM25 costruito su {len(tokenized_docs)} documenti")

# ============================================================
# STEP 4: Funzioni di retrieval
# ============================================================

def retrieve_semantic(query: str, k: int = 10) -> list:
    """Retrieval semantico con SciBERT + FAISS."""
    query_emb = embedding_model.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)
    similarities, indices = index.search(query_emb, k)
    return [
        {'rank': i+1, 'score': float(sim), 'idx': int(idx),
         'document': documents[idx], 'metadata': metadata[idx]}
        for i, (sim, idx) in enumerate(zip(similarities[0], indices[0]))
    ]


def retrieve_bm25(query: str, k: int = 10) -> list:
    """Retrieval lessicale con BM25."""
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:k]
    return [
        {'rank': i+1, 'score': float(scores[idx]), 'idx': int(idx),
         'document': documents[idx], 'metadata': metadata[idx]}
        for i, idx in enumerate(top_indices)
    ]


def reciprocal_rank_fusion(results_list: list, k: int = 60) -> list:
    """
    Reciprocal Rank Fusion: fonde più liste di risultati.

    Formula: RRF(d) = sum(1 / (k + rank(d)))
    k=60 è il valore standard della letteratura (Cormack et al., 2009).

    Motivazione: RRF è robusto rispetto alle differenze di scala
    tra i punteggi BM25 e cosine similarity — non serve normalizzare.
    """
    rrf_scores = {}
    doc_map    = {}

    for results in results_list:
        for item in results:
            idx = item['idx']
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + item['rank'])
            doc_map[idx]    = item

    # Ordina per score RRF decrescente
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    return [
        {'rank': i+1, 'rrf_score': score, 'idx': idx,
         'document': doc_map[idx]['document'], 'metadata': doc_map[idx]['metadata']}
        for i, (idx, score) in enumerate(sorted_docs)
    ]


def retrieve_hybrid(query: str, k: int = 5) -> list:
    """
    Hybrid retrieval: BM25 + SciBERT combinati con RRF.
    Recupera top-20 da ciascun metodo, poi fonde con RRF e restituisce top-k.
    """
    semantic_results = retrieve_semantic(query, k=20)
    bm25_results     = retrieve_bm25(query, k=20)
    fused            = reciprocal_rank_fusion([semantic_results, bm25_results])
    return fused[:k]


# ============================================================
# STEP 5: Caricamento LLM
# ============================================================
print("\n[STEP 5] Caricamento Phi-3.5-mini-instruct...")

LLM_MODEL = "microsoft/Phi-3.5-mini-instruct"
device    = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
model     = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    low_cpu_mem_usage=True
)
llm = pipeline(
    'text-generation', model=model, tokenizer=tokenizer,
    max_new_tokens=300, do_sample=True, temperature=0.3,
    pad_token_id=tokenizer.eos_token_id,
    clean_up_tokenization_spaces=False
)
print(f"Modello caricato su {device}")


# ============================================================
# STEP 6: Funzione RAG generica
# ============================================================
def rag_answer(query: str, results: list, label: str = "RAG") -> str:
    """Genera risposta RAG dato un set di risultati (base o ibrido)."""

    context_parts = [
        f"[Paper {r['rank']}] {r['metadata']['title']}\n{r['document']}"
        for r in results
    ]
    context = "\n\n".join(context_parts)
    if len(context) > 3000:
        context = context[:3000] + "\n[...truncated...]"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant specialized in NLP research. "
                "Answer questions based only on the provided research papers. "
                "Always cite the paper numbers [Paper X] you used. "
                "If the context is insufficient, say so clearly."
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

    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    output    = llm(prompt)
    full_text = output[0]['generated_text']
    return full_text[len(prompt):].strip() \
           if full_text.startswith(prompt) else full_text


# ============================================================
# STEP 7: Confronto RAG base vs RAG ibrido
# ============================================================
def compare(query: str, k: int = 5):
    """
    Confronta il RAG base (solo semantico) con il RAG ibrido (BM25 + semantico).
    Mostra i documenti recuperati da ciascun metodo e le risposte generate.
    """
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print('='*60)

    # Retrieval
    base_results   = retrieve_semantic(query, k=k)
    hybrid_results = retrieve_hybrid(query, k=k)

    # Mostra documenti recuperati
    print(f"\n--- RAG BASE (solo SciBERT) ---")
    for r in base_results:
        print(f"  [{r['rank']}] {r['metadata']['title'][:65]} (sim={r['score']:.3f})")

    print(f"\n--- RAG IBRIDO (BM25 + SciBERT) ---")
    for r in hybrid_results:
        print(f"  [{r['rank']}] {r['metadata']['title'][:65]} (rrf={r['rrf_score']:.4f})")

    # Documenti in comune
    base_titles   = {r['metadata']['title'] for r in base_results}
    hybrid_titles = {r['metadata']['title'] for r in hybrid_results}
    overlap       = base_titles & hybrid_titles
    print(f"\nDocumenti in comune: {len(overlap)}/{k}")
    print(f"Documenti unici nel base:   {len(base_titles - hybrid_titles)}")
    print(f"Documenti unici nell'ibrido: {len(hybrid_titles - base_titles)}")

    # Generazione risposte
    print(f"\n--- RISPOSTA RAG BASE ---")
    answer_base = rag_answer(query, base_results, "BASE")
    print(answer_base)

    print(f"\n--- RISPOSTA RAG IBRIDO ---")
    answer_hybrid = rag_answer(query, hybrid_results, "IBRIDO")
    print(answer_hybrid)

    # Fonti
    print(f"\n--- FONTI BASE ---")
    for r in base_results:
        print(f"  [{r['rank']}] {r['metadata']['title']} ({r['metadata']['year']})")

    print(f"\n--- FONTI IBRIDO ---")
    for r in hybrid_results:
        print(f"  [{r['rank']}] {r['metadata']['title']} ({r['metadata']['year']})")

    return base_results, hybrid_results


# ============================================================
# STEP 8: Valutazione Precision@k
# ============================================================
# Gold standard manuale: per ogni query indichiamo le parole
# chiave che un documento rilevante dovrebbe contenere nel titolo.
# È una valutazione approssimativa ma sufficiente per confrontare
# i due metodi in modo quantitativo.
# ============================================================

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


def precision_at_k(results: list, relevant_keywords: list, k: int = 5) -> float:
    """
    Calcola Precision@k usando keyword matching sul titolo del documento.
    Un documento è considerato rilevante se il suo titolo contiene
    almeno una delle keyword rilevanti.
    """
    relevant_count = 0
    for r in results[:k]:
        title_lower = r['metadata']['title'].lower()
        if any(kw in title_lower for kw in relevant_keywords):
            relevant_count += 1
    return relevant_count / k


def evaluate():
    """
    Valuta Precision@k per RAG base e RAG ibrido su tutte le query del gold standard.
    """
    print(f"\n{'='*60}")
    print("VALUTAZIONE PRECISION@K")
    print('='*60)
    print(f"{'Query':<45} {'P@5 Base':>10} {'P@5 Ibrido':>12} {'Migliore':>10}")
    print("-" * 80)

    base_scores   = []
    hybrid_scores = []

    for query, keywords in GOLD_STANDARD.items():
        base_results   = retrieve_semantic(query, k=5)
        hybrid_results = retrieve_hybrid(query, k=5)

        p_base   = precision_at_k(base_results,   keywords, k=5)
        p_hybrid = precision_at_k(hybrid_results, keywords, k=5)

        base_scores.append(p_base)
        hybrid_scores.append(p_hybrid)

        winner = "IBRIDO" if p_hybrid > p_base else ("BASE" if p_base > p_hybrid else "PARI")
        print(f"{query[:44]:<45} {p_base:>10.2f} {p_hybrid:>12.2f} {winner:>10}")

    avg_base   = np.mean(base_scores)
    avg_hybrid = np.mean(hybrid_scores)

    print("-" * 80)
    print(f"{'MEDIA':<45} {avg_base:>10.2f} {avg_hybrid:>12.2f}")
    print(f"\nConclusion: {'RAG IBRIDO migliore' if avg_hybrid > avg_base else 'RAG BASE migliore' if avg_base > avg_hybrid else 'PARI'}")
    print(f"Miglioramento ibrido vs base: {((avg_hybrid - avg_base) / max(avg_base, 0.001)) * 100:+.1f}%")

    return avg_base, avg_hybrid


# ============================================================
# DEMO
# ============================================================
print("\n\n[DEMO] Confronto RAG base vs ibrido...\n")

# Query di confronto
test_queries = [
    "What is BERT and how does self-attention work?",
    "How does word2vec represent word meaning?",
    "What are the main challenges in machine translation?"
]

for q in test_queries:
    compare(q, k=5)
    print()

# Valutazione quantitativa
evaluate()