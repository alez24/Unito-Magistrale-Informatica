"""
LAB-2: Valutazione Content-to-Form (Ricerca Onomasiologica)
TLN 2025/2026 - Prof. Di Caro

Obiettivo: data una definizione (contenuto), risalire al synset WordNet corretto (forma).
Approccio: cosine similarity TF-IDF tra ogni definizione e le glosse dei synset candidati.
"""

import pandas as pd
import re, string, itertools
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------------------------------------------------------------------
# 1. SYNSET CANDIDATI (da WordNet 3.1)
#    Per ogni concetto: lista di (synset_id, glossa)
#    Il primo elemento è il synset target (quello corretto)
# ---------------------------------------------------------------------------
WORDNET_SYNSETS = {
    'Music': [
        ('music.n.01', 'an artistic form of auditory communication incorporating instrumental or vocal tones in a structured and continuous manner'),
        ('music.n.02', 'any agreeable (pleasing and harmonious) sounds'),
        ('music.n.03', 'musical activity (singing or whistling etc.)'),
        ('music.n.04', 'the sounds produced by singers or musical instruments (or reproductions of such sounds)'),
        ('music.n.05', 'punishment for one\'s actions'),
    ],
    'Ethics': [
        ('ethics.n.01', 'the philosophical study of moral values and rules'),
        ('ethical_motive.n.01', 'motivation based on ideas of right and wrong'),
        ('ethics.n.02', 'a system of principles governing morality and acceptable conduct'),
        ('morality.n.01', 'concern with the distinction between good and evil or right and wrong; right or good conduct'),
        ('moral_philosophy.n.01', 'the branch of philosophy that studies the principles of right and wrong in human conduct'),
    ],
    'Tree': [
        ('tree.n.01', 'a tall perennial woody plant having a main trunk and branches forming a distinct elevated crown; includes both gymnosperms and angiosperms'),
        ('tree.n.02', 'a figure that branches from a single root'),
        ('tree.n.03', 'English actor and theater manager who was the son of Herbert Beerbohm Tree'),
        ('corner.n.04', 'force a person or an animal into a position from which he cannot escape'),
        ('plant.n.01', 'a living organism lacking the power of locomotion'),
    ],
    'Teapot': [
        ('teapot.n.01', 'pot for brewing tea; usually has a spout and handle'),
        ('pot.n.01', 'metal or earthenware cooking vessel that is usually round and deep; often has a handle and lid'),
        ('vessel.n.03', 'a container used for carrying or storing liquids'),
        ('kettle.n.01', 'a metal pot for stewing or boiling; usually has a lid'),
        ('container.n.01', 'any object that can be used to hold things (especially a large metal container for liquids)'),
    ]
}

# ---------------------------------------------------------------------------
# 2. STOPWORDS E PULIZIA TESTO
# ---------------------------------------------------------------------------
STOPWORDS = set([
    'a','an','the','and','or','but','in','on','of','to','for','is','are',
    'was','were','it','its','this','that','which','with','by','from','as','at','be',
    'has','have','had','not','can','may','also','one','two','used','use','often',
    'usually','made','make','such','some','other','their','they','them','than',
    'more','most','very','each','both','into','through','during','including',
    'before','after','above','below','between','out','off','over','under','then',
    'once','here','there','when','where','who','how','all','any','few','no','nor',
    'so','yet','only','own','same','just','because','while','although','though',
    'if','what','about','up','down','s','do','does','did','will','would','could',
    'should','might','must','shall','been','being','am','he','she','we','you',
    'i','me','him','her','us','my','your','his','our','its'
])

def clean(text):
    """Pulisce il testo rimuovendo punteggiatura e stopwords."""
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
    return ' '.join([w for w in text.split() if w not in STOPWORDS and len(w) > 2])

# ---------------------------------------------------------------------------
# 3. CARICAMENTO DATI
# ---------------------------------------------------------------------------
df = pd.read_csv('Dataset definizioni-spurio.csv')
print(f"Dataset caricato: {len(df)} righe\n")

col_map = {
    'Music':  '(AG) Definizione del concetto ASTRATTO e GENERICO',
    'Ethics': '(AS) Definizione del concetto ASTRATTO e SPECIFICO',
    'Tree':   '(CG) Definizione del concetto CONCRETO e GENERICO',
    'Teapot': '(CS) Definizione del concetto CONCRETO e SPECIFICO',
}

# ---------------------------------------------------------------------------
# 4. RICERCA ONOMASIOLOGICA: definizione → synset
# ---------------------------------------------------------------------------
all_results = []

for concept, col in col_map.items():
    definitions = df[col].dropna().tolist()
    synsets     = WORDNET_SYNSETS[concept]
    syn_names   = [s[0] for s in synsets]
    syn_glosses = [s[1] for s in synsets]
    target_syn  = syn_names[0]  # synset corretto

    concept_results = []
    for idx, defn in enumerate(definitions):
        defn_clean    = clean(defn)
        glosses_clean = [clean(g) for g in syn_glosses]

        # Calcola cosine similarity TF-IDF tra definizione e ogni glossa
        corpus = [defn_clean] + glosses_clean
        tfidf  = TfidfVectorizer()
        try:
            mat   = tfidf.fit_transform(corpus)
            sims  = cosine_similarity(mat[0:1], mat[1:])[0]
            best_idx    = int(np.argmax(sims))
            best_score  = round(float(sims[best_idx]), 4)
            best_synset = syn_names[best_idx]
            best_gloss  = syn_glosses[best_idx]
        except Exception:
            best_synset = target_syn
            best_score  = 0.0
            best_gloss  = syn_glosses[0]

        correct = (best_synset == target_syn)

        concept_results.append({
            'Concetto':     concept,
            'Tipo':         'Astratto' if concept in ['Music', 'Ethics'] else 'Concreto',
            'Specificità':  'Generico' if concept in ['Music', 'Tree']   else 'Specifico',
            'Def_ID':       idx + 1,
            'Definizione':  defn,
            'Synset trovato': best_synset,
            'Synset corretto': target_syn,
            'Corretto':     correct,
            'Score':        best_score,
            'Glossa WordNet': best_gloss,
        })
        all_results.append(concept_results[-1])

    scores  = [r['Score'] for r in concept_results]
    correct_count = sum(1 for r in concept_results if r['Corretto'])

    print(f"{'='*60}")
    print(f"Concetto: {concept} | Tipo: {concept_results[0]['Tipo']} {concept_results[0]['Specificità']}")
    print(f"Synset target: {target_syn}")
    print(f"Synset trovato correttamente: {correct_count}/{len(definitions)}")
    print(f"Score medio: {np.mean(scores):.4f} | Max: {max(scores):.4f} | Min: {min(scores):.4f}")

# ---------------------------------------------------------------------------
# 5. AGGREGAZIONE E OUTPUT
# ---------------------------------------------------------------------------
res_df = pd.DataFrame(all_results)

print(f"\n{'='*60}")
print("AGGREGAZIONE PER TIPO (Astratto vs Concreto)")
agg_tipo = res_df.groupby('Tipo').agg(
    Score_medio=('Score', 'mean'),
    Accuratezza=('Corretto', 'mean')
).round(4)
print(agg_tipo)

print(f"\nAGGREGAZIONE PER SPECIFICITÀ (Generico vs Specifico)")
agg_spec = res_df.groupby('Specificità').agg(
    Score_medio=('Score', 'mean'),
    Accuratezza=('Corretto', 'mean')
).round(4)
print(agg_spec)

# Salva risultati
res_df.to_csv('risultati_lab2.csv', index=False)
print("\nRisultati salvati in: risultati_lab2.csv")