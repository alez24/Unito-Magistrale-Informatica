# ============================================================
# LAB 8 - Word Clustering Based on Word2Vec Representation
# TLN - Daniele Radicioni, UNITO
# Confronto: testi musicali anni 70 vs anni 2000
# ============================================================

import re
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

import nltk
warnings.filterwarnings('ignore') # per evitare messaggi di warning quindi errori non critici  durante l'addestramento Word2Vec

stop = set(stopwords.words('english')) # lista di stopword in inglese da rimuovere dai testi

print("=" * 60)
print("LAB 8 - Word2Vec su testi musicali")
print("Anni 70 vs Anni 2000")
print("=" * 60)

# Caricamento  dataset

print("\n[STEP 1] Caricamento dataset...")

df = pd.read_csv('spotify_millsongdata.csv')
print(f"Dataset: {df.shape[0]} canzoni, {df['artist'].nunique()} artisti")


# Selezione artisti per era

print("\n[STEP 2] Selezione artisti per era...")

artisti_70s = [
    'Led Zeppelin', 'Pink Floyd', 'Queen',
    'Eagles', 'Fleetwood Mac', 'Bee Gees',
    'David Bowie', 'Elton John', 'ABBA',
    'Doors', 'Rolling Stones', 'Deep Purple'
]

artisti_2000s = [
    'Eminem', 'Coldplay', 'Linkin Park',
    'Christina Aguilera', 'Radiohead', 'Foo Fighters',
    'Lady Gaga', 'Taylor Swift', 'The Killers',
    'Green Day', 'Nickelback'
]
# filtriamo il dataset per ottenere solo le canzoni degli artisti selezionati per gli anni 70 e per gli anni 2000, creando due nuovi dataframe separati(.copy())
df_70s   = df[df['artist'].isin(artisti_70s)].copy() 
df_2000s = df[df['artist'].isin(artisti_2000s)].copy()

# stampiamo la lista degli artisti trovati per gli anni 70 e 2000, ordinati alfabeticamente, e il numero totale di canzoni trovate.
print(f"Artisti 70s trovati:   {sorted(df_70s['artist'].unique())}") 
print(f"Canzoni anni 70:       {len(df_70s)}")
print(f"\nArtisti 2000s trovati: {sorted(df_2000s['artist'].unique())}")
print(f"Canzoni anni 2000:     {len(df_2000s)}")


#Pulizia testi con NLTK

print("\n[STEP 3] Pulizia testi...")

def pulisci_testo(testo): 
    if not isinstance(testo, str): # se il testo non è una stringa  restituisce una lista vuota 
        return []
    # rimuove eventuali annotazioni o parti tra parentesi quadre che spesso si trovano nei testi delle canzoni
    testo = re.sub(r'\[.*?\]', '', testo) 
    testo = re.sub(r'[^a-zA-Z\s]', '', testo)
    testo = testo.lower()
    tokens = testo.split()
    tokens = [t for t in tokens if t not in stop and len(t) >= 3] # rimuove stopword e parole troppo corte (meno di 3 caratteri)
    return tokens
# applichiamo la funzione di pulizia a tutti i testi , creando una nuova colonna 'tokens'  che contiene la lista dei token puliti per ogni canzone.
df_70s['tokens']   = df_70s['text'].apply(pulisci_testo)
df_2000s['tokens'] = df_2000s['text'].apply(pulisci_testo)

# filtriamo ulteriormente i dataframe per mantenere solo le canzoni che hanno almeno 5 token dopo la pulizia (map funzione di pandas per applicare la regola )
df_70s   = df_70s[df_70s['tokens'].map(len) > 5] 
df_2000s = df_2000s[df_2000s['tokens'].map(len) > 5]
# creiamo due liste di tutti i token presenti nei testi degli anni 70 e degli anni 2000, appiattendo la lista di token per ogni canzone in un'unica lista complessiva.
tutti_70s   = [t for tok in df_70s['tokens']   for t in tok]
tutti_2000s = [t for tok in df_2000s['tokens'] for t in tok]

print(f"Anni 70  → {len(df_70s)} canzoni, "
      f"{len(tutti_70s)} token, "
      f"{len(set(tutti_70s))} unici")
print(f"Anni 2000 → {len(df_2000s)} canzoni, "
      f"{len(tutti_2000s)} token, "
      f"{len(set(tutti_2000s))} unici")

# calcoliamo la frequenza di ogni parola (token) presente nei testi degli anni 70 e degli anni 2000, utilizzando la classe Counter della libreria collections. 
# Questo ci permette di identificare le parole più comuni in ciascuna era.
freq_70s   = Counter(tutti_70s)
freq_2000s = Counter(tutti_2000s)

# most_common restituisce una lista di tuple (parola, frequenza) ordinata per frequenza decrescente
print("\nTop 15 parole anni 70:")
for p, c in freq_70s.most_common(15): 
    print(f"  {p:<15} → {c}")

print("\nTop 15 parole anni 2000:")
for p, c in freq_2000s.most_common(15):
    print(f"  {p:<15} → {c}")


# Addestramento Word2Vec


print("\nAddestramento Word2Vec")
# definiamo i parametri comuni per l'addestramento dei modelli Word2Vec per entrambe le ere.
params = dict(
    vector_size = 100,# dimensione dei vettori di embedding  un numero potrebbe rappresentare quanto la parola è positiva, un altro quanto è legata al tempo.
    window      = 5,# dimensione della finestra di contesto (quanto lontano guardare a sinistra e a destra della parola target durante l'addestramento)
    min_count   = 3,# frequenza minima di una parola per essere inclusa nel vocabolario (serve a filtrare parole troppo rare che potrebbero non avere un embedding di qualità)
    workers     = 4,# numero di thread da utilizzare per l'addestramento 
    epochs      = 20, # Quante volte l'algoritmo deve rileggere tutti i testi dall'inizio alla fine
    seed        = 42# seme per la generazione dei numeri casuali
)


# addestriamo due modelli Word2Vec separati, uno per i testi degli anni 70 e uno per i testi degli anni 2000, utilizzando la lista di token puliti come input.

#trasformmiamo la colonna 'tokens' di ciascun dataframe in una lista di liste di token (una lista per ogni canzone con toList()) 
# e la passiamo al costruttore di Word2Vec insieme ai parametri definiti (params-->con ** aggiungimao alla scatola i parametri ).

#Word2vec è una funzione che prende in input una lista di frasi (dove ogni frase è una lista di parole) 
# e restituisce un modello che contiene i vettori di embedding per ogni parola presente nei testi.
model_70s   = Word2Vec(sentences=df_70s['tokens'].tolist(),   **params)
model_2000s = Word2Vec(sentences=df_2000s['tokens'].tolist(), **params)

print(f"Vocabolario anni 70:   {len(model_70s.wv)} parole") # restituisce il numero di parole nel vocabolario del modello.
print(f"Vocabolario anni 2000: {len(model_2000s.wv)} parole") # restituisce il numero di parole nel vocabolario del modello.


#Parole simili

print("\n Parole simili per parola chiave...")

parole_test = ['love', 'night', 'heart', 'world', 'time', 'life', 'feel']

print(f"\n{'PAROLA':<10} | {'TOP 3 ANNI 70':<35} | TOP 3 ANNI 2000")
print("-" * 80)
 
# per ogni parola nella lista parole_test, calcoliamo le parole più simili utilizzando il metodo most_similar del modello Word2Vec.
for parola in parole_test:
    sim_70   = [w for w,_ in model_70s.wv.most_similar(parola, topn=3)] \
               if parola in model_70s.wv else ['---'] 
    sim_2000 = [w for w,_ in model_2000s.wv.most_similar(parola, topn=3)] \
               if parola in model_2000s.wv else ['---']
    print(f"{parola:<10} | {', '.join(sim_70):<35} | {', '.join(sim_2000)}") 
# se la parola è presente nel vocabolario del modello degli anni 70, calcoliamo le parole più simili; altrimenti, 
#  una lista con '---' per indicare che la parola non è presente.




#Similarità tra coppie

print("\nSimilarità coseno tra coppie di parole...")
# definiamo una lista di coppie di parole per le quali vogliamo calcolare la similarità coseno nei due modelli.
coppie = [
    ('love', 'heart'),
    ('love', 'money'),
    ('night', 'dark'),
    ('god',  'heaven'),
    ('war',  'peace'),
    ('free', 'soul'),
]

print(f"\n{'Coppia':<22} | {'Anni 70':>8} | {'Anni 2000':>10}")
print("-" * 48)
# per ogni coppia di parole, calcoliamo la similarità coseno utilizzando il metodo similarity del modello Word2Vec, 
# se entrambe le parole sono presenti nel vocabolario; altrimenti, stampiamo '---' per indicare che la coppia non è confrontabile.

#4f serve per arrotondare il risultato a 4 cifre decimali per una visualizzazione più pulita.

#similarity è una funzione che prende in input due parole e restituisce un numero compreso tra -1 e 1 
# che rappresenta quanto sono simili tra loro in base ai loro vettori di embedding.
for w1, w2 in coppie:
    s70   = f"{model_70s.wv.similarity(w1,w2):.4f}" \
            if w1 in model_70s.wv   and w2 in model_70s.wv   else "---"
    s2000 = f"{model_2000s.wv.similarity(w1,w2):.4f}" \
            if w1 in model_2000s.wv and w2 in model_2000s.wv else "---"
    print(f"({w1}, {w2}){'':6} | {s70:>8} | {s2000:>10}")




#Analisi vocabolario

print("\n Analisi vocabolario...")

vocab_70s   = set(model_70s.wv.index_to_key) # restituisce un elenco di tutte le parole presenti nel vocabolario del modello degli anni 70, 
vocab_2000s = set(model_2000s.wv.index_to_key)# restituisce un elenco di tutte le parole presenti nel vocabolario del modello degli anni 2000.

solo_70s   = vocab_70s - vocab_2000s
solo_2000s = vocab_2000s - vocab_70s
comuni     = vocab_70s & vocab_2000s

print(f"Solo anni 70:   {len(solo_70s)} parole")
print(f"Solo anni 2000: {len(solo_2000s)} parole")
print(f"In comune:      {len(comuni)} parole")

interessanti_70s   = sorted( # ordiniamo le parole presenti solo negli anni 70 in base alla loro frequenza (freq_70s) e manteniamo solo quelle con frequenza maggiore di 20.
    [p for p in solo_70s   if freq_70s[p]   > 20],
    key=lambda x: -freq_70s[x]
)
interessanti_2000s = sorted( # ordiniamo le parole presenti solo negli anni 2000 in base alla loro frequenza (freq_2000s) e manteniamo solo quelle con frequenza maggiore di 20.
    [p for p in solo_2000s if freq_2000s[p] > 20],
    key=lambda x: -freq_2000s[x] # ordiniamo le parole in base alla frequenza decrescente (il più frequente prima ) (lambda funzione usa e getta)
)

print(f"\nParole caratteristiche anni 70   (freq > 20):")
print(f"  {interessanti_70s[:20]}") # stampiamo le prime 20 parole più frequenti che sono presenti solo nei testi degli anni 70 e non nei testi degli anni 2000, indicando che sono parole caratteristiche di quell'era.
print(f"\nParole caratteristiche anni 2000 (freq > 20):")
print(f"  {interessanti_2000s[:20]}")# stampiamo le prime 20 parole più frequenti che sono presenti solo nei testi degli anni 2000 e non nei testi degli anni 70, indicando che sono parole caratteristiche di quell'era.


#Analisi sistematica coppie di parole

print("\nAnalisi sistematica coppie...")

FREQ_COPPIE = 100
# selezioniamo le parole che sono presenti in entrambe le ere (vocab_70s & vocab_2000s) 
# e che hanno una frequenza maggiore o uguale a FREQ_COPPIE in entrambi i periodi.
candidati = [ 
    p for p in (vocab_70s & vocab_2000s)
    if freq_70s[p] >= FREQ_COPPIE and freq_2000s[p] >= FREQ_COPPIE
]
# calcoliamo il numero totale di coppie uniche che possono essere formate con le parole candidate,
# utilizzando la formula n*(n-1)/2, dove n è il numero di parole candidate.
print(f"Parole candidate (freq >= {FREQ_COPPIE} in entrambe): {len(candidati)}")
print(f"Coppie totali da confrontare: {len(candidati) * (len(candidati)-1) // 2}")

coppie_sist = [] 
# per ogni coppia unica di parole candidate, calcoliamo la similarità coseno tra le due parole nei modelli degli anni 70 e degli anni 2000,
for i, w1 in enumerate(candidati):
    for w2 in candidati[i+1:]:
        s70   = model_70s.wv.similarity(w1, w2)
        s2000 = model_2000s.wv.similarity(w1, w2)
        delta = abs(s70 - s2000) # calcoliamo la differenza assoluta tra le due similarità (delta) per capire quanto è cambiata la relazione tra queste parole tra le due ere.
        coppie_sist.append({ # aggiungiamo un dizionario con le informazioni sulla coppia di parole e le loro similarità nei due modelli alla lista coppie_sist.
            'w1':        w1,
            'w2':        w2,
            's70':       s70,
            's2000':     s2000,
            'delta':     delta,
            'direzione': s2000 - s70,
        })

# ordiniamo la lista coppie_sist in base al delta in ordine decrescente, 
#in modo da avere le coppie che hanno cambiato di più la loro relazione tra le due ere in cima alla lista.
coppie_sist.sort(key=lambda x: -x['delta']) 


sep = "=" * 65
sep2 = "-" * 65
print("\n" + sep)
print("TOP 20 COPPIE CON PIU' CAMBIAMENTO DI SIMILARITA'")
print("(delta alto = la relazione tra queste parole e' cambiata molto)")
print(sep)
print(f"{'COPPIA':<26} {'ANNI 70':>8} {'ANNI 2000':>10} {'DELTA':>7}  TREND")
print(sep2)

for r in coppie_sist[:20]:
    trend    = "piu' vicine ->" if r['direzione'] > 0 else "<- piu' lontane"
    coppia   = f"({r['w1']}, {r['w2']})"
    print(f"{coppia:<26} {r['s70']:>8.4f} {r['s2000']:>10.4f} {r['delta']:>7.4f}  {trend}")

print("\n" + sep)
print("TOP 10 COPPIE PIU' STABILI")
print("(delta basso = la relazione e' rimasta praticamente uguale)")
print(sep)
print(f"{'COPPIA':<26} {'ANNI 70':>8} {'ANNI 2000':>10} {'DELTA':>7}")
print(sep2)

for r in coppie_sist[-10:][::-1]:
    coppia = f"({r['w1']}, {r['w2']})"
    print(f"{coppia:<26} {r['s70']:>8.4f} {r['s2000']:>10.4f} {r['delta']:>7.4f}")


#Analisi sistematica vocabolario comune

print("\n Analisi sistematica parole comuni...")

FREQ_MINIMA   = 30
TOP_N_VICINI  = 10 # numero di vicini più simili da considerare per ogni parola quando confrontiamo i contesti tra le due ere
TOP_RISULTATI = 30
# selezioniamo le parole che sono presenti in entrambe le ere (comuni) e che hanno una frequenza maggiore o uguale a FREQ_MINIMA in entrambi i periodi,
parole_frequenti_comuni = [
    p for p in comuni
    if freq_70s[p] >= FREQ_MINIMA and freq_2000s[p] >= FREQ_MINIMA
]

print(f"Parole comuni con freq >= {FREQ_MINIMA} in entrambe le ere: "
      f"{len(parole_frequenti_comuni)}")

risultati = []
# per ogni parola comune che soddisfa il criterio di frequenza, calcoliamo i vicini più simili nei modelli degli anni 70 e degli anni 2000,
for parola in parole_frequenti_comuni:
    vicini_70s   = set(w for w,_ in model_70s.wv.most_similar(parola,   topn=TOP_N_VICINI))
    vicini_2000s = set(w for w,_ in model_2000s.wv.most_similar(parola, topn=TOP_N_VICINI))

    n_comuni_v  = len(vicini_70s & vicini_2000s)
    overlap     = n_comuni_v / TOP_N_VICINI
    cambiamento = 1 - overlap

    risultati.append({
        'parola':       parola,
        'cambiamento':  cambiamento,
        'overlap':      overlap,
        'vicini_70s':   vicini_70s,
        'vicini_2000s': vicini_2000s,
        'freq_70s':     freq_70s[parola],
        'freq_2000s':   freq_2000s[parola],
    })

risultati.sort(key=lambda x: -x['cambiamento'])

print(f"\n{'='*70}")
print(f"TOP {TOP_RISULTATI} PAROLE CHE HANNO CAMBIATO PIU' CONTESTO")
print(f"(overlap basso = vicini completamente diversi tra le due ere)")
print(f"{'='*70}")
print(f"{'#':<4} {'PAROLA':<12} {'CAMBIAMENTO':>12} {'OVERLAP':>8} "
      f"{'FREQ 70s':>9} {'FREQ 2000s':>10}")
print("-" * 70)
# stampiamo le parole che hanno cambiato di più il loro contesto tra le due ere,
#  ordinati per cambiamento decrescente, mostrando anche l'overlap tra i vicini più simili e le frequenze nei due periodi.
for i, r in enumerate(risultati[:TOP_RISULTATI]): 
    print(f"{i+1:<4} {r['parola']:<12} {r['cambiamento']:>11.0%} "
          f"{r['overlap']:>8.0%} {r['freq_70s']:>9} {r['freq_2000s']:>10}")

print(f"\n{'='*70}")
print("DETTAGLIO TOP 10: cosa era vicino prima vs adesso")
print(f"{'='*70}")

for r in risultati[:10]:
    p            = r['parola']
    solo_70s_v   = r['vicini_70s']  - r['vicini_2000s']
    solo_2000s_v = r['vicini_2000s'] - r['vicini_70s']
    rimasti      = r['vicini_70s']  & r['vicini_2000s']

    print(f"\n[ {p.upper()} ]  cambiamento: {r['cambiamento']:.0%}  "
          f"(freq: {r['freq_70s']} anni70 / {r['freq_2000s']} anni2000)")
    print(f"  Vicini spariti  (solo anni 70):   {', '.join(sorted(solo_70s_v))}")
    print(f"  Vicini nuovi    (solo anni 2000): {', '.join(sorted(solo_2000s_v))}")
    print(f"  Rimasti stabili:                  {', '.join(sorted(rimasti)) or 'nessuno'}")

print(f"\n{'='*70}")
print(f"TOP 10 PAROLE PIU' STABILI (contesto quasi identico tra le ere)")
print(f"{'='*70}")
# stampiamo le parole che hanno cambiato di meno il loro contesto tra le due ere, ordinati per cambiamento crescente, mostrando anche l'overlap tra i vicini più simili.
for r in risultati[-10:][::-1]: 
    vicini_comuni_str = ', '.join(sorted(r['vicini_70s'] & r['vicini_2000s']))
    print(f"  {r['parola']:<12} overlap: {r['overlap']:.0%}  "
          f"| vicini comuni: {vicini_comuni_str}")


# Clustering K-Means

print("\n Clustering K-Means...")
# definiamo una funzione fai_clustering che prende in input un modello Word2Vec, il numero di cluster da creare 
# e il numero di parole più frequenti da considerare per il clustering.
def fai_clustering(model, n_clusters=6, top_words=200): 
    parole  = model.wv.index_to_key[:top_words]
    vettori = np.array([model.wv[w] for w in parole]) # creiamo una matrice di vettori di embedding per le parole selezionate, dove ogni riga corrisponde al vettore di una parola.
    km      = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels  = km.fit_predict(vettori) # applichiamo l'algoritmo di clustering K-Means alla matrice dei vettori di embedding, ottenendo un'etichetta di cluster per ogni parola.
    cluster = {}
    # creiamo un dizionario cluster che raggruppa le parole in base alle loro etichette di cluster, in modo da poter analizzare quali parole sono state assegnate a ciascun cluster.
    for p, l in zip(parole, labels):
        cluster.setdefault(l, []).append(p) # per ogni parola e la sua etichetta di cluster, aggiungiamo la parola alla lista corrispondente nel dizionario cluster, utilizzando setdefault per inizializzare la lista se il cluster non è ancora presente.
    return cluster, list(parole), vettori, labels
# applichiamo la funzione fai_clustering ai modelli degli anni 70 e degli anni 2000, ottenendo i cluster di parole per ciascuna era.
print("\nCluster anni 70 (top 200 parole, 6 cluster):")
cl_70s, par_70s, vec_70s, lbl_70s = fai_clustering(model_70s)
for cid, parole_cl in sorted(cl_70s.items()):
    print(f"  Cluster {cid}: {', '.join(parole_cl[:12])}")

print("\nCluster anni 2000 (top 200 parole, 6 cluster):")
cl_2000s, par_2000s, vec_2000s, lbl_2000s = fai_clustering(model_2000s)
for cid, parole_cl in sorted(cl_2000s.items()):
    print(f"  Cluster {cid}: {', '.join(parole_cl[:12])}")


# Grafici

print("\n Generazione grafici...")

# helper: top-N parole per cluster ordinate per frequenza
def top_per_cluster(parole, labels, freq_dict, n=7):
    result = {}
    for cid in np.unique(labels):
        words_in = [p for p, l in zip(parole, labels) if l == cid]
        result[cid] = sorted(words_in, key=lambda w: -freq_dict.get(w, 0))[:n]
    return result

# === FIGURA 1: t-SNE migliorato ===
print("  Generazione t-SNE...")
fig1, axes1 = plt.subplots(1, 2, figsize=(20, 9))
fig1.suptitle('Clustering Word2Vec: Anni 70 vs Anni 2000',
              fontsize=16, fontweight='bold')

def tsne_plot_v2(parole, vettori, labels, freq_dict, titolo, ax, n_clusters=6):
    n_perp = min(30, max(5, len(parole) - 1))
    tsne = TSNE(n_components=2, random_state=42, perplexity=n_perp, max_iter=1000)
    v2d = tsne.fit_transform(vettori)

    colors = plt.cm.tab10(np.linspace(0, 0.9, n_clusters))
    top_words = top_per_cluster(parole, labels, freq_dict, n=7)
    annotated = set()
    for tw_list in top_words.values():
        annotated.update(tw_list)

    for cid in range(n_clusters):
        mask = labels == cid
        ax.scatter(v2d[mask, 0], v2d[mask, 1],
                   c=[colors[cid]], label=f'C{cid}',
                   alpha=0.5, s=50, zorder=2)

    for i, p in enumerate(parole):
        if p in annotated:
            ax.annotate(p, (v2d[i, 0], v2d[i, 1]),
                        fontsize=8.5, fontweight='bold', zorder=5,
                        bbox=dict(boxstyle='round,pad=0.2', fc='white',
                                  alpha=0.75, ec='none'),
                        xytext=(4, 4), textcoords='offset points')

    ax.set_title(titolo, fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='best', framealpha=0.7, ncol=2)
    ax.set_xlabel('t-SNE dim 1', fontsize=10)
    ax.set_ylabel('t-SNE dim 2', fontsize=10)
    ax.grid(True, alpha=0.15, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

tsne_plot_v2(par_70s, vec_70s, lbl_70s, freq_70s,
             'Anni 70 — Led Zeppelin, Pink Floyd, Queen, Eagles…', axes1[0])
tsne_plot_v2(par_2000s, vec_2000s, lbl_2000s, freq_2000s,
             'Anni 2000 — Eminem, Coldplay, Taylor Swift, Linkin Park…', axes1[1])

plt.tight_layout(pad=2)
plt.savefig('word2vec_cluster.png', dpi=150, bbox_inches='tight')
print("  Salvato: word2vec_cluster.png")
plt.close()


# === FIGURA 2: Heatmap similarità ===
print("  Generazione heatmap similarità...")
KEYWORDS = ['love', 'life', 'night', 'heart', 'god',
            'soul', 'free', 'time', 'baby', 'feel', 'world', 'dark']
kw = [p for p in KEYWORDS if p in model_70s.wv and p in model_2000s.wv]

def build_sim_matrix(model, words):
    n = len(words)
    mat = np.zeros((n, n))
    for i, w1 in enumerate(words):
        for j, w2 in enumerate(words):
            mat[i, j] = 1.0 if i == j else model.wv.similarity(w1, w2)
    return mat

mat70  = build_sim_matrix(model_70s, kw)
mat00  = build_sim_matrix(model_2000s, kw)
diff_m = mat00 - mat70
np.fill_diagonal(diff_m, 0)

fig2, axes2 = plt.subplots(1, 3, figsize=(22, 7))
fig2.suptitle('Similarità coseno tra parole chiave: Anni 70 vs Anni 2000',
              fontsize=14, fontweight='bold')

for ax_i, (mat, title, cmap, vmin, vmax) in enumerate([
    (mat70,   'Anni 70',          'RdYlGn', -0.3,  1.0),
    (mat00,   'Anni 2000',        'RdYlGn', -0.3,  1.0),
    (diff_m,  'Δ (2000s − 70s)', 'coolwarm', -0.5, 0.5),
]):
    ax = axes2[ax_i]
    im = ax.imshow(mat, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')
    ax.set_xticks(range(len(kw)))
    ax.set_yticks(range(len(kw)))
    ax.set_xticklabels(kw, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(kw, fontsize=9)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=8)
    plt.colorbar(im, ax=ax, shrink=0.75, pad=0.02)

    for i in range(len(kw)):
        for j in range(len(kw)):
            if i == j:
                continue
            val = mat[i, j]
            if ax_i == 2:
                if abs(val) < 0.05:
                    continue
                txt   = f'{val:+.2f}'
                color = 'white' if abs(val) > 0.3 else 'black'
            else:
                txt   = f'{val:.2f}'
                color = 'white' if (val > 0.6 or val < -0.1) else 'black'
            ax.text(j, i, txt, ha='center', va='center',
                    fontsize=7, color=color)

plt.tight_layout()
plt.savefig('word2vec_heatmap.png', dpi=150, bbox_inches='tight')
print("  Salvato: word2vec_heatmap.png")
plt.close()


# === FIGURA 3: Deriva semantica ===
print("  Generazione grafici deriva semantica...")
fig3, axes3 = plt.subplots(1, 2, figsize=(20, 8))
fig3.suptitle('Deriva semantica tra le due ere musicali',
              fontsize=14, fontweight='bold')

# 3a: Top 20 parole con maggiore deriva (da analisi sistematica)
top_n   = 20
top_d   = risultati[:top_n]
lbls_d  = [r['parola'] for r in top_d][::-1]
vals_d  = [r['cambiamento'] for r in top_d][::-1]

cmap_d = plt.cm.Reds(np.linspace(0.35, 0.9, top_n))
axes3[0].barh(range(top_n), vals_d, color=cmap_d, alpha=0.9, height=0.7)
axes3[0].set_yticks(range(top_n))
axes3[0].set_yticklabels(lbls_d, fontsize=10)
axes3[0].set_xlabel('Grado di cambiamento del contesto semantico', fontsize=11)
axes3[0].set_title(f'Top {top_n} parole con maggiore deriva semantica',
                    fontsize=12, fontweight='bold')
axes3[0].set_xlim(0, 1.18)
for i, v in enumerate(vals_d):
    axes3[0].text(v + 0.02, i, f'{v:.0%}', va='center', fontsize=9)
axes3[0].axvline(x=0.5, color='gray', linestyle='--', alpha=0.4, label='soglia 50%')
axes3[0].legend(fontsize=9)
axes3[0].spines['top'].set_visible(False)
axes3[0].spines['right'].set_visible(False)

# 3b: scatter plot coppie (sim70s vs sim2000s) — top 800 per delta
ax_s   = axes3[1]
n_plot = min(800, len(coppie_sist))
s70_v  = [r['s70']   for r in coppie_sist[:n_plot]]
s00_v  = [r['s2000'] for r in coppie_sist[:n_plot]]
d_v    = [r['delta'] for r in coppie_sist[:n_plot]]

sc = ax_s.scatter(s70_v, s00_v, c=d_v, cmap='YlOrRd',
                   alpha=0.5, s=18, vmin=0, vmax=0.35, zorder=2)

all_vals = s70_v + s00_v
lo = min(all_vals) - 0.05
hi = max(all_vals) + 0.05
ax_s.plot([lo, hi], [lo, hi], 'k--', alpha=0.4, lw=1.5, label='nessun cambiamento')
ax_s.fill_between([lo, hi], [lo, hi], [hi, hi], alpha=0.04, color='steelblue')
ax_s.fill_between([lo, hi], [lo, lo], [lo, hi], alpha=0.04, color='tomato')
ax_s.text(lo + 0.02, hi - 0.05, 'più vicine\nnei 2000s',
           fontsize=8, color='steelblue', alpha=0.8)
ax_s.text(hi - 0.18, lo + 0.02, 'più lontane\nnei 2000s',
           fontsize=8, color='tomato', alpha=0.8)

for r in coppie_sist[:8]:
    ax_s.annotate(f"{r['w1']}–{r['w2']}", (r['s70'], r['s2000']),
                   fontsize=7.5, alpha=0.85,
                   xytext=(6, 4), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.1', fc='white', alpha=0.6, ec='none'))

ax_s.set_xlim(lo, hi)
ax_s.set_ylim(lo, hi)
ax_s.set_xlabel('Similarità coseno — Anni 70', fontsize=11)
ax_s.set_ylabel('Similarità coseno — Anni 2000', fontsize=11)
ax_s.set_title('Coppie di parole: 70s vs 2000s\n(sopra diagonale = più simili nei 2000s)',
                fontsize=12, fontweight='bold')
plt.colorbar(sc, ax=ax_s, label='|Δ similarità|', shrink=0.8)
ax_s.legend(fontsize=9, loc='upper left')
ax_s.grid(True, alpha=0.2)
ax_s.spines['top'].set_visible(False)
ax_s.spines['right'].set_visible(False)

plt.tight_layout(pad=2)
plt.savefig('word2vec_drift.png', dpi=150, bbox_inches='tight')
print("  Salvato: word2vec_drift.png")
plt.close()


# STEP 10: Riepilogo

print("\n[STEP 10] Riepilogo finale...")

print("\n=== PAROLE PIU' VICINE A 'love' ===")
if 'love' in model_70s.wv:
    print(f"Anni 70:   {[w for w,_ in model_70s.wv.most_similar('love', topn=8)]}")
if 'love' in model_2000s.wv:
    print(f"Anni 2000: {[w for w,_ in model_2000s.wv.most_similar('love', topn=8)]}")

print("\n=== PAROLE PIU' VICINE A 'night' ===")
if 'night' in model_70s.wv:
    print(f"Anni 70:   {[w for w,_ in model_70s.wv.most_similar('night', topn=8)]}")
if 'night' in model_2000s.wv:
    print(f"Anni 2000: {[w for w,_ in model_2000s.wv.most_similar('night', topn=8)]}")

print("\n=== PAROLE PIU' VICINE A 'feel' ===")
if 'feel' in model_70s.wv:
    print(f"Anni 70:   {[w for w,_ in model_70s.wv.most_similar('feel', topn=8)]}")
if 'feel' in model_2000s.wv:
    print(f"Anni 2000: {[w for w,_ in model_2000s.wv.most_similar('feel', topn=8)]}")

print(f"\n=== VOCABOLARIO ===")
print(f"Anni 70:         {len(model_70s.wv)} parole")
print(f"Anni 2000:       {len(model_2000s.wv)} parole")
print(f"Solo anni 70:    {len(solo_70s)}")
print(f"Solo anni 2000:  {len(solo_2000s)}")
print(f"In comune:       {len(comuni)}")

print("\nLab completato!")
print("File generati:")
print("  - word2vec_cluster.png   (t-SNE clustering 70s vs 2000s)")
print("  - word2vec_heatmap.png   (heatmap similarità parole chiave)")
print("  - word2vec_drift.png     (deriva semantica + scatter coppie)")