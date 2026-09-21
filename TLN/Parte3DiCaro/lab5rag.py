# -*- coding: utf-8 -*-
# ============================================================
# VERSIONE COMMENTATA DI lab5rag.py
# Il codice è identico all'originale: sono stati aggiunti solo commenti
# esplicativi (in italiano) per capire cosa fa ogni blocco e perché.
# ============================================================

# ------------------------------------------------------------
# Variabili d'ambiente: vanno impostate PRIMA di importare torch/faiss/tokenizers,
# altrimenti non hanno effetto.
# ------------------------------------------------------------
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"           # evita il crash "OpenMP runtime already initialized"
                                                       # quando FAISS e PyTorch caricano ciascuno la propria copia di libiomp
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"   # silenzia un avviso di Hugging Face su Windows (symlink nella cache)
os.environ["TOKENIZERS_PARALLELISM"] = "false"        # evita avvisi/deadlock dei tokenizer quando il processo fa fork

# ============================================================
# LAB-5: Sistema RAG su articoli scientifici NLP
# Tecnologie del Linguaggio Naturale - Prof. Di Caro
# A.A. 2025/2026
#
# Configurazione scelta:
#   - Dataset:   MaartenGr/arxiv_nlp (campione casuale, dimensione variabile)
#   - Embedding: confronto fra due modelli (vedi STEP 2)
#   - FAISS:     IndexFlatIP (ricerca esatta, CPU)
#   - LLM:       microsoft/Phi-3.5-mini-instruct
#   - Decoding:  greedy (do_sample=False) per risposte riproducibili
#
# Esperimento (risposta alle domande del Prof. Di Caro):
#   per ogni modello di embedding e ogni N_DOCS in N_DOCS_LIST si
#   confrontano diversi valori di k su 7 query eterogenee, misurando
#   Precision@k, Context Relevance, Answer Relevance e Faithfulness
#   proxy. Questo permette di vedere se la qualita' del retrieval
#   semantico puro (senza BM25/hybrid) cambia con la dimensione del
#   corpus e con il modello di embedding, oltre che con k.
#
#   Il confronto fra k sulla base della sola Precision@k tende a
#   premiare k piccoli e non dice nulla sulla qualita' della
#   generazione: per un solo N_DOCS (il piu' piccolo, DETAIL_N_DOCS,
#   per contenere i tempi di generazione su CPU) si generano le
#   risposte a OGNI valore di k, non solo al k con Precision@k
#   migliore, cosi' da poter confrontare anche Answer Relevance e
#   Faithfulness al variare di k.
#
#   I corpus a N_DOCS diversi sono sovrainsiemi annidati gli uni
#   degli altri (si mischia il dataset una sola volta e si
#   prendono i primi N_DOCS): cosi' l'effetto di N_DOCS e' isolato
#   dal caso di un documento che compare in un campione e non
#   nell'altro per pura variazione del campionamento casuale.
# ============================================================

import re                                   # espressioni regolari (match parola intera, tokenizzazione semplice)
import torch                                # backend dei modelli; qui serve anche per sapere se c'è la GPU
import faiss                                # libreria di Facebook per la ricerca di vicini più prossimi su vettori
import numpy as np                          # array numerici (embeddings, medie)
import pandas as pd                         # DataFrame per il dataset e per salvare i CSV dei risultati
from datasets import load_dataset           # scarica/carica dataset da Hugging Face
from sentence_transformers import SentenceTransformer   # modelli che trasformano testi in vettori (embeddings)
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline   # per l'LLM generativo (Phi-3.5)

# ------------------------------------------------------------
# Informazioni sull'hardware: la GPU cambia di molto i tempi (specie per l'LLM)
# ------------------------------------------------------------
print("=" * 60)
print("LAB-5: Sistema RAG - TLN 2025/2026")
print("=" * 60)
print(f"Device: {'CUDA (GPU)' if torch.cuda.is_available() else 'CPU'}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# ------------------------------------------------------------
# Stopword inglesi (parole funzionali come "the", "with", "that").
# Servono solo a faithfulness_proxy, per non contare parole prive di contenuto.
# Strategia a due livelli: prova a leggerle; se il dizionario NLTK non è scaricato
# (LookupError) lo scarica e riprova; se ancora fallisce, va avanti con un insieme
# vuoto e avvisa che la metrica sarà meno significativa.
# ------------------------------------------------------------
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

# ============================================================
# CONFIGURAZIONE ESPERIMENTO
# Qui si decide cosa variare: dimensione del corpus, numero di documenti
# recuperati (k), modello di embedding.
# ============================================================
N_DOCS_LIST = [1000, 5000, 15000, 25000]  # valori da testare; il dataset completo
                                           # viene aggiunto sotto dopo il caricamento
K_VALUES    = [3, 5, 10, 15]                # quanti documenti dare al retriever/LLM (il "k" del top-k)
RANDOM_STATE = 42                           # seed dello shuffle: rende gli esperimenti riproducibili
PER_DOC_CHARS = 800  # troncamento per singolo paper nel contesto (non sul blocco intero:
                      # cosi' tutti i k paper entrano nel prompt anche per k grandi)

# Due famiglie di embedding a confronto:
#   - SciBERT: vocabolario specializzato per il dominio scientifico, ma il
#     checkpoint di base NON e' fine-tuned per sentence similarity (SentenceTransformer
#     aggiunge solo un mean pooling): le similarita' coseno tendono quindi a essere
#     compresse verso l'alto e poco informative.
#   - all-mpnet-base-v2: general-purpose ma esplicitamente fine-tuned per
#     similarity/retrieval. Il confronto serve a capire quanto delle differenze
#     osservate (es. Context/Answer Relevance, o il retrieval che perde il paper
#     BERT) dipende dal modello scelto piuttosto che da un limite del retrieval
#     semantico puro in se'.
EMBEDDING_MODELS = [
    "allenai/scibert_scivocab_uncased",
    "sentence-transformers/all-mpnet-base-v2",
]
LLM_MODEL = "microsoft/Phi-3.5-mini-instruct"   # modello generativo che scrive le risposte

# ------------------------------------------------------------
# GOLD STANDARD: le 7 domande di test, ciascuna con una lista di parole chiave.
# Un documento recuperato è considerato "rilevante" se contiene almeno una
# delle keyword della sua query. È una definizione di rilevanza LESSICALE e
# approssimata (non c'è un giudizio umano): va tenuta presente nell'interpretazione.
# ------------------------------------------------------------
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


def match_kw(text, keywords):
    """Match per parola intera (o frase intera per keyword multi-parola): un semplice
    'kw in text' farebbe matchare 'ner' con 'corner' o 'bert' con 'roberta'."""
    text = text.lower()   # confronto case-insensitive
    # \b = confine di parola nella regex; re.escape neutralizza eventuali caratteri speciali
    # (es. il trattino in "pre-training", "skip-gram"). any() = basta una keyword che matchi.
    return any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in keywords)


# ============================================================
# STEP 1: Caricamento dataset completo (una volta sola)
# ============================================================
print("\n[STEP 1] Caricamento dataset arXiv NLP completo...")

dataset = load_dataset("MaartenGr/arxiv_nlp")   # scarica da Hugging Face (poi usa la cache locale)
df_full = pd.DataFrame(dataset['train'])         # trasforma lo split 'train' in DataFrame pandas
print(f"Documenti totali disponibili: {len(df_full)}")

# Aggiunge alla lista degli esperimenti anche il corpus completo (44.949 doc).
if len(df_full) not in N_DOCS_LIST:
    N_DOCS_LIST.append(len(df_full))

# Auto-rilevamento delle colonne per nome: rende lo script robusto a piccole
# differenze fra versioni del dataset. Se non trova nulla, ripiega sulla prima/seconda colonna.
title_col    = next((c for c in df_full.columns if 'title'    in c.lower()), df_full.columns[0])
abstract_col = next((c for c in df_full.columns if 'abstract' in c.lower()
                     or 'summar' in c.lower()), df_full.columns[1])
year_col     = next((c for c in df_full.columns if 'year'     in c.lower()), None)   # l'anno può non esserci

# mischiato una sola volta: ogni N_DOCS prende i primi N di questo stesso ordine,
# quindi i corpus di dimensioni diverse sono sovrainsiemi annidati l'uno dell'altro
# (frac=1 = tutte le righe in ordine casuale; reset_index rinumera da 0)
df_shuffled = df_full.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
MAX_N_DOCS = max(N_DOCS_LIST)   # dimensione del corpus più grande (= tutto il dataset)

# N_DOCS scelto per il confronto dettagliato "Answer Relevance/Faithfulness per ogni k"
# (il piu' piccolo, per limitare il numero di generazioni extra su CPU)
DETAIL_N_DOCS = min(N_DOCS_LIST)


def build_corpus(df, n):
    """Prende i primi n documenti di un dataframe già mischiato una volta sola."""
    df_s = df.head(n).reset_index(drop=True)
    docs, meta = [], []   # docs = testi da indicizzare; meta = info da citare nelle fonti
    for _, row in df_s.iterrows():
        # pd.notna evita di scrivere "nan" quando un campo è mancante
        title    = str(row[title_col])    if pd.notna(row[title_col])    else 'No Title'
        abstract = str(row[abstract_col]) if pd.notna(row[abstract_col]) else 'No Abstract'
        year     = str(row[year_col])     if year_col and pd.notna(row[year_col]) else 'Unknown'
        # Il "documento" è titolo + abstract insieme: sono semanticamente coesi
        docs.append(f"Title: {title}\n\nAbstract: {abstract}")
        meta.append({'title': title, 'year': year})
    return docs, meta


print(f"\n[STEP 1b] Costruzione corpus completo ({MAX_N_DOCS:,} documenti, "
      "indipendente dal modello di embedding)...")
all_documents, all_metadata = build_corpus(df_shuffled, MAX_N_DOCS)   # corpus completo, calcolato una volta


def build_faiss_index(embeddings):
    """Costruisce l'indice FAISS (IndexFlatIP) da embeddings già calcolati."""
    # IndexFlatIP = ricerca ESATTA (nessuna approssimazione) per prodotto scalare (Inner Product).
    # Poiché gli embedding sono normalizzati (norma 1), prodotto scalare == similarità coseno.
    idx = faiss.IndexFlatIP(embeddings.shape[1])   # shape[1] = dimensione dei vettori (768 per SciBERT/mpnet)
    idx.add(embeddings.astype(np.float32))          # FAISS richiede float32
    return idx


# ============================================================
# STEP 2: Caricamento LLM - Phi-3.5-mini-instruct (una volta sola,
# condiviso fra tutti i modelli di embedding confrontati)
# ============================================================
# Scelta: microsoft/Phi-3.5-mini-instruct (3.8B parametri), float16 su
# GPU / float32 su CPU. Decoding greedy per risposte riproducibili.
# Nota: su CPU, float32 occupa circa 15 GB di RAM e ogni generazione da
# fino a 300 token e' lenta - con 2 modelli di embedding x N_DOCS x query
# il numero di generazioni cresce di conseguenza (vedi DETAIL_N_DOCS sopra).
# ============================================================
print("\n[STEP 2] Caricamento LLM: Phi-3.5-mini-instruct...")
print("(prima volta scarica ~7.6GB, poi usa la cache)")

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)   # converte testo <-> token per l'LLM
model = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,   # float16 dimezza la memoria ma su CPU non conviene
    device_map="auto",          # lascia a accelerate la scelta di dove mettere i pesi (GPU se c'è)
    low_cpu_mem_usage=True      # carica i pesi a pezzi per non raddoppiare l'uso di RAM
)
# pipeline = wrapper comodo che unisce tokenizer + modello + generazione
llm = pipeline(
    'text-generation',
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=300,       # lunghezza massima della risposta (le più lunghe vengono troncate)
    do_sample=False,          # greedy: riproducibile fra run, necessario per confrontare le metriche
    return_full_text=False,   # restituisce solo il testo generato, non prompt+testo
    pad_token_id=tokenizer.eos_token_id,    # evita un warning: il modello non ha un token di padding dedicato
    clean_up_tokenization_spaces=False      # non "aggiusta" gli spazi nell'output
)
print(f"Modello caricato su {device}")


# ============================================================
# STEP 3: Retriever e pipeline RAG
# ============================================================
def retrieve(query, faiss_index, documents, metadata, k=5):
    """Recupera i k documenti più rilevanti per la query (FAISS + embedding_model corrente)."""
    # 1) trasforma la query nello stesso spazio vettoriale dei documenti (stesso modello!)
    #    NB: usa la variabile GLOBALE embedding_model, che il ciclo principale cambia a ogni modello
    query_emb = embedding_model.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)
    # 2) FAISS restituisce, per la query, le k similarità più alte e i relativi indici nel corpus
    similarities, indices = faiss_index.search(query_emb, k)
    # 3) [0] perché abbiamo passato una sola query; rank parte da 1 (1 = più simile)
    return [
        {
            'rank':       i + 1,
            'similarity': float(sim),
            'document':   documents[idx],    # testo completo (titolo + abstract)
            'metadata':   metadata[idx]      # titolo e anno, per citare la fonte
        }
        for i, (sim, idx) in enumerate(zip(similarities[0], indices[0]))
    ]


def rag_answer(query, results):
    """Costruisce il prompt dai documenti recuperati e genera la risposta con Phi-3.5-mini."""
    # niente titolo anteposto: r['document'] inizia gia' con "Title: ...", altrimenti
    # il titolo comparirebbe due volte nel prompt
    # Ogni paper è etichettato [Paper N] così il modello può citarlo; il testo è troncato
    # a PER_DOC_CHARS caratteri per tenere il prompt entro dimensioni gestibili.
    context_parts = [
        f"[Paper {r['rank']}]\n{r['document'][:PER_DOC_CHARS]}"
        for r in results
    ]
    context = "\n\n".join(context_parts)

    # Formato "chat": un messaggio di sistema (ruolo e regole) e uno dell'utente (contesto + domanda).
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant specialized in NLP research. "
                "Answer questions based only on the provided research papers. "     # vincola al contesto (riduce le allucinazioni)
                "Always cite the paper numbers [Paper X] you used in your answer. " # richiede le citazioni
                "If the context does not contain enough information, say so clearly."  # permette di dire "non lo so"
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

    # apply_chat_template trasforma i messaggi nel formato di token speciali atteso da Phi-3.5;
    # add_generation_prompt=True aggiunge l'intestazione del turno dell'assistente, da cui il modello continua.
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    output = llm(prompt)
    return output[0]['generated_text'].strip()   # con return_full_text=False è solo la risposta


# ============================================================
# METRICHE DI VALUTAZIONE
# ============================================================
def precision_at_k(results, relevant_keywords):
    # Frazione dei documenti recuperati che contengono almeno una keyword (rilevanza lessicale).
    # Es.: 2 rilevanti su 5 recuperati -> 0.4. Il denominatore è len(results), cioè k.
    return sum(
        1 for r in results if match_kw(r['document'], relevant_keywords)
    ) / len(results)


def context_relevance(query, results):
    # Similarità coseno media fra la query e l'INIZIO (200 caratteri) di ogni documento recuperato.
    # ATTENZIONE: usa embedding_model, cioè lo stesso modello che ha fatto il retrieval, quindi
    # i valori di SciBERT e mpnet non sono direttamente confrontabili fra loro.
    qe   = embedding_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    snip = [r['document'][:200] for r in results]
    de   = embedding_model.encode(snip, convert_to_numpy=True, normalize_embeddings=True)
    return float(np.mean(de @ qe.T))   # de @ qe.T 37cvmh y        = coseno di ogni documento con la query


def answer_relevance(query, answer):
    # Similarità coseno fra domanda e risposta generata: quanto la risposta è "in tema".
    # Stessa avvertenza: dipende dal modello di embedding corrente.
    embs = embedding_model.encode([query, answer], convert_to_numpy=True, normalize_embeddings=True)
    return float(embs[0] @ embs[1])


def faithfulness_proxy(answer, results):
    # stessa finestra per-documento usata in rag_answer, altrimenti la faithfulness
    # risulterebbe sottostimata per costruzione (risposta generata da più contesto
    # di quanto la metrica vada poi a verificare).
    # Confronto per insieme di parole (non substring: "that" altrimenti matcherebbe
    # dentro "mathematical"). "paper" è escluso perché compare sempre sia nel
    # contesto (intestazioni "[Paper N]") sia nelle citazioni della risposta,
    # quindi conterebbe come parola supportata a prescindere dal contenuto.
    # In sintesi: quale frazione delle parole "di contenuto" della risposta compare nel contesto?
    # È un proxy LESSICALE: non verifica se l'affermazione è vera, solo se usa parole del contesto.
    context_text  = ' '.join(r['document'][:PER_DOC_CHARS] for r in results).lower()
    context_words = set(re.findall(r'\b[a-z]{4,}\b', context_text)) - {'paper'}   # parole di >=4 lettere nel contesto
    words         = re.findall(r'\b[a-z]{4,}\b', answer.lower())                  # idem nella risposta
    content_words = [w for w in words if w not in STOPWORDS and w != 'paper']     # via stopword e "paper"
    if not content_words:
        return 0.0   # risposta vuota o senza parole utili: evita la divisione per zero
    return sum(1 for w in content_words if w in context_words) / len(content_words)


# ============================================================
# ESPERIMENTO PRINCIPALE: variazione di modello di embedding, N_DOCS e k
# ============================================================
BERT_QUERY = "What is BERT and how does self-attention work?"   # query "difficile": il retrieval semantico tende a sbagliarla
all_results    = []  # un dict per ogni (embedding_model, N_DOCS)
qa_rows        = []  # query/risposta generata, per esempi qualitativi nel report
k_detail_rows  = []  # precision/context relevance per ogni (embedding_model, n_docs, k)
k_gen_rows     = []  # answer relevance/faithfulness per ogni k, solo a DETAIL_N_DOCS

# --- CICLO ESTERNO: un giro per ogni modello di embedding ---
for EMBEDDING_MODEL in EMBEDDING_MODELS:

    print(f"\n{'#' * 60}")
    print(f"  MODELLO DI EMBEDDING: {EMBEDDING_MODEL}")
    print(f"{'#' * 60}")

    # Variabile globale usata da retrieve(), context_relevance() e answer_relevance()
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    print("Modello di embedding caricato.")

    # cache su disco per modello: la firma include EMBEDDING_MODEL e si invalida da
    # sola se cambia modello/corpus, ma il *nome del file* include gia' un tag del
    # modello cosi' due modelli diversi non si sovrascrivono a vicenda la cache a ogni
    # run (lab5_hybrid.py usa la stessa convenzione per SciBERT e puo' condividerla).
    # Codificare 44.949 abstract su CPU richiede decine di minuti: la cache evita di rifarlo.
    model_tag = EMBEDDING_MODEL.split('/')[-1]      # es. "scibert_scivocab_uncased"
    EMB_CACHE_PATH = f"embeddings_{model_tag}_{MAX_N_DOCS}.npy"          # i vettori
    EMB_CACHE_META_PATH = f"embeddings_{model_tag}_{MAX_N_DOCS}.meta.txt" # la "firma" del corpus
    # Firma: dimensione|seed|modello|primo e ultimo documento. Se qualcosa cambia (altro
    # seed, altro dataset, altro modello) la firma non coincide e la cache viene scartata.
    emb_signature = f"{MAX_N_DOCS}|{RANDOM_STATE}|{EMBEDDING_MODEL}|{all_documents[0][:80]}|{all_documents[-1][:80]}"

    if (os.path.exists(EMB_CACHE_PATH) and os.path.exists(EMB_CACHE_META_PATH)
            and open(EMB_CACHE_META_PATH, encoding="utf-8").read() == emb_signature):
        # cache valida: ricarica i vettori dal disco
        print(f"Embeddings trovati in cache ({EMB_CACHE_PATH}), li ricarico...")
        all_embeddings = np.load(EMB_CACHE_PATH)
    else:
        # cache assente o non valida: calcola gli embedding di TUTTI i documenti e salvali
        all_embeddings = embedding_model.encode(
            all_documents,
            show_progress_bar=True,
            batch_size=64,                  # quanti documenti alla volta (compromesso memoria/velocità)
            convert_to_numpy=True,
            normalize_embeddings=True       # norma 1: serve perché prodotto scalare == coseno
        ).astype(np.float32)
        np.save(EMB_CACHE_PATH, all_embeddings)
        with open(EMB_CACHE_META_PATH, "w", encoding="utf-8") as f:
            f.write(emb_signature)
    print(f"Embeddings disponibili: {all_embeddings.shape}")   # (numero_documenti, 768)

    # --- CICLO INTERNO: un giro per ogni dimensione del corpus ---
    for N_DOCS in N_DOCS_LIST:

        print(f"\n{'=' * 60}")
        print(f"  ESPERIMENTO  embedding={model_tag}  N_DOCS = {N_DOCS:,}")
        print('=' * 60)

        print(f"\n[1/2] Corpus e indice FAISS per N_DOCS={N_DOCS:,} (slice del corpus completo)...")
        # Slicing dei primi N: i corpus sono annidati e non serve ricodificare nulla.
        documents   = all_documents[:N_DOCS]
        metadata    = all_metadata[:N_DOCS]
        faiss_index = build_faiss_index(all_embeddings[:N_DOCS])   # indice FAISS solo su questi N documenti
        print(f"Indice FAISS creato con {faiss_index.ntotal} vettori")

        print("[2/2] Confronto k su 7 query eterogenee...")
        # con IndexFlatIP (ricerca esatta) i top-k per k piccolo sono un prefisso dei top-k
        # per k grande: si recupera una sola volta a max(K_VALUES) e si fa slicing, invece
        # di rifare retrieve()+encode() per ciascun valore di k (~4x ricerche/encode in meno)
        max_k = max(K_VALUES)
        # per ogni k accumula le metriche di tutte le query (poi si fa la media)
        per_k = {k: {'p': [], 'cr': [], 'p_bert': None} for k in K_VALUES}

        for query, keywords in GOLD_STANDARD.items():
            full_results = retrieve(query, faiss_index, documents, metadata, k=max_k)   # top-15
            # embedding della query e dei primi 200 caratteri dei 15 documenti (per la Context Relevance)
            qe = embedding_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
            snip_embs = embedding_model.encode(
                [r['document'][:200] for r in full_results],
                convert_to_numpy=True, normalize_embeddings=True
            )
            for k in K_VALUES:
                sliced = full_results[:k]                          # i primi k dei 15 già recuperati
                p = precision_at_k(sliced, keywords)
                cr = float(np.mean(snip_embs[:k] @ qe.T))          # stessa formula di context_relevance(), ma senza ricodificare
                per_k[k]['p'].append(p)
                per_k[k]['cr'].append(cr)
                if query == BERT_QUERY:
                    per_k[k]['p_bert'] = p                         # tiene da parte la precisione sulla sola query BERT

        # Media sulle 7 query, per ogni k
        k_summary = [
            {
                'k': k,
                'precision': float(np.mean(v['p'])),
                'context_relevance': float(np.mean(v['cr'])),
                'precision_bert': v['p_bert'],
            }
            for k, v in per_k.items()
        ]

        print(f"\n  {'k':>4} {'Precision@k':>12} {'Context Rel.':>14} {'P@k (BERT)':>12}")
        print(f"  {'-' * 46}")
        for row in k_summary:
            print(f"  {row['k']:>4} {row['precision']:>12.3f} {row['context_relevance']:>14.3f} {row['precision_bert']:>12.3f}")

        # k con la Precision@k più alta. In caso di parità max() restituisce il primo (quindi il k più piccolo);
        # la Precision tende a calare all'aumentare di k, quindi di solito vince k=3.
        best_k = max(k_summary, key=lambda r: r['precision'])['k']
        print(f"\n  k con Precision@k migliore: {best_k}")

        # Valutazione qualitativa con generazione: Answer Relevance e Faithfulness.
        # A DETAIL_N_DOCS si genera a OGNI k (non solo al best_k) per poter rispondere
        # anche sulla qualita' della generazione al variare di k, non solo sul retrieval.
        if N_DOCS == DETAIL_N_DOCS:
            # RAMO A: corpus più piccolo -> genera per tutti i k (4 k x 7 query = 28 risposte)
            print(f"\n  Generazione risposte per OGNI k (dettaglio limitato a "
                  f"N_DOCS={N_DOCS:,} per contenere i tempi su CPU)...")
            k_gen_summary = []
            for k in K_VALUES:
                ar_k, ff_k = [], []
                for query, keywords in GOLD_STANDARD.items():
                    results = retrieve(query, faiss_index, documents, metadata, k=k)
                    answer  = rag_answer(query, results)                     # chiamata all'LLM (la parte lenta)
                    ar_k.append(answer_relevance(query, answer))
                    ff_k.append(faithfulness_proxy(answer, results))
                    # conserva la risposta testuale, per riportare esempi nella relazione
                    qa_rows.append({
                        'embedding_model': EMBEDDING_MODEL, 'n_docs': N_DOCS, 'k': k,
                        'query': query, 'answer': answer,
                        'answer_relevance': ar_k[-1], 'faithfulness': ff_k[-1],
                    })
                k_gen_summary.append({
                    'k': k,
                    'answer_relevance': float(np.mean(ar_k)),
                    'faithfulness': float(np.mean(ff_k)),
                })
                print(f"    k={k:>2}: AnsRel={np.mean(ar_k):.3f}  Faith={np.mean(ff_k):.3f}")
            k_gen_rows.extend({'embedding_model': EMBEDDING_MODEL, 'n_docs': N_DOCS, **row}
                               for row in k_gen_summary)
            # per la tabella riepilogativa serve un solo valore: quello del best_k
            best_gen = next(r for r in k_gen_summary if r['k'] == best_k)
            answer_relevance_mean = best_gen['answer_relevance']
            faithfulness_mean     = best_gen['faithfulness']
        else:
            # RAMO B: corpus più grandi -> genera solo al best_k (7 risposte), per contenere i tempi
            print(f"\n  Generazione risposte per valutazione qualitativa (k={best_k})...")
            ar_list, ff_list = [], []
            for query, keywords in GOLD_STANDARD.items():
                results = retrieve(query, faiss_index, documents, metadata, k=best_k)
                answer  = rag_answer(query, results)
                ar_list.append(answer_relevance(query, answer))
                ff_list.append(faithfulness_proxy(answer, results))
                qa_rows.append({
                    'embedding_model': EMBEDDING_MODEL, 'n_docs': N_DOCS, 'k': best_k,
                    'query': query, 'answer': answer,
                    'answer_relevance': ar_list[-1], 'faithfulness': ff_list[-1],
                })
            answer_relevance_mean = float(np.mean(ar_list))
            faithfulness_mean     = float(np.mean(ff_list))

        # Salva il dettaglio per k (Precision e Context Relevance) di questa configurazione
        for row in k_summary:
            k_detail_rows.append({'embedding_model': EMBEDDING_MODEL, 'n_docs': N_DOCS, **row})

        # Salva la riga riepilogativa (modello, N_DOCS) usata nella tabella finale
        all_results.append({
            'embedding_model':  EMBEDDING_MODEL,
            'n_docs':           N_DOCS,
            'best_k':           best_k,
            'k_summary':        k_summary,
            'precision':        next(r['precision'] for r in k_summary if r['k'] == best_k),
            'precision_bert':   next(r['precision_bert'] for r in k_summary if r['k'] == best_k),
            'answer_relevance': answer_relevance_mean,
            'faithfulness':     faithfulness_mean,
        })

        print(f"  Answer Relevance media: {answer_relevance_mean:.3f}")
        print(f"  Faithfulness media:     {faithfulness_mean:.3f}")

# ============================================================
# RIEPILOGO COMPARATIVO FINALE
# Tabella con una riga per ogni (modello, N_DOCS): dà il colpo d'occhio per la relazione.
# ============================================================
print(f"\n\n{'=' * 60}")
print("  RIEPILOGO COMPARATIVO — variazione di embedding e N_DOCS")
print('=' * 60)

print(f"\n  {'Embedding':<28} {'N_DOCS':<9} {'best_k':>7} {'P@k':>8} "
      f"{'P@k (BERT)':>12} {'AnsRel':>8} {'Faith':>8}")
print(f"  {'-' * 84}")
for r in all_results:
    tag = r['embedding_model'].split('/')[-1]
    print(f"  {tag:<28} {r['n_docs']:<9,} {r['best_k']:>7} {r['precision']:>8.3f} "
          f"{r['precision_bert']:>12.3f} {r['answer_relevance']:>8.3f} {r['faithfulness']:>8.3f}")

print("\n  Nota: 'P@k (BERT)' è la Precision@k sulla sola query "
      "\"What is BERT and how does self-attention work?\" al k migliore di "
      "ciascuna configurazione — utile per capire se il retrieval semantico "
      "puro continua a perdere questo paper specifico al variare della "
      "dimensione del corpus e del modello di embedding (limite già osservato "
      "e motivante l'approccio ibrido di lab5_hybrid.py).")

# Tabella di dettaglio: come cambia la QUALITÀ DELLA RISPOSTA al variare di k (solo a DETAIL_N_DOCS)
print(f"\n\n  DETTAGLIO PER k — Answer Relevance e Faithfulness a N_DOCS={DETAIL_N_DOCS:,} "
      "(non solo al best_k)")
print(f"\n  {'Embedding':<28} {'k':>4} {'AnsRel':>8} {'Faith':>8}")
print(f"  {'-' * 50}")
for row in k_gen_rows:
    tag = row['embedding_model'].split('/')[-1]
    print(f"  {tag:<28} {row['k']:>4} {row['answer_relevance']:>8.3f} {row['faithfulness']:>8.3f}")

# ============================================================
# SALVATAGGIO SU DISCO (numeri e risposte generate per la relazione,
# senza doverli ricopiare a mano dallo stdout o rilanciare il run)
# ============================================================
# 1) riepilogo per (modello, N_DOCS); si esclude 'k_summary' perché è una lista annidata, non adatta a una cella CSV
summary_df = pd.DataFrame([{k: v for k, v in r.items() if k != 'k_summary'} for r in all_results])
summary_df.to_csv('risultati_rag_base_ndocs.csv', index=False)

# 2) Precision/Context Relevance per ogni (modello, N_DOCS, k)
pd.DataFrame(k_detail_rows).to_csv('risultati_rag_base_k_detail.csv', index=False)
# 3) Answer Relevance/Faithfulness per ogni k (solo a DETAIL_N_DOCS)
pd.DataFrame(k_gen_rows).to_csv('risultati_rag_base_k_gen_detail.csv', index=False)
# 4) tutte le risposte testuali generate, per esempi qualitativi
pd.DataFrame(qa_rows).to_csv('risultati_rag_base_risposte.csv', index=False)

print("\n  Salvati: risultati_rag_base_ndocs.csv, risultati_rag_base_k_detail.csv, "
      "risultati_rag_base_k_gen_detail.csv, risultati_rag_base_risposte.csv")

# ============================================================
# DEMO: RAG con citazione delle fonti su una query reale
# (usa l'ultimo modello di embedding e l'ultimo corpus rimasti in memoria
# dai cicli sopra, cioè mpnet sul corpus completo)
# ============================================================
def rag_with_sources(query, k=3):
    results = retrieve(query, faiss_index, documents, metadata, k=k)
    answer = rag_answer(query, results)
    print(f"Query: {query}\n\nANSWER:\n{answer}\n\nSOURCES:")
    for r in results:
        print(f"[Paper {r['rank']}] {r['metadata']['title']} "
              f"({r['metadata']['year']}) - sim {r['similarity']:.3f}")
    return answer


rag_with_sources("What is BERT and how does it work?")