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
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

warnings.filterwarnings('ignore')

stop = set(stopwords.words('english'))

print("=" * 60)
print("LAB 8 - Word2Vec su testi musicali")
print("Anni 70 vs Anni 2000")
print("=" * 60)

# ============================================================
# STEP 1: Carica dataset
# ============================================================
print("\n[STEP 1] Caricamento dataset...")

df = pd.read_csv('spotify_millsongdata.csv')
print(f"Dataset: {df.shape[0]} canzoni, {df['artist'].nunique()} artisti")

# ============================================================
# STEP 2: Selezione artisti per era
# ============================================================
print("\n[STEP 2] Selezione artisti per era...")

artisti_70s = [
    'Led Zeppelin', 'Pink Floyd', 'Queen',
    'Eagles', 'Fleetwood Mac', 'Bee Gees',
    'David Bowie', 'Elton John', 'ABBA',
    'Doors', 'Rolling Stones', 'Deep Purple'
]

artisti_2000s = [
    'Eminem', 'Coldplay', 'Linkin Park',
    'Kanye West', 'Radiohead', 'Foo Fighters',
    'Lady Gaga', 'Taylor Swift', 'The Killers',
    'Green Day', 'Nickelback'
]

df_70s   = df[df['artist'].isin(artisti_70s)].copy()
df_2000s = df[df['artist'].isin(artisti_2000s)].copy()

print(f"Artisti 70s trovati:   {sorted(df_70s['artist'].unique())}")
print(f"Canzoni anni 70:       {len(df_70s)}")
print(f"\nArtisti 2000s trovati: {sorted(df_2000s['artist'].unique())}")
print(f"Canzoni anni 2000:     {len(df_2000s)}")

# ============================================================
# STEP 3: Pulizia testi con NLTK
# ============================================================
print("\n[STEP 3] Pulizia testi...")

def pulisci_testo(testo):
    """
    Pulisce un testo lirico rimuovendo:
    - indicazioni strutturali [Chorus], [Verse]...
    - punteggiatura e caratteri non alfabetici
    - stopwords NLTK
    - parole molto corte (< 3 caratteri)
    Restituisce una lista di token puliti.
    """
    if not isinstance(testo, str):
        return []

    # Rimuovi [Chorus], [Verse 1], etc.
    testo = re.sub(r'\[.*?\]', '', testo)

    # Solo lettere e spazi
    testo = re.sub(r'[^a-zA-Z\s]', '', testo)

    # Lowercase
    testo = testo.lower()

    # Tokenizza con NLTK
    tokens = word_tokenize(testo)

    # Rimuovi stopwords e parole corte
    tokens = [t for t in tokens
              if t not in stop
              and len(t) >= 3]

    return tokens

df_70s['tokens']   = df_70s['text'].apply(pulisci_testo)
df_2000s['tokens'] = df_2000s['text'].apply(pulisci_testo)

# Rimuovi canzoni vuote
df_70s   = df_70s[df_70s['tokens'].map(len) > 5]
df_2000s = df_2000s[df_2000s['tokens'].map(len) > 5]

tutti_70s   = [t for tok in df_70s['tokens']   for t in tok]
tutti_2000s = [t for tok in df_2000s['tokens'] for t in tok]

print(f"Anni 70  → {len(df_70s)} canzoni, "
      f"{len(tutti_70s)} token, "
      f"{len(set(tutti_70s))} unici")
print(f"Anni 2000 → {len(df_2000s)} canzoni, "
      f"{len(tutti_2000s)} token, "
      f"{len(set(tutti_2000s))} unici")

freq_70s   = Counter(tutti_70s)
freq_2000s = Counter(tutti_2000s)

print("\nTop 15 parole anni 70:")
for p, c in freq_70s.most_common(15):
    print(f"  {p:<15} → {c}")

print("\nTop 15 parole anni 2000:")
for p, c in freq_2000s.most_common(15):
    print(f"  {p:<15} → {c}")

# ============================================================
# STEP 4: Addestramento Word2Vec
# ============================================================
print("\n[STEP 4] Addestramento Word2Vec...")

# Parametri:
# vector_size: dimensione embedding (quante dimensioni ha ogni vettore)
# window:      contesto (quante parole prima/dopo considerare)
# min_count:   ignora parole che appaiono meno di N volte
# epochs:      quante volte scorre il dataset durante il training
# seed:        per riproducibilità

params = dict(
    vector_size = 100,
    window      = 5,
    min_count   = 3,
    workers     = 4,
    epochs      = 20,
    seed        = 42
)

model_70s   = Word2Vec(sentences=df_70s['tokens'].tolist(),   **params)
model_2000s = Word2Vec(sentences=df_2000s['tokens'].tolist(), **params)

print(f"Vocabolario anni 70:   {len(model_70s.wv)} parole")
print(f"Vocabolario anni 2000: {len(model_2000s.wv)} parole")

# ============================================================
# STEP 5: Parole simili
# ============================================================
print("\n[STEP 5] Parole simili per parola chiave...")

parole_test = ['love', 'night', 'heart', 'world', 'time', 'life', 'feel']

print(f"\n{'PAROLA':<10} | {'TOP 3 ANNI 70':<35} | TOP 3 ANNI 2000")
print("-" * 80)

for parola in parole_test:
    sim_70   = [w for w,_ in model_70s.wv.most_similar(parola, topn=3)] \
               if parola in model_70s.wv else ['---']
    sim_2000 = [w for w,_ in model_2000s.wv.most_similar(parola, topn=3)] \
               if parola in model_2000s.wv else ['---']
    print(f"{parola:<10} | {', '.join(sim_70):<35} | {', '.join(sim_2000)}")

# ============================================================
# STEP 6: Similarità tra coppie
# ============================================================
print("\n[STEP 6] Similarità coseno tra coppie di parole...")

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

for w1, w2 in coppie:
    s70   = f"{model_70s.wv.similarity(w1,w2):.4f}" \
            if w1 in model_70s.wv   and w2 in model_70s.wv   else "---"
    s2000 = f"{model_2000s.wv.similarity(w1,w2):.4f}" \
            if w1 in model_2000s.wv and w2 in model_2000s.wv else "---"
    print(f"({w1}, {w2}){'':6} | {s70:>8} | {s2000:>10}")

# ============================================================
# STEP 7: Analisi vocabolario
# ============================================================
print("\n[STEP 7] Analisi vocabolario...")

vocab_70s   = set(model_70s.wv.index_to_key)
vocab_2000s = set(model_2000s.wv.index_to_key)

solo_70s   = vocab_70s - vocab_2000s
solo_2000s = vocab_2000s - vocab_70s
comuni     = vocab_70s & vocab_2000s

print(f"Solo anni 70:   {len(solo_70s)} parole")
print(f"Solo anni 2000: {len(solo_2000s)} parole")
print(f"In comune:      {len(comuni)} parole")

# Filtra parole con frequenza significativa
interessanti_70s   = sorted(
    [p for p in solo_70s   if freq_70s[p]   > 20],
    key=lambda x: -freq_70s[x]
)
interessanti_2000s = sorted(
    [p for p in solo_2000s if freq_2000s[p] > 20],
    key=lambda x: -freq_2000s[x]
)

print(f"\nParole caratteristiche anni 70   (freq > 20):")
print(f"  {interessanti_70s[:20]}")
print(f"\nParole caratteristiche anni 2000 (freq > 20):")
print(f"  {interessanti_2000s[:20]}")

# ============================================================
# STEP 8: Clustering K-Means
# ============================================================
print("\n[STEP 8] Clustering K-Means...")

def fai_clustering(model, n_clusters=6, top_words=200):
    """
    Prende le top_words parole più comuni nel vocabolario,
    le rappresenta come vettori Word2Vec e le raggruppa
    con K-Means in n_clusters cluster.
    """
    parole  = model.wv.index_to_key[:top_words]
    vettori = np.array([model.wv[w] for w in parole])
    km      = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels  = km.fit_predict(vettori)
    cluster = {}
    for p, l in zip(parole, labels):
        cluster.setdefault(l, []).append(p)
    return cluster, list(parole), vettori, labels

print("\nCluster anni 70 (top 200 parole, 6 cluster):")
cl_70s, par_70s, vec_70s, lbl_70s = fai_clustering(model_70s)
for cid, parole_cl in sorted(cl_70s.items()):
    print(f"  Cluster {cid}: {', '.join(parole_cl[:12])}")

print("\nCluster anni 2000 (top 200 parole, 6 cluster):")
cl_2000s, par_2000s, vec_2000s, lbl_2000s = fai_clustering(model_2000s)
for cid, parole_cl in sorted(cl_2000s.items()):
    print(f"  Cluster {cid}: {', '.join(parole_cl[:12])}")

# ============================================================
# STEP 9: Grafici
# ============================================================
print("\n[STEP 9] Generazione grafici...")

def tsne_plot(parole, vettori, labels, titolo, ax, n_clusters=6):
    """
    Riduce i vettori a 2D con t-SNE e li visualizza
    colorati per cluster. Annota le parole più significative.
    """
    tsne = TSNE(n_components=2, random_state=42,
                perplexity=30, max_iter=1000)
    v2d  = tsne.fit_transform(vettori)

    colori    = plt.cm.Set1(np.linspace(0, 1, n_clusters))
    highlight = {
        'love', 'night', 'heart', 'baby', 'time',
        'world', 'life', 'feel', 'fire', 'rain',
        'sun', 'soul', 'free', 'dark', 'light', 'god'
    }

    for cid in range(n_clusters):
        mask = labels == cid
        ax.scatter(v2d[mask, 0], v2d[mask, 1],
                   c=[colori[cid]], label=f'Cluster {cid}',
                   alpha=0.7, s=60)

    for i, p in enumerate(parole):
        if p in highlight:
            ax.annotate(p, (v2d[i, 0], v2d[i, 1]),
                        fontsize=9, fontweight='bold',
                        xytext=(5, 5),
                        textcoords='offset points')

    ax.set_title(titolo, fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.set_xlabel('t-SNE dim 1')
    ax.set_ylabel('t-SNE dim 2')

# --- Grafico 1: t-SNE + frequenze ---
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('Word2Vec - Testi Musicali: Anni 70 vs Anni 2000',
             fontsize=15, fontweight='bold')

tsne_plot(par_70s, vec_70s, lbl_70s,
          'Cluster parole anni 70\n'
          '(Pink Floyd, Queen, Eagles, Bee Gees...)',
          axes[0, 0])

tsne_plot(par_2000s, vec_2000s, lbl_2000s,
          'Cluster parole anni 2000\n'
          '(Eminem, Coldplay, Lady Gaga, Taylor Swift...)',
          axes[0, 1])

top15_70s   = freq_70s.most_common(15)
top15_2000s = freq_2000s.most_common(15)

axes[1, 0].barh([p for p,_ in top15_70s][::-1],
                [c for _,c in top15_70s][::-1],
                color='steelblue', alpha=0.8)
axes[1, 0].set_title('Top 15 parole anni 70', fontweight='bold')
axes[1, 0].set_xlabel('Frequenza')

axes[1, 1].barh([p for p,_ in top15_2000s][::-1],
                [c for _,c in top15_2000s][::-1],
                color='coral', alpha=0.8)
axes[1, 1].set_title('Top 15 parole anni 2000', fontweight='bold')
axes[1, 1].set_xlabel('Frequenza')

plt.tight_layout()
plt.savefig('word2vec_analisi.png', dpi=150, bbox_inches='tight')
print("Salvato: word2vec_analisi.png")

# --- Grafico 2: similarità con "love" ---
fig2, ax2 = plt.subplots(figsize=(10, 5))

parole_sim = ['heart', 'life', 'night', 'time', 'feel', 'baby']
parole_sim = [p for p in parole_sim
              if p in model_70s.wv and p in model_2000s.wv]

x     = np.arange(len(parole_sim))
width = 0.35

ax2.bar(x - width/2,
        [model_70s.wv.similarity('love', p)   for p in parole_sim],
        width, label='Anni 70',   color='steelblue', alpha=0.8)
ax2.bar(x + width/2,
        [model_2000s.wv.similarity('love', p) for p in parole_sim],
        width, label='Anni 2000', color='coral', alpha=0.8)

ax2.set_xticks(x)
ax2.set_xticklabels(parole_sim, fontsize=11)
ax2.set_ylabel('Similarità coseno con "love"')
ax2.set_title('Come cambia il concetto di "love" tra le due ere',
              fontweight='bold')
ax2.legend()
ax2.set_ylim(0, 1)

plt.tight_layout()
plt.savefig('word2vec_similarita.png', dpi=150, bbox_inches='tight')
print("Salvato: word2vec_similarita.png")

# ============================================================
# STEP 10: Riepilogo
# ============================================================
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
print("  - word2vec_analisi.png")
print("  - word2vec_similarita.png")
