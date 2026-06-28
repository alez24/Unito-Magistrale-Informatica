import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string
import re
import itertools
import numpy as np
import os

# --- 1. SETUP E DOWNLOAD RISORSE NLTK ---
# Esegue il download delle risorse linguistiche se non sono già presenti
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
    nltk.download('omw-1.4')

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# --- 2. INIZIALIZZAZIONE ---
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# --- 3. DEFINIZIONE FUNZIONI DI UTILITA' ---
def clean_text(text):
    """
    Pulisce il testo: lo converte in minuscolo, rimuove la punteggiatura, 
    tokenizza, rimuove le stopword e applica la lemmatizzazione.
    """
    if not isinstance(text, str): 
        return set()
    
    text = text.lower()
    text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    
    return set(words)

def jaccard_similarity(set1, set2):
    """
    Calcola l'Indice di Jaccard (Simlex) tra due insiemi di parole.
    Formula: Intersezione / Unione
    """
    if not set1 or not set2: 
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union

# --- 4. CARICAMENTO DATI ---
file_name = 'Dataset definizioni-spurio.csv'

# Verifica che il file esista nella cartella corrente
if not os.path.exists(file_name):
    print(f"ERRORE: Il file '{file_name}' non è stato trovato nella cartella corrente:")
    print(os.getcwd())
    print("Assicurati di aver scaricato il dataset e di averlo messo nella stessa cartella di questo script.")
    exit()

try:
    df = pd.read_csv(file_name)
    print(f"Dataset caricato correttamente. Righe totali: {len(df)}")
except Exception as e:
    print(f"Errore durante il caricamento del file: {e}")
    exit()

# --- 5. ELABORAZIONE DATI ---
# Mappatura: Nome del concetto -> Nome esatto della colonna nel CSV
cols = {
    'Music (AG)': '(AG) Definizione del concetto ASTRATTO e GENERICO',
    'Ethics (AS)': '(AS) Definizione del concetto ASTRATTO e SPECIFICO',
    'Tree (CG)': '(CG) Definizione del concetto CONCRETO e GENERICO',
    'Teapot (CS)': '(CS) Definizione del concetto CONCRETO e SPECIFICO'
}

results = []

print("\nCalcolo delle similarità in corso...\n")

for concept, col_name in cols.items():
    if col_name not in df.columns:
        print(f"Attenzione: La colonna '{col_name}' non esiste nel dataset. Salto questo concetto.")
        continue
        
    # Estrae le definizioni ignorando le righe vuote
    definitions = df[col_name].dropna().tolist()
    
    if len(definitions) < 2:
        print(f"Attenzione: Non ci sono abbastanza definizioni valide per il concetto '{concept}'.")
        continue
    
    # --- CALCOLO SIMLEX (Jaccard Similarity Pairwise) ---
    simlex_scores = []
    cleaned_defs = [clean_text(d) for d in definitions]
    
    # Crea tutte le combinazioni possibili di coppie di definizioni
    for i, j in itertools.combinations(range(len(cleaned_defs)), 2):
        score = jaccard_similarity(cleaned_defs[i], cleaned_defs[j])
        simlex_scores.append(score)
        
    avg_simlex = np.mean(simlex_scores) if simlex_scores else 0
    
    # --- CALCOLO SIMSEM (Cosine Similarity con TF-IDF) ---
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        # Vettorializza le definizioni
        tfidf_matrix = tfidf.fit_transform(definitions)
        
        # Calcola la matrice di similarità coseno
        cos_sim_matrix = cosine_similarity(tfidf_matrix)
        
        # Estrae i valori sopra la diagonale (evitando di confrontare una definizione con se stessa)
        upper_tri = cos_sim_matrix[np.triu_indices(cos_sim_matrix.shape[0], k=1)]
        avg_simsem = np.mean(upper_tri) if len(upper_tri) > 0 else 0
    except Exception as e:
        print(f"Errore nel calcolo TF-IDF per {concept}: {e}")
        avg_simsem = 0
        
    # Salva i risultati
    results.append({
        'Concetto': concept,
        'Tipo': 'Astratto' if 'A' in concept else 'Concreto',
        'Specificità': 'Generico' if 'G' in concept else 'Specifico',
        'Simlex (Jaccard)': round(avg_simlex, 3),
        'Simsem (Cosine)': round(avg_simsem, 3)
    })

# --- 6. OUTPUT RISULTATI ---
if results:
    res_df = pd.DataFrame(results)
    print("--- RISULTATI FINALI ---")
    print(res_df.to_string(index=False))
    
    # Salva i risultati in un nuovo file CSV
    output_file = 'risultati_similarita.csv'
    res_df.to_csv(output_file, index=False)
    print(f"\nI risultati sono stati salvati anche nel file: {output_file}")
else:
    print("Nessun risultato da mostrare.")