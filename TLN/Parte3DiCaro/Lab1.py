import itertools
import os
import re
import string

import numpy as np
import pandas as pd
import nltk
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


# --- 1. SETUP RISORSE NLTK ---
RESOURCES = {
    "corpora/stopwords": "stopwords",
    "corpora/wordnet": "wordnet",
    "corpora/omw-1.4": "omw-1.4",
    "taggers/averaged_perceptron_tagger": "averaged_perceptron_tagger",
}

for resource_path, resource_name in RESOURCES.items():
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(resource_name)


# --- 2. INIZIALIZZAZIONE ---
STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()
SBERT_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def _wordnet_pos(treebank_pos):
    if treebank_pos.startswith("J"):
        return "a"
    if treebank_pos.startswith("V"):
        return "v"
    if treebank_pos.startswith("N"):
        return "n"
    if treebank_pos.startswith("R"):
        return "r"
    return "n"


# --- 3. PREPROCESSING UNIFICATO ---
def preprocess_definition(text):
    """
    Pipeline unica per Simlex e Simsem:
    lowercase, rimozione punteggiatura, stopwords, lemmatizzazione POS-aware.
    Restituisce sia la stringa pulita sia il set di token.
    """
    if not isinstance(text, str):
        return "", set()

    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    tokens = [t for t in text.split() if t.isalpha() and t not in STOP_WORDS and len(t) > 2]

    if not tokens:
        return "", set()

    tagged = pos_tag(tokens)
    lemmas = [LEMMATIZER.lemmatize(tok, _wordnet_pos(pos)) for tok, pos in tagged]

    cleaned = " ".join(lemmas)
    return cleaned, set(lemmas)


def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union


# --- 4. CARICAMENTO DATI ---
FILE_NAME = "Dataset definizioni-spurio.csv"

if not os.path.exists(FILE_NAME):
    print(f"ERRORE: File non trovato -> {FILE_NAME}")
    print(f"Cartella corrente: {os.getcwd()}")
    raise SystemExit(1)

try:
    df = pd.read_csv(FILE_NAME)
    print(f"Dataset caricato correttamente. Righe totali: {len(df)}")
except Exception as exc:
    print(f"Errore durante il caricamento: {exc}")
    raise SystemExit(1)


# Mappatura esplicita con metadati, senza inferenze da substring nel nome concetto
CONCEPTS = [
    {
        "concetto": "Music",
        "tipo": "Astratto",
        "specificita": "Generico",
        "colonna": "(AG) Definizione del concetto ASTRATTO e GENERICO",
    },
    {
        "concetto": "Ethics",
        "tipo": "Astratto",
        "specificita": "Specifico",
        "colonna": "(AS) Definizione del concetto ASTRATTO e SPECIFICO",
    },
    {
        "concetto": "Tree",
        "tipo": "Concreto",
        "specificita": "Generico",
        "colonna": "(CG) Definizione del concetto CONCRETO e GENERICO",
    },
    {
        "concetto": "Teapot",
        "tipo": "Concreto",
        "specificita": "Specifico",
        "colonna": "(CS) Definizione del concetto CONCRETO e SPECIFICO",
    },
]


# --- 5. CALCOLO SIMILARITA ---
results = []

print("\nCalcolo Similarita Lessicale (Simlex) e Semantica (Simsem) in corso...\n")

for item in CONCEPTS:
    concept = item["concetto"]
    column = item["colonna"]

    if column not in df.columns:
        print(f"Attenzione: colonna mancante -> {column}")
        continue

    raw_definitions = [d for d in df[column].dropna().tolist() if isinstance(d, str) and d.strip()]
    if len(raw_definitions) < 2:
        print(f"Attenzione: definizioni insufficienti per {concept}")
        continue

    processed = [preprocess_definition(d) for d in raw_definitions]
    cleaned_defs = [p[0] for p in processed if p[0]]
    token_sets = [p[1] for p in processed if p[0]]

    if len(cleaned_defs) < 2:
        print(f"Attenzione: definizioni utili insufficienti dopo preprocessing per {concept}")
        continue

    # Simlex = media pairwise Jaccard sui token lemmatizzati
    simlex_scores = []
    for i, j in itertools.combinations(range(len(token_sets)), 2):
        simlex_scores.append(jaccard_similarity(token_sets[i], token_sets[j]))
    avg_simlex = float(np.mean(simlex_scores)) if simlex_scores else 0.0

    # Simsem = cosine similarity su embedding Sentence-BERT
    embs = SBERT_MODEL.encode(cleaned_defs, show_progress_bar=False)
    cos_sim_matrix = cosine_similarity(embs)
    upper_tri = cos_sim_matrix[np.triu_indices(cos_sim_matrix.shape[0], k=1)]
    avg_simsem = float(np.mean(upper_tri)) if len(upper_tri) else 0.0

    results.append(
        {
            "Concetto": concept,
            "Tipo": item["tipo"],
            "Specificita": item["specificita"],
            "Simlex": round(avg_simlex, 4),
            "Simsem": round(avg_simsem, 4),
            "Delta_Simsem_minus_Simlex": round(avg_simsem - avg_simlex, 4),
            "N_definizioni": len(cleaned_defs),
        }
    )


# --- 6. OUTPUT ---
if not results:
    print("Nessun risultato disponibile.")
    raise SystemExit(0)

res_df = pd.DataFrame(results)
by_tipo = (
    res_df.groupby("Tipo")[["Simlex", "Simsem", "Delta_Simsem_minus_Simlex"]]
    .mean()
    .round(4)
    .reset_index()
)
by_specificita = (
    res_df.groupby("Specificita")[["Simlex", "Simsem", "Delta_Simsem_minus_Simlex"]]
    .mean()
    .round(4)
    .reset_index()
)

print("--- RISULTATI PER CONCETTO ---")
print(res_df.to_string(index=False))

print("\n--- AGGREGAZIONE PER TIPO (Concretezza) ---")
print(by_tipo.to_string(index=False))

print("\n--- AGGREGAZIONE PER SPECIFICITA ---")
print(by_specificita.to_string(index=False))

res_df.to_csv("risultati_lab1_concetti.csv", index=False)
by_tipo.to_csv("risultati_lab1_by_tipo.csv", index=False)
by_specificita.to_csv("risultati_lab1_by_specificita.csv", index=False)

print("\nFile salvati:")
print("- risultati_lab1_concetti.csv")
print("- risultati_lab1_by_tipo.csv")
print("- risultati_lab1_by_specificita.csv")
