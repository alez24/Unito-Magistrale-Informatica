import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ============================================================
# LAB 5 - Hybrid Search RAG (consegna)
# Tecnologie del Linguaggio Naturale - Prof. Di Caro - A.A. 2025/2026
#
# Pipeline RAG ibrida su paper NLP da arXiv: retrieval semantico
# (SciBERT + FAISS) e lessicale (BM25) fusi con Reciprocal Rank Fusion,
# generazione con Phi-3.5-mini-instruct e citazione delle fonti.
#
# L'analisi completa (variazione di N_DOCS e di k, robustezza alle
# parafrasi) e' nella relazione; questo script mostra la pipeline
# end-to-end e confronta live base vs ibrido su due query di esempio.
# ============================================================

import re
import sys
import torch
import faiss
import numpy as np
import pandas as pd
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from rank_bm25 import BM25Okapi

sys.stdout.reconfigure(encoding='utf-8')

try:
    from nltk.corpus import stopwords as nltk_sw
    STOPWORDS = set(nltk_sw.words('english'))
except LookupError:
    import nltk
    nltk.download('stopwords', quiet=True)
    STOPWORDS = set(nltk_sw.words('english'))

# ============================================================
# CONFIGURAZIONE
# ============================================================
N_DOCS          = 44949   # corpus completo (embeddings gia' in cache da lab5_hybrid.py)
RANDOM_STATE    = 42
PER_DOC_CHARS   = 800
EMBEDDING_MODEL = "allenai/scibert_scivocab_uncased"
LLM_MODEL       = "microsoft/Phi-3.5-mini-instruct"

# Due query di esempio per il confronto live base vs ibrido: la prima e'
# il caso critico dell'esperimento (il retrieval solo-semantico perde il
# paper su BERT su corpus grandi), la seconda il caso di vittoria netta
# dell'ibrido (termine tecnico esatto, "NER", che BM25 intercetta subito).
DEMO_QUERIES = {
    "What is BERT and how does self-attention work?": [
        "bert", "attention", "transformer", "language model", "pre-training"
    ],
    "What is named entity recognition?": [
        "named entity", "ner", "entity recognition", "sequence labeling"
    ],
}


def match_kw(text, keywords):
    """Match per parola (o frase) intera: 'kw in text' matcherebbe 'ner' in 'corner'."""
    text = text.lower()
    return any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in keywords)


def tok(text):
    return re.findall(r'\w+', text.lower())


# ============================================================
# STEP 1: dataset e corpus
# ============================================================
print("[1/5] Caricamento dataset arXiv-NLP...")
dataset = load_dataset("MaartenGr/arxiv_nlp")
df_full = pd.DataFrame(dataset['train'])

title_col    = next((c for c in df_full.columns if 'title' in c.lower()), df_full.columns[0])
abstract_col = next((c for c in df_full.columns if 'abstract' in c.lower() or 'summar' in c.lower()), df_full.columns[1])
year_col     = next((c for c in df_full.columns if 'year' in c.lower()), None)

# stesso shuffle/seed di lab5_hybrid.py: stesso corpus, cache degli embeddings condivisa
df_shuffled = df_full.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True).head(N_DOCS)

documents, metadata = [], []
for _, row in df_shuffled.iterrows():
    title    = str(row[title_col])    if pd.notna(row[title_col])    else 'No Title'
    abstract = str(row[abstract_col]) if pd.notna(row[abstract_col]) else 'No Abstract'
    year     = str(row[year_col])     if year_col and pd.notna(row[year_col]) else 'Unknown'
    documents.append(f"Title: {title}\n\nAbstract: {abstract}")
    metadata.append({'title': title, 'year': year})
print(f"      Corpus: {len(documents):,} documenti")

# ============================================================
# STEP 2: embeddings SciBERT (riusa la cache se presente) + FAISS + BM25
# ============================================================
print("[2/5] Embedding SciBERT e indici (FAISS + BM25)...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

model_tag = EMBEDDING_MODEL.split('/')[-1]
emb_cache_path = f"embeddings_{model_tag}_{N_DOCS}.npy"
emb_sig_path   = f"embeddings_{model_tag}_{N_DOCS}.meta.txt"
emb_signature  = f"{N_DOCS}|{RANDOM_STATE}|{EMBEDDING_MODEL}|{documents[0][:80]}|{documents[-1][:80]}"

if (os.path.exists(emb_cache_path) and os.path.exists(emb_sig_path)
        and open(emb_sig_path, encoding="utf-8").read() == emb_signature):
    embeddings = np.load(emb_cache_path)
else:
    embeddings = embedding_model.encode(
        documents, show_progress_bar=True, batch_size=64,
        convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)
    np.save(emb_cache_path, embeddings)
    with open(emb_sig_path, "w", encoding="utf-8") as f:
        f.write(emb_signature)

faiss_index = faiss.IndexFlatIP(embeddings.shape[1])
faiss_index.add(embeddings)

bm25_index = BM25Okapi([tok(doc) for doc in documents])
print(f"      Indici pronti su {len(documents):,} documenti")

# ============================================================
# STEP 3: LLM
# ============================================================
print("[3/5] Caricamento Phi-3.5-mini-instruct...")
device    = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
model     = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto", low_cpu_mem_usage=True
)
llm = pipeline(
    'text-generation', model=model, tokenizer=tokenizer,
    max_new_tokens=300, do_sample=False, return_full_text=False,
    pad_token_id=tokenizer.eos_token_id, clean_up_tokenization_spaces=False
)
print(f"      Modello caricato su {device}")


# ============================================================
# STEP 4: retrieval (semantico, lessicale, ibrido) e generazione
# ============================================================
def retrieve_semantic(query, k=10):
    qe = embedding_model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
    sims, idxs = faiss_index.search(qe, k)
    return [{'rank': i + 1, 'idx': int(ix), 'document': documents[ix], 'metadata': metadata[ix]}
            for i, ix in enumerate(idxs[0])]


def retrieve_bm25(query, k=10):
    scores = bm25_index.get_scores(tok(query))
    top = np.argsort(scores)[::-1][:k]
    return [{'rank': i + 1, 'idx': int(ix), 'document': documents[ix], 'metadata': metadata[ix]}
            for i, ix in enumerate(top)]


def reciprocal_rank_fusion(results_list, k=60):
    """RRF: somma 1/(k+rank) sulle liste da fondere; k=60 e' il valore standard in letteratura."""
    rrf_scores, doc_map = {}, {}
    for results in results_list:
        for item in results:
            ix = item['idx']
            rrf_scores[ix] = rrf_scores.get(ix, 0) + 1 / (k + item['rank'])
            doc_map[ix] = item
    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return [{'rank': i + 1, 'idx': ix, 'document': doc_map[ix]['document'], 'metadata': doc_map[ix]['metadata']}
            for i, (ix, _) in enumerate(ranked)]


def retrieve_hybrid(query, k=5):
    # pool piu' ampio (20) per ciascun retriever prima della fusione, per dare a RRF
    # abbastanza candidati da ricombinare
    sem = retrieve_semantic(query, k=20)
    bm  = retrieve_bm25(query, k=20)
    return reciprocal_rank_fusion([sem, bm])[:k]


def rag_answer(query, results):
    context = "\n\n".join(f"[Paper {r['rank']}]\n{r['document'][:PER_DOC_CHARS]}" for r in results)
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
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return llm(prompt)[0]['generated_text'].strip()


def print_with_sources(label, query, results, answer):
    print(f"\n--- {label} ---")
    print(f"ANSWER:\n{answer}")
    print("SOURCES:")
    for r in results:
        print(f"  [Paper {r['rank']}] {r['metadata']['title']} ({r['metadata']['year']})")


# ============================================================
# STEP 5: metriche (per il confronto numerico rapido nel demo)
# ============================================================
def precision_at_k(results, keywords, k=5):
    return sum(1 for r in results[:k] if match_kw(r['document'], keywords)) / k


def answer_relevance(query, answer):
    embs = embedding_model.encode([query, answer], convert_to_numpy=True, normalize_embeddings=True)
    return float(embs[0] @ embs[1])


def faithfulness_proxy(answer, results):
    # confronto per insieme di parole (non substring, altrimenti "that" matcherebbe
    # dentro "mathematical"); "paper" escluso perche' compare sempre nelle citazioni
    # a prescindere dal contenuto reale della risposta
    context_words = set(re.findall(r'\b[a-z]{4,}\b', ' '.join(r['document'][:PER_DOC_CHARS] for r in results).lower())) - {'paper'}
    content_words = [w for w in re.findall(r'\b[a-z]{4,}\b', answer.lower()) if w not in STOPWORDS and w != 'paper']
    if not content_words:
        return 0.0
    return sum(1 for w in content_words if w in context_words) / len(content_words)


# ============================================================
# DEMO: confronto base vs ibrido, con fonti citate, su due query reali
# ============================================================
print("[4/5] Confronto retrieval base (solo semantico) vs ibrido (semantico+BM25)...")
print("[5/5] Generazione risposte con citazione delle fonti...\n")

for query, keywords in DEMO_QUERIES.items():
    base_results   = retrieve_semantic(query, k=5)
    hybrid_results = retrieve_hybrid(query, k=5)

    ans_base   = rag_answer(query, base_results)
    ans_hybrid = rag_answer(query, hybrid_results)

    print("=" * 70)
    print(f"QUERY: {query}")
    print_with_sources("BASE (semantico)", query, base_results, ans_base)
    print_with_sources("IBRIDO (semantico + BM25, RRF)", query, hybrid_results, ans_hybrid)

    print(f"\nMetriche  {'':>10} {'Base':>8} {'Ibrido':>8}")
    print(f"  Precision@5      {precision_at_k(base_results, keywords):>8.3f} {precision_at_k(hybrid_results, keywords):>8.3f}")
    print(f"  Answer Relevance {answer_relevance(query, ans_base):>8.3f} {answer_relevance(query, ans_hybrid):>8.3f}")
    print(f"  Faithfulness     {faithfulness_proxy(ans_base, base_results):>8.3f} {faithfulness_proxy(ans_hybrid, hybrid_results):>8.3f}")
    print()
