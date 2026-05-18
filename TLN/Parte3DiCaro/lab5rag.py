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
#   - Dataset:   MaartenGr/arxiv_nlp (15.000 documenti, campione casuale)
#   - Embedding: SciBERT (allenai/scibert_scivocab_uncased)
#   - FAISS:     IndexFlatIP (ricerca esatta, CPU)
#   - k:         5 documenti per query
#   - LLM:       microsoft/Phi-3.5-mini-instruct
#   - Temp:      0.3
# ============================================================

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

# ============================================================
# STEP 1: Caricamento e preprocessing dei dati
# ============================================================
print("\n[STEP 1] Caricamento dataset arXiv NLP...")

INDEX_PATH = "arxiv_nlp_scibert_faiss.index"
DOCS_PATH  = "arxiv_nlp_documents.npy"
META_PATH  = "arxiv_nlp_metadata.npy"
N_DOCS     = 15000

dataset = load_dataset("MaartenGr/arxiv_nlp")
df = pd.DataFrame(dataset['train'])

# Campione casuale riproducibile — più rappresentativo di head()
# Motivazione: head() prende sempre i paper più vecchi/recenti,
# sample() garantisce varietà tematica nel corpus
df = df.sample(n=N_DOCS, random_state=42).reset_index(drop=True)
print(f"Documenti caricati: {len(df)}")

# Auto-rileva colonne
title_col    = next((c for c in df.columns if 'title'    in c.lower()), df.columns[0])
abstract_col = next((c for c in df.columns if 'abstract' in c.lower()
                     or 'summar' in c.lower()), df.columns[1])

documents = []
metadata  = []

for _, row in df.iterrows():
    title    = str(row[title_col])    if pd.notna(row[title_col])    else 'No Title'
    abstract = str(row[abstract_col]) if pd.notna(row[abstract_col]) else 'No Abstract'
    documents.append(f"Title: {title}\n\nAbstract: {abstract}")
    metadata.append({'title': title, 'year': str(row.get('year', 'Unknown'))})

print(f"Documenti preparati: {len(documents)}")

# ============================================================
# STEP 2: Generazione embeddings con SciBERT
# ============================================================
# Scelta: SciBERT (allenai/scibert_scivocab_uncased)
# Motivazione: pre-addestrato su 1.14M paper scientifici,
# vocabolario specializzato per il dominio — molto più adatto
# di MiniLM su un corpus di abstract NLP.
# SciBERT usa 768 dimensioni vs 384 di MiniLM: rappresentazioni
# più ricche a costo di più memoria e tempo.
# ============================================================
print("\n[STEP 2] Generazione embeddings con SciBERT...")
print("(prima volta ~5 minuti, poi usa la cache)")

EMBEDDING_MODEL = "allenai/scibert_scivocab_uncased"
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

embeddings = embedding_model.encode(
    documents,
    show_progress_bar=True,
    batch_size=64,
    convert_to_numpy=True,
    normalize_embeddings=True   # obbligatorio per IndexFlatIP (cosine similarity)
)
print(f"Embeddings generati: shape {embeddings.shape}")

# ============================================================
# STEP 3: Creazione vector store FAISS
# ============================================================
# Scelta: IndexFlatIP (Inner Product su vettori normalizzati = cosine similarity)
# Motivazione: con 15.000 documenti la ricerca esatta è velocissima
# (~ms per query). Indici approssimati come IVFFlat o HNSW
# introdurrebbero rumore senza reale guadagno a questa scala.
# Su Windows faiss-gpu non è disponibile via pip, usiamo CPU.
# ============================================================
print("\n[STEP 3] Creazione indice FAISS...")

dimension = embeddings.shape[1]  # 768 per SciBERT
index = faiss.IndexFlatIP(dimension)
index.add(embeddings.astype(np.float32))
print(f"Indice FAISS creato con {index.ntotal} vettori")

faiss.write_index(index, INDEX_PATH)
print(f"Indice salvato: {INDEX_PATH}")

# ============================================================
# STEP 4: Retriever
# ============================================================
def retrieve(query: str, k: int = 5) -> list:
    """
    Recupera i k documenti più rilevanti per la query.

    Scelta k=5: buon compromesso tra contesto ricco
    e lunghezza del prompt per il modello generativo.
    Aumentare k (es. k=10) migliora il recall ma
    rischia di superare la context window del LLM.
    """
    query_emb = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)

    similarities, indices = index.search(query_emb, k)

    return [
        {
            'rank':       i + 1,
            'similarity': float(sim),
            'document':   documents[idx],
            'metadata':   metadata[idx]
        }
        for i, (sim, idx) in enumerate(zip(similarities[0], indices[0]))
    ]


# Test retriever
print("\n[STEP 4] Test retriever...")
test_query = "What are transformer models and how does attention work?"
results = retrieve(test_query, k=5)
print(f"\nQuery: {test_query}\n")
for r in results:
    print(f"  [{r['rank']}] sim={r['similarity']:.3f} | {r['metadata']['title'][:70]}")

# ============================================================
# STEP 5: Caricamento LLM - Phi-3.5-mini-instruct
# ============================================================
# Scelta: microsoft/Phi-3.5-mini-instruct (3.8B parametri)
# Motivazione: con 16GB VRAM (RTX 5070) possiamo permetterci
# un modello di qualità superiore rispetto a Qwen 0.5B.
# Phi-3.5-mini è tra i migliori modelli small open-source
# per ragionamento e comprensione testuale.
# Carichiamo in float16 per dimezzare l'uso di VRAM.
#
# Alternativa Qwen2.5-0.5B:
#   PRO: 500MB, gira su qualsiasi hardware
#   CONTRO: qualità risposte nettamente inferiore
# ============================================================
print("\n[STEP 5] Caricamento LLM: Phi-3.5-mini-instruct...")
print("(prima volta scarica ~7.6GB, poi usa la cache)")

LLM_MODEL = "microsoft/Phi-3.5-mini-instruct"
device    = "cuda" if torch.cuda.is_available() else "cpu"

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
    temperature=0.3,        # bassa: risposte precise e deterministiche
    pad_token_id=tokenizer.eos_token_id,
    clean_up_tokenization_spaces=False
)

print(f"Modello caricato su {device}")

# ============================================================
# STEP 6: Pipeline RAG completa
# ============================================================
def rag_answer(query: str, k: int = 5) -> str:
    """
    Pipeline RAG completa: retrieval + costruzione contesto + generazione.

    1. Recupera i k paper più rilevanti (SciBERT + FAISS)
    2. Costruisce il prompt con titoli e abstract come contesto
    3. Genera la risposta con Phi-3.5-mini citando le fonti
    """
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print('='*60)

    # 1. Retrieval
    results = retrieve(query, k=k)
    print(f"\nDocumenti recuperati (top {k}):")
    for r in results:
        print(f"  [{r['rank']}] {r['metadata']['title'][:65]} (sim={r['similarity']:.3f})")

    # 2. Costruzione contesto
    context_parts = [
        f"[Paper {r['rank']}] {r['metadata']['title']}\n{r['document']}"
        for r in results
    ]
    context = "\n\n".join(context_parts)

    # Limita contesto: Phi-3.5-mini ha context window di 128K token
    # ma teniamo il prompt ragionevole per velocità di generazione
    MAX_CONTEXT = 3000
    if len(context) > MAX_CONTEXT:
        context = context[:MAX_CONTEXT] + "\n[...truncated...]"

    # 3. Prompt
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

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # 4. Generazione
    print("\nGenerazione risposta...")
    output    = llm(prompt)
    full_text = output[0]['generated_text']
    answer    = full_text[len(prompt):].strip() \
                if full_text.startswith(prompt) else full_text

    # 5. Output
    print(f"\n{'='*60}")
    print("RISPOSTA:")
    print('='*60)
    print(answer)
    print(f"\n{'='*60}")
    print("FONTI:")
    print('='*60)
    for r in results:
        print(f"  [{r['rank']}] {r['metadata']['title']} ({r['metadata']['year']})")

    return answer


# ============================================================
# DEMO
# ============================================================
print("\n\n[DEMO] Query di esempio...\n")

queries = [
    "What is BERT and how does self-attention work?",
    "How does word2vec represent word meaning?",
    "What are the main challenges in machine translation?"
]

for q in queries:
    rag_answer(q, k=5)
    print()