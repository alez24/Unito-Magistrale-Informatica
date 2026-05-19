# ============================================================
# LAB 4 - Modeling social media and literary language with N-grams
# TLN - Daniele Radicioni, UNITO
# ============================================================

import nltk
import re
import math
from collections import Counter
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import ngrams
from nltk.lm import MLE, Laplace
from nltk.lm.preprocessing import padded_everygram_pipeline

nltk.download('twitter_samples')
nltk.download('gutenberg')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

from nltk.corpus import twitter_samples, gutenberg, stopwords

print("Import completati!")

# ============================================================
# STEP 1: Carica i dati
# ============================================================
tweets_pos = twitter_samples.strings('positive_tweets.json')
tweets_neg = twitter_samples.strings('negative_tweets.json')
tweets_raw = tweets_pos + tweets_neg

testo_letterario_raw = gutenberg.raw('austen-emma.txt')

print(f"Tweet caricati: {len(tweets_raw)}")
print(f"Esempio positivo: {tweets_pos[0]}")
print(f"Esempio negativo: {tweets_neg[0]}")

# ============================================================
# STEP 2: Pulizia
# ============================================================
def pulisci_tweet(testo):
    testo = re.sub(r'http\S+', '', testo)
    testo = re.sub(r'@\w+', '', testo)
    testo = re.sub(r'#', '', testo)
    testo = re.sub(r'[^a-zA-Z\s]', '', testo)
    testo = testo.lower().strip()
    return testo

def pulisci_letterario(testo):
    testo = re.sub(r'[^a-zA-Z\s]', '', testo)
    testo = testo.lower().strip()
    return testo

tweets_puliti     = [pulisci_tweet(t) for t in tweets_raw]
tweets_puliti     = [t for t in tweets_puliti if len(t) > 0]
testo_lett_pulito = pulisci_letterario(testo_letterario_raw)

print("\n=== PULIZIA ===")
print(f"Tweet PRIMA: {tweets_raw[0]}")
print(f"Tweet DOPO:  {tweets_puliti[0]}")

# ============================================================
# STEP 3: Tokenizzazione
# ============================================================
testo_tweet_unito = ' '.join(tweets_puliti)
tokens_tweet = word_tokenize(testo_tweet_unito)
tokens_lett  = word_tokenize(testo_lett_pulito)

vocab_tweet_set = set(tokens_tweet)
vocab_lett_set  = set(tokens_lett)

print("\n=== TOKENIZZAZIONE ===")
print(f"Token Twitter:            {len(tokens_tweet)}")
print(f"Token Letterario:         {len(tokens_lett)}")
print(f"Parole uniche Twitter:    {len(vocab_tweet_set)}")
print(f"Parole uniche Letterario: {len(vocab_lett_set)}")

# ============================================================
# STEP 4: Stopwords removal
# ============================================================
stop = set(stopwords.words('english'))

tokens_tweet_filtrati = [t for t in tokens_tweet if t not in stop]
tokens_lett_filtrati  = [t for t in tokens_lett  if t not in stop]

bi_tweet_filtrati = Counter(ngrams(tokens_tweet_filtrati, 2))
bi_lett_filtrati  = Counter(ngrams(tokens_lett_filtrati,  2))

print("\n=== BIGRAMMI SENZA STOPWORDS ===")
print("\nTWITTER (top 10):")
for coppia, count in bi_tweet_filtrati.most_common(10):
    print(f"  {str(coppia):<35} → {count} volte")
print("\nLETTERARIO (top 10):")
for coppia, count in bi_lett_filtrati.most_common(10):
    print(f"  {str(coppia):<35} → {count} volte")

# ============================================================
# STEP 5: Analisi N-gram
# ============================================================
bi_tweet  = Counter(ngrams(tokens_tweet, 2))
bi_lett   = Counter(ngrams(tokens_lett,  2))
tri_tweet = Counter(ngrams(tokens_tweet, 3))
tri_lett  = Counter(ngrams(tokens_lett,  3))

print("\n=== BIGRAMMI CON STOPWORDS (top 10) ===")
print("TWITTER:")
for coppia, count in bi_tweet.most_common(10):
    print(f"  {str(coppia):<30} → {count} volte")
print("\nLETTERARIO:")
for coppia, count in bi_lett.most_common(10):
    print(f"  {str(coppia):<30} → {count} volte")

print("\n=== TRIGRAMMI (top 10) ===")
print("TWITTER:")
for t, c in tri_tweet.most_common(10):
    print(f"  {str(t):<42} → {c} volte")
print("\nLETTERARIO:")
for t, c in tri_lett.most_common(10):
    print(f"  {str(t):<42} → {c} volte")

# ============================================================
# STEP 6: Addestramento modelli
# ============================================================
print("\n=== ADDESTRAMENTO MODELLI ===")
n = 2

# MLE per generazione e probabilità
train_tw_mle, vocab_tw_mle = padded_everygram_pipeline(n, [tokens_tweet])
train_lt_mle, vocab_lt_mle = padded_everygram_pipeline(n, [tokens_lett])
modello_tweet = MLE(n)
modello_tweet.fit(train_tw_mle, vocab_tw_mle)
modello_lett = MLE(n)
modello_lett.fit(train_lt_mle, vocab_lt_mle)

# Laplace per perplexity
train_tw_lp, vocab_tw_lp = padded_everygram_pipeline(n, [tokens_tweet])
train_lt_lp, vocab_lt_lp = padded_everygram_pipeline(n, [tokens_lett])
modello_tweet_lp = Laplace(n)
modello_tweet_lp.fit(train_tw_lp, vocab_tw_lp)
modello_lett_lp = Laplace(n)
modello_lett_lp.fit(train_lt_lp, vocab_lt_lp)

print(f"Vocabolario Twitter:    {len(modello_tweet.vocab)} parole")
print(f"Vocabolario Letterario: {len(modello_lett.vocab)} parole")

print("\n--- PROBABILITA' CONDIZIONALI (MLE) ---")
print("\nModello TWITTER:")
print(f"  P('love'  | 'i')    = {modello_tweet.score('love',  ['i']):.4f}")
print(f"  P('wait'  | 'cant') = {modello_tweet.score('wait',  ['cant']):.4f}")
print(f"  P('happy' | 'so')   = {modello_tweet.score('happy', ['so']):.4f}")
print(f"  P('mr'    | 'said') = {modello_tweet.score('mr',    ['said']):.4f}")
print("\nModello LETTERARIO:")
print(f"  P('mr'    | 'said') = {modello_lett.score('mr',    ['said']):.4f}")
print(f"  P('been'  | 'had')  = {modello_lett.score('been',  ['had']):.4f}")
print(f"  P('love'  | 'i')    = {modello_lett.score('love',  ['i']):.4f}")
print(f"  P('wait'  | 'cant') = {modello_lett.score('wait',  ['cant']):.4f}")

# ============================================================
# STEP 7: Generazione testo
# FIX: generiamo un testo lungo e poi filtriamo le lettere
#      singole che sono artefatti del modello
# ============================================================
print("\n=== GENERAZIONE TESTO (MLE) ===")

def genera_testo(modello, n_parole=30):
    """
    Genera n_parole parole e filtra i token
    che sono lettere singole (artefatti del modello)
    """
    testo_raw = modello.generate(n_parole, random_seed=42)

    # Filtra token speciali e lettere singole (tranne 'i' e 'a')
    testo_filtrato = []
    for token in testo_raw:
        if token in ['<s>', '</s>', '<UNK>']:
            continue
        if len(token) == 1 and token not in ['i', 'a']:
            continue
        testo_filtrato.append(token)

    return ' '.join(testo_filtrato)

print("\nStile TWITTER:")
print(f"  {genera_testo(modello_tweet, 40)}")

print("\nStile LETTERARIO:")
print(f"  {genera_testo(modello_lett, 40)}")

# Confronto con parole iniziali diverse
print("\nConfronto generazione per dominio:")
for seed in [42, 99, 7, 123]:
    tw_raw  = modello_tweet.generate(15, random_seed=seed)
    lt_raw  = modello_lett.generate(15, random_seed=seed)

    tw_filt = [t for t in tw_raw  if t not in ['<s>','</s>','<UNK>'] and not (len(t)==1 and t not in ['i','a'])]
    lt_filt = [t for t in lt_raw  if t not in ['<s>','</s>','<UNK>'] and not (len(t)==1 and t not in ['i','a'])]

    print(f"\n  seed={seed}")
    print(f"    TWITTER:    {' '.join(tw_filt)}")
    print(f"    LETTERARIO: {' '.join(lt_filt)}")

# ============================================================
# STEP 8: Perplexity cross-domain
# ============================================================
print("\n=== PERPLEXITY CROSS-DOMAIN ===")

frasi_test = {
    "tw_pos_1": "i love you so much thank you",
    "tw_pos_2": "so happy right now love this",
    "tw_neg_1": "i miss you so much feel so sad",
    "tw_neg_2": "i cant stop thinking about you",
    "lett_1":   "she had been very well disposed towards him",
    "lett_2":   "it was a very good thing to have done",
    "lett_3":   "she was not a woman of many words",
    "lett_4":   "he had been very much in love with her",
}

print(f"\n{'Frase':<12} | {'PP Twitter':>10} | {'PP Lett.':>8} | Verdetto")
print("-" * 55)

corretti = 0
totale   = 0

for nome, frase in frasi_test.items():
    tokens_frase = word_tokenize(frase)
    pp_tw   = modello_tweet_lp.perplexity(tokens_frase)
    pp_lett = modello_lett_lp.perplexity(tokens_frase)

    # Normalizza per vocabolario
    pp_tw_n   = pp_tw   / len(modello_tweet_lp.vocab)
    pp_lett_n = pp_lett / len(modello_lett_lp.vocab)

    verdetto_atteso = "TW" if nome.startswith("tw") else "LT"
    verdetto        = "TW" if pp_tw_n < pp_lett_n else "LT"
    corretto        = "✓" if verdetto == verdetto_atteso else "✗"

    if verdetto == verdetto_atteso:
        corretti += 1
    totale += 1

    print(f"{nome:<12} | {pp_tw:>10.1f} | {pp_lett:>8.1f} | {verdetto} {corretto}")

print(f"\nAccuratezza classificatore: {corretti}/{totale} = {corretti/totale*100:.0f}%")

# ============================================================
# STEP 9: Classificatore con log-likelihood
# FIX: usiamo log-likelihood invece di perplexity
#      La log-likelihood misura quanto il modello "spiega"
#      il testo → più alta = più probabile per quel modello
# ============================================================
print("\n=== CLASSIFICATORE CON LOG-LIKELIHOOD ===")
print("Log-likelihood: più alta = il modello conosce meglio questo testo\n")

def log_likelihood(modello, tokens):
    """
    Calcola la log-likelihood di una sequenza.
    Più alta (meno negativa) = il modello spiega meglio il testo.
    Usiamo Laplace per evitare log(0).
    """
    score = 0.0
    for i in range(1, len(tokens)):
        contesto = [tokens[i-1]]
        parola   = tokens[i]
        prob = modello.score(parola, contesto)
        if prob > 0:
            score += math.log(prob)
        else:
            score += math.log(1e-10)  # valore piccolo per parole mai viste
    return score

def classifica_loglik(testo, mod_tw, mod_lt):
    tokens = word_tokenize(testo.lower())

    ll_tw   = log_likelihood(mod_tw,   tokens)
    ll_lett = log_likelihood(mod_lt,   tokens)

    # Più alta (meno negativa) = quel modello spiega meglio il testo
    verdetto   = "TWITTER" if ll_tw > ll_lett else "LETTERARIO"
    differenza = abs(ll_tw - ll_lett)

    print(f"  Testo: '{testo}'")
    print(f"    Log-lik Twitter:    {ll_tw:.3f}")
    print(f"    Log-lik Letterario: {ll_lett:.3f}")
    print(f"    Verdetto: {verdetto} (differenza {differenza:.2f})")
    print()

testi_classificare = [
    "i love you so much thank you",
    "she had been very well disposed towards him",
    "i miss you so much cant stop thinking",
    "it was a very good thing to have done",
    "happy birthday love you so much",
    "she was not a woman of many words",
    "i cant stop smiling so happy",
    "mr knightley had always been very fond of her",
]

for testo in testi_classificare:
    classifica_loglik(testo, modello_tweet, modello_lett)

# ============================================================
# STEP 10: MLE vs Laplace
# ============================================================
print("\n=== MLE vs LAPLACE ===")

parola_rara = "xyzword"
print(f"Parola mai vista: '{parola_rara}'")
print(f"  MLE     P = {modello_tweet.score(parola_rara, ['i']):.6f}")
print(f"  Laplace P = {modello_tweet_lp.score(parola_rara, ['i']):.6f}")

frase_rara = word_tokenize("i xyzword lol")
try:
    pp_mle = modello_tweet.perplexity(frase_rara)
except:
    pp_mle = float('inf')
pp_lap = modello_tweet_lp.perplexity(frase_rara)

print(f"\nPerplexity MLE     su frase con parola rara: {pp_mle}")
print(f"Perplexity Laplace su frase con parola rara: {pp_lap:.2f}")

# ============================================================
# STEP 11: Confronto n=1,2,3
# ============================================================
print("\n=== CONFRONTO n=1, n=2, n=3 ===")

frase_tw = word_tokenize("i love you so much thank you")
frase_lt = word_tokenize("she had been very well disposed")

for n_test in [1, 2, 3]:
    tr_tmp, voc_tmp = padded_everygram_pipeline(n_test, [tokens_tweet])
    mod_tmp = Laplace(n_test)
    mod_tmp.fit(tr_tmp, voc_tmp)

    pp_tw = mod_tmp.perplexity(frase_tw)
    pp_lt = mod_tmp.perplexity(frase_lt)

    print(f"\nn={n_test}:")
    print(f"  PP su frase Twitter:    {pp_tw:.2f}")
    print(f"  PP su frase Letterario: {pp_lt:.2f}")

# ============================================================
# STEP 12: Analisi linguistica
# ============================================================
print("\n=== ANALISI LINGUISTICA ===")

ttr_tweet = len(vocab_tweet_set) / len(tokens_tweet)
ttr_lett  = len(vocab_lett_set)  / len(tokens_lett)

print(f"\nType-Token Ratio:")
print(f"  Twitter:    {ttr_tweet:.4f}")
print(f"  Letterario: {ttr_lett:.4f}")
if ttr_tweet > ttr_lett:
    print("  → Twitter ha vocabolario più vario (slang, abbreviazioni)")

lung_tw  = [len(word_tokenize(t)) for t in tweets_raw]
frasi_lt = sent_tokenize(testo_letterario_raw)
lung_lt  = [len(word_tokenize(f)) for f in frasi_lt]

media_tw = sum(lung_tw) / len(lung_tw)
media_lt = sum(lung_lt) / len(lung_lt)

print(f"\nLunghezza media:")
print(f"  Tweet:            {media_tw:.1f} parole")
print(f"  Frase letteraria: {media_lt:.1f} parole")
print(f"  → Frasi letterarie {media_lt - media_tw:.1f} parole più lunghe in media")

# ============================================================
# STEP 13: Grafici
# ============================================================
print("\n=== GENERAZIONE GRAFICI ===")
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Lab 4 - N-gram: Twitter vs Letterario', fontsize=14)

    # Grafico 1: bigrammi Twitter
    top_tw = bi_tweet_filtrati.most_common(10)
    axes[0,0].barh([str(p) for p, _ in top_tw],
                   [c for _, c in top_tw], color='steelblue')
    axes[0,0].set_title('Top 10 bigrammi Twitter\n(senza stopwords)')
    axes[0,0].set_xlabel('Frequenza')

    # Grafico 2: bigrammi Letterario
    top_lt = bi_lett_filtrati.most_common(10)
    axes[0,1].barh([str(p) for p, _ in top_lt],
                   [c for _, c in top_lt], color='coral')
    axes[0,1].set_title('Top 10 bigrammi Letterario\n(senza stopwords)')
    axes[0,1].set_xlabel('Frequenza')

    # Grafico 3: log-likelihood classificatore
    testi_graf = [
        ("i love you so much",           "TW", "steelblue"),
        ("i miss you feel so sad",        "TW", "steelblue"),
        ("she had been very well",        "LT", "coral"),
        ("it was a very good thing",      "LT", "coral"),
    ]

    ll_tw_vals   = []
    ll_lett_vals = []
    labels_graf  = []
    colori_graf  = []

    for testo, tipo, col in testi_graf:
        tok = word_tokenize(testo.lower())
        ll_tw_vals.append(log_likelihood(modello_tweet, tok))
        ll_lett_vals.append(log_likelihood(modello_lett, tok))
        labels_graf.append(f"{tipo}: {testo[:20]}")
        colori_graf.append(col)

    x = range(len(labels_graf))
    w = 0.35
    bars1 = axes[1,0].bar([i - w/2 for i in x], ll_tw_vals,
                          w, label='Log-lik Twitter', color='steelblue', alpha=0.7)
    bars2 = axes[1,0].bar([i + w/2 for i in x], ll_lett_vals,
                          w, label='Log-lik Letterario', color='coral', alpha=0.7)
    axes[1,0].set_xticks(list(x))
    axes[1,0].set_xticklabels(labels_graf, rotation=15, ha='right', fontsize=8)
    axes[1,0].set_title('Log-likelihood per testo\n(meno negativo = più probabile)')
    axes[1,0].set_ylabel('Log-likelihood')
    axes[1,0].legend()

    # Grafico 4: TTR e lunghezza frasi
    categorie_bar = ['TTR (x100)', 'Lung. media frasi']
    tw_bars  = [ttr_tweet * 100, media_tw]
    lt_bars  = [ttr_lett  * 100, media_lt]

    x2 = range(len(categorie_bar))
    axes[1,1].bar([i - w/2 for i in x2], tw_bars,
                  w, label='Twitter', color='steelblue', alpha=0.7)
    axes[1,1].bar([i + w/2 for i in x2], lt_bars,
                  w, label='Letterario', color='coral', alpha=0.7)
    axes[1,1].set_xticks(list(x2))
    axes[1,1].set_xticklabels(categorie_bar)
    axes[1,1].set_title('TTR e lunghezza media frasi')
    axes[1,1].legend()

    plt.tight_layout()
    plt.savefig('analisi_ngram.png', dpi=150, bbox_inches='tight')
    print("Grafico salvato come 'analisi_ngram.png'")

except ImportError:
    print("Installa matplotlib con: pip install matplotlib")

# ============================================================
# STEP 14: Riepilogo
# ============================================================
print("\n=== RIEPILOGO FINALE ===")

print(f"\nDataset:")
print(f"  Twitter:    {len(tweets_raw)} tweet (5000 pos + 5000 neg)")
print(f"  Letterario: Emma by Jane Austen (1816)")

print(f"\nVocabolario:")
print(f"  Twitter:    {len(vocab_tweet_set)} parole uniche")
print(f"  Letterario: {len(vocab_lett_set)} parole uniche")

print(f"\nTTR: Twitter={ttr_tweet:.4f}, Letterario={ttr_lett:.4f}")
print(f"Lunghezza media: Tweet={media_tw:.1f}, Letterario={media_lt:.1f}")

print(f"\nModelli:")
print(f"  MLE     → generazione testo e probabilità condizionali")
print(f"  Laplace → perplexity (gestisce parole mai viste)")
print(f"  Log-lik → classificatore (più stabile di perplexity)")

print("\nLab completato!")