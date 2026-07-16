# LAB 8 - Word Clustering Based on Word2Vec Representation
# TLN - Daniele Radicioni, UNITO
# Confronto: testi musicali anni 70 vs anni 2000

import re
import sys
import io
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# su Windows la console non e' UTF-8 di default: senza questo i print con simboli non-ASCII crashano
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import nltk
from collections import Counter
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

 # silenzia i warning non critici di gensim, non i nostri
warnings.filterwarnings('ignore', module=r'gensim.*') 


try:
    stop = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    stop = set(stopwords.words('english'))

# le contrazioni perdono l'apostrofo nella pulizia (don't -> dont), quindi
# non sono coperte dalle stopword NLTK: le aggiungiamo esplicitamente
stop.update(['dont', 'cant', 'wont', 'aint', 'youre', 'youll', 'youve',
             'ive', 'ill', 'im', 'id', 'hes', 'shes', 'thats',
             'were', 'weve', 'theyre', 'lets', 'didnt', 'doesnt',
             'isnt', 'wasnt', 'couldnt', 'wouldnt', 'theres'])

print("=" * 60)
print("LAB 8 - Word2Vec su testi musicali")
print("Anni 70 vs Anni 2000")
print("=" * 60)

print("\nCaricamento dataset...")

df = pd.read_csv('spotify_millsongdata.csv')
print(f"Dataset: {df.shape[0]} canzoni, {df['artist'].nunique()} artisti")

print("\nSelezione artisti per era...")

artisti_70s = [
    'Black Sabbath', 'Pink Floyd', 'Queen',
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

df_70s   = df[df['artist'].isin(artisti_70s)].copy()
df_2000s = df[df['artist'].isin(artisti_2000s)].copy()

print(f"Artisti 70s trovati:   {sorted(df_70s['artist'].unique())}")
print(f"Canzoni anni 70:       {len(df_70s)}")
print(f"\nArtisti 2000s trovati: {sorted(df_2000s['artist'].unique())}")
print(f"Canzoni anni 2000:     {len(df_2000s)}")

# isin() non solleva errori se un nome non trova corrispondenze: verifica esplicita
n_trovati_70s   = df_70s['artist'].nunique()
n_trovati_2000s = df_2000s['artist'].nunique()
if n_trovati_70s != len(artisti_70s):
    mancanti = set(artisti_70s) - set(df_70s['artist'].unique())
    print(f"ATTENZIONE: attesi {len(artisti_70s)} artisti anni 70, trovati {n_trovati_70s}. Mancanti: {mancanti}")
if n_trovati_2000s != len(artisti_2000s):
    mancanti = set(artisti_2000s) - set(df_2000s['artist'].unique())
    print(f"ATTENZIONE: attesi {len(artisti_2000s)} artisti anni 2000, trovati {n_trovati_2000s}. Mancanti: {mancanti}")

print("\nPulizia testi...")

def pulisci_testo(testo):
    """Tokenizza un testo di canzone rimuovendo annotazioni, punteggiatura, stopword e parole corte."""
    if not isinstance(testo, str):
        return []
    testo = re.sub(r'\[.*?\]', '', testo)
    testo = re.sub(r'[^a-zA-Z\s]', '', testo)
    testo = testo.lower()
    tokens = testo.split()
    tokens = [t for t in tokens if t not in stop and len(t) >= 3]
    return tokens

df_70s['tokens']   = df_70s['text'].apply(pulisci_testo)
df_2000s['tokens'] = df_2000s['text'].apply(pulisci_testo)

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

print("\nAddestramento Word2Vec...")

params = dict(
    sg          = 1,     # Skip-gram (il default di gensim sarebbe CBOW, sg=0)
    vector_size = 100,
    window      = 5,
    min_count   = 3,
    workers     = 1,     # riproducibilita' bit-esatta: con workers>1 l'ordine di
                          # elaborazione tra thread varia e il training smette di essere
                          # deterministico anche a parita' di seed (costo trascurabile
                          # su un corpus di questa dimensione)
    epochs      = 20,
    seed        = 42
)

model_70s   = Word2Vec(sentences=df_70s['tokens'].tolist(),   **params)
model_2000s = Word2Vec(sentences=df_2000s['tokens'].tolist(), **params)

print(f"Vocabolario anni 70:   {len(model_70s.wv)} parole")
print(f"Vocabolario anni 2000: {len(model_2000s.wv)} parole")

print("\nParole simili per parola chiave...")

parole_test = ['love', 'night', 'heart', 'world', 'time', 'life', 'feel']

print(f"\n{'PAROLA':<10} | {'TOP 3 ANNI 70':<35} | TOP 3 ANNI 2000")
print("-" * 80)

for parola in parole_test:
    sim_70   = [w for w,_ in model_70s.wv.most_similar(parola, topn=3)] \
               if parola in model_70s.wv else ['---']
    sim_2000 = [w for w,_ in model_2000s.wv.most_similar(parola, topn=3)] \
               if parola in model_2000s.wv else ['---']
    print(f"{parola:<10} | {', '.join(sim_70):<35} | {', '.join(sim_2000)}")

print("\nSimilarità coseno tra coppie di parole...")

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

print("\nAnalisi vocabolario...")

vocab_70s   = set(model_70s.wv.index_to_key)
vocab_2000s = set(model_2000s.wv.index_to_key)

solo_70s   = vocab_70s - vocab_2000s
solo_2000s = vocab_2000s - vocab_70s
comuni     = vocab_70s & vocab_2000s

print(f"Solo anni 70:   {len(solo_70s)} parole")
print(f"Solo anni 2000: {len(solo_2000s)} parole")
print(f"In comune:      {len(comuni)} parole")

interessanti_70s = sorted(
    [p for p in solo_70s   if freq_70s[p]   > 20],
    key=lambda x: (-freq_70s[x], x)
)
interessanti_2000s = sorted(
    [p for p in solo_2000s if freq_2000s[p] > 20],
    key=lambda x: (-freq_2000s[x], x)
)

print(f"\nParole caratteristiche anni 70   (freq > 20):")
print(f"  {interessanti_70s[:20]}")
print(f"\nParole caratteristiche anni 2000 (freq > 20):")
print(f"  {interessanti_2000s[:20]}")

print("\nAnalisi sistematica coppie...")

FREQ_COPPIE = 100
# sorted(): l'intersezione fra due set ha un ordine di iterazione dipendente da
# PYTHONHASHSEED (randomizzato ad ogni processo Python); senza un ordine fisso,
# le liste con parita' esatta di punteggio (vedi STEP 9) sarebbero non riproducibili
candidati = [
    p for p in sorted(vocab_70s & vocab_2000s)
    if freq_70s[p] >= FREQ_COPPIE and freq_2000s[p] >= FREQ_COPPIE
]
print(f"Parole candidate (freq >= {FREQ_COPPIE} in entrambe): {len(candidati)}")
print(f"Coppie totali da confrontare: {len(candidati) * (len(candidati)-1) // 2}")

# similarita' vettorizzata: una singola matrice N x N invece di N^2/2 chiamate
# a .similarity() (rilevante quando i candidati salgono a qualche centinaio)
def matrice_coseno(model, parole):
    vettori = np.array([model.wv[p] for p in parole])
    norme   = vettori / np.linalg.norm(vettori, axis=1, keepdims=True)
    return norme @ norme.T

sim70  = matrice_coseno(model_70s,   candidati)
sim2000 = matrice_coseno(model_2000s, candidati)

coppie_sist = []
for i, w1 in enumerate(candidati):
    for j in range(i + 1, len(candidati)):
        w2    = candidati[j]
        s70   = float(sim70[i, j])
        s2000 = float(sim2000[i, j])
        coppie_sist.append({
            'w1':        w1,
            'w2':        w2,
            's70':       s70,
            's2000':     s2000,
            'delta':     abs(s70 - s2000),
            'direzione': s2000 - s70,
        })

coppie_sist.sort(key=lambda x: (-x['delta'], x['w1'], x['w2']))

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

print("\nAnalisi sistematica parole comuni...")

FREQ_MINIMA   = 30
TOP_N_VICINI  = 10
TOP_RISULTATI = 30

parole_frequenti_comuni = [
    p for p in sorted(comuni)
    if freq_70s[p] >= FREQ_MINIMA and freq_2000s[p] >= FREQ_MINIMA
]

print(f"Parole comuni con freq >= {FREQ_MINIMA} in entrambe le ere: "
      f"{len(parole_frequenti_comuni)}")

risultati = []
# cambiamento = 1 - overlap tra i top-N vicini nelle due ere
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

# tra le parole a pari 'cambiamento' (frequente, dato che overlap e' quantizzato
# su 11 soli livelli) si preferisce mostrare prima quelle piu' frequenti: la
# stima di overlap e' piu' affidabile quando il vicinato e' basato su piu' occorrenze
risultati.sort(key=lambda x: (-x['cambiamento'], -(x['freq_70s'] + x['freq_2000s']), x['parola']))

print(f"\n{'='*70}")
print(f"TOP {TOP_RISULTATI} PAROLE CHE HANNO CAMBIATO PIU' CONTESTO")
print(f"(overlap basso = vicini completamente diversi tra le due ere)")
print(f"{'='*70}")
print(f"{'#':<4} {'PAROLA':<12} {'CAMBIAMENTO':>12} {'OVERLAP':>8} "
      f"{'FREQ 70s':>9} {'FREQ 2000s':>10}")
print("-" * 70)
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
for r in risultati[-10:][::-1]:
    vicini_comuni_str = ', '.join(sorted(r['vicini_70s'] & r['vicini_2000s']))
    print(f"  {r['parola']:<12} overlap: {r['overlap']:.0%}  "
          f"| vicini comuni: {vicini_comuni_str}")

print("\nClustering K-Means...")

def fai_clustering(model, n_clusters=6, top_words=200):
    """Raggruppa le parole più frequenti in cluster semantici via KMeans sugli embedding."""
    parole  = model.wv.index_to_key[:top_words]
    vettori = np.array([model.wv[w] for w in parole])
    # KMeans usa distanza euclidea: senza normalizzare, un vettore con norma anomala
    # domina la distanza e finisce isolato in un cluster singoletto. Normalizzando a
    # norma unitaria il clustering diventa coerente con la cosine similarity usata
    # nel resto dell'analisi.
    vettori_norm = vettori / np.linalg.norm(vettori, axis=1, keepdims=True)
    km      = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels  = km.fit_predict(vettori_norm)
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

print("\nGenerazione grafici...")

def top_per_cluster(parole, labels, freq_dict, n=7):
    """Le n parole più frequenti di ciascun cluster, usate per etichettare i punti nel plot t-SNE."""
    result = {}
    for cid in np.unique(labels):
        words_in = [p for p, l in zip(parole, labels) if l == cid]
        result[cid] = sorted(words_in, key=lambda w: -freq_dict.get(w, 0))[:n]
    return result

# --- FIGURA 1: t-SNE ---
print("  Generazione t-SNE...")
fig1, axes1 = plt.subplots(1, 2, figsize=(20, 9))
fig1.suptitle('Clustering Word2Vec: Anni 70 vs Anni 2000',
              fontsize=16, fontweight='bold')

def tsne_plot_v2(parole, vettori, labels, freq_dict, titolo, ax, n_clusters=6):
    """Proietta gli embedding in 2D con t-SNE, colorati per cluster e annotati solo nei punti chiave."""
    n_perp = min(30, max(5, len(parole) - 1))  # perplexity limitata dal numero di punti
    # niente max_iter/n_iter espliciti: il nome del parametro e' cambiato tra
    # versioni di scikit-learn, il default (1000) e' comunque quello voluto
    tsne = TSNE(n_components=2, random_state=42, perplexity=n_perp)
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
             'Anni 70 — Black Sabbath, Pink Floyd, Queen, Eagles…', axes1[0])
tsne_plot_v2(par_2000s, vec_2000s, lbl_2000s, freq_2000s,
             'Anni 2000 — Eminem, Coldplay, Taylor Swift, Linkin Park…', axes1[1])

plt.tight_layout(pad=2)
plt.savefig('word2vec_cluster.png', dpi=150, bbox_inches='tight')
print("  Salvato: word2vec_cluster.png")
plt.close()

# --- FIGURA 2: Heatmap similarità ---
print("  Generazione heatmap similarità...")
KEYWORDS = ['love', 'life', 'night', 'heart', 'god',
            'soul', 'free', 'time', 'baby', 'feel', 'world', 'dark']
kw = [p for p in KEYWORDS if p in model_70s.wv and p in model_2000s.wv]

def build_sim_matrix(model, words):
    """Matrice n×n delle similarità coseno a coppie tra le parole date (diagonale = 1)."""
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
                if abs(val) < 0.05:  # non annotare differenze trascurabili, per non affollare la cella
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

# --- FIGURA 3: Deriva semantica ---
print("  Generazione grafici deriva semantica...")
fig3, axes3 = plt.subplots(1, 2, figsize=(20, 8))
fig3.suptitle('Deriva semantica tra le due ere musicali',
              fontsize=14, fontweight='bold')

# 3a: top parole per cambiamento di contesto (da STEP 9)
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

# 3b: scatter s70 vs s2000; sopra la diagonale = coppie piu simili nei 2000s
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

# coordinate relative agli assi (0-1), non ai dati: restano nell'angolo giusto
# qualunque sia il range effettivo di lo/hi
ax_s.text(0.03, 0.95, 'più vicine\nnei 2000s', transform=ax_s.transAxes,
           fontsize=8, color='steelblue', alpha=0.8, va='top')
ax_s.text(0.75, 0.05, 'più lontane\nnei 2000s', transform=ax_s.transAxes,
           fontsize=8, color='tomato', alpha=0.8, va='bottom')

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

print("\nRiepilogo finale...")

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
