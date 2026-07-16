# LAB 4 - Modeling social media and literary language with N-grams
# TLN - Daniele Radicioni, UNITO

import nltk
import re
import math
from collections import Counter
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import ngrams
from nltk.lm import MLE, Laplace
from nltk.lm.preprocessing import padded_everygram_pipeline, pad_both_ends
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')


nltk.download('twitter_samples')
nltk.download('gutenberg')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

from nltk.corpus import twitter_samples, gutenberg, stopwords

print("Import completati!")

# due domini a confronto: social (breve/informale) vs letterario (lungo/formale)
tweets_pos = twitter_samples.strings('positive_tweets.json')
tweets_neg = twitter_samples.strings('negative_tweets.json')
tweets_raw = tweets_pos + tweets_neg

testo_letterario_raw = gutenberg.raw('austen-emma.txt')

print(f"Tweet caricati: {len(tweets_raw)}")
print(f"Esempio positivo: {tweets_pos[0]}")
print(f"Esempio negativo: {tweets_neg[0]}")

#pulizia del testo
def pulisci_tweet(testo):
    """Rimuove URL, menzioni e hashtag, che distorcerebbero le frequenze degli n-grammi."""
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
tweets_puliti     = [t for t in tweets_puliti if len(t) > 0]  # scarta i tweet svuotati dalla pulizia (es. solo URL/menzioni) altrimenti li tiene se lunghezza > 0
testo_lett_pulito = pulisci_letterario(testo_letterario_raw)


print("\n=== PULIZIA ===")
print(f"Tweet PRIMA: {tweets_raw[0]}")
print(f"Tweet DOPO:  {tweets_puliti[0]}")

<<<<<<< HEAD
testo_tweet_unito = ' '.join(tweets_puliti) #prendiamo i testi e li tokenizziamo in singole parole  che vengono unite in un listone di parole --- questo è il grezzo che ci serve solo per contare nella funzione len nel print f
tokens_tweet = word_tokenize(testo_tweet_unito)
tokens_lett  = word_tokenize(testo_lett_pulito)

vocab_tweet_set = set(tokens_tweet)# set elimina i duplicati
vocab_lett_set  = set(tokens_lett)

# sequenze separate (un tweet/una frase = una sequenza) per l'addestramento: servono a non far attraversare i bigrammi tra un tweet/frase e il successivo
sequenze_tweet = [word_tokenize(t) for t in tweets_puliti]#prendiamo tweet puliti e creiamo lista di liste dei tweet tokenizzati 
frasi_lett_raw = sent_tokenize(testo_letterario_raw)#funzione natia nltk che considera le frasi in base alle stopword per poi creare una liste di liste formate dalle frasi del testo letterario 
sequenze_lett  = [word_tokenize(pulisci_letterario(f)) for f in frasi_lett_raw]#sequenze_lett tokenizza il testo letterario scomposto in lista di liste
sequenze_lett  = [s for s in sequenze_lett if s]#iterazione del processo
=======

testo_tweet_unito = ' '.join(tweets_puliti) 
tokens_tweet = word_tokenize(testo_tweet_unito)
tokens_lett  = word_tokenize(testo_lett_pulito)
vocab_tweet_set = set(tokens_tweet) 
vocab_lett_set  = set(tokens_lett)



# sequenze separate (un tweet/una frase = una sequenza) per l'addestramento: servono
# a non far attraversare i bigrammi tra un tweet/frase e il successivo
sequenze_tweet = [word_tokenize(t) for t in tweets_puliti]
frasi_lett_raw = sent_tokenize(testo_letterario_raw)
sequenze_lett  = [word_tokenize(pulisci_letterario(f)) for f in frasi_lett_raw]
sequenze_lett  = [s for s in sequenze_lett if s]
>>>>>>> 69016fbaa8a1f0aa2f1e61b3924ff8442b0c7e13

print("\n=== TOKENIZZAZIONE ===")
print(f"Token Twitter:            {len(tokens_tweet)}")#len conta i singoli token dalla divisione grezza
print(f"Token Letterario:         {len(tokens_lett)}")
print(f"Parole uniche Twitter:    {len(vocab_tweet_set)}")
print(f"Parole uniche Letterario: {len(vocab_lett_set)}")

stop = set(stopwords.words('english'))#rimozione stopword dal testo

tokens_tweet_filtrati = [t for t in tokens_tweet if t not in stop]#salviamo i token ripuliti dalle stopword
tokens_lett_filtrati  = [t for t in tokens_lett  if t not in stop]

# senza stopword: piu informativi sui temi ricorrenti
bi_tweet_filtrati = Counter(ngrams(tokens_tweet_filtrati, 2))#conta le apparizioni dei diversi bigrammi nel testo filtrato
bi_lett_filtrati  = Counter(ngrams(tokens_lett_filtrati,  2))

print("\n=== BIGRAMMI SENZA STOPWORDS ===")#dati rilevati dall'estrazione dei bigrammi puliti dalle stopwords
print("\nTWITTER (top 10):")
for coppia, count in bi_tweet_filtrati.most_common(10):
    print(f"  {str(coppia):<35} → {count} volte")
print("\nLETTERARIO (top 10):")
for coppia, count in bi_lett_filtrati.most_common(10):
    print(f"  {str(coppia):<35} → {count} volte")

# stessa estrazione sul testo integrale con le stopwords, per confrontare lo stile sintattico
bi_tweet  = Counter(ngrams(tokens_tweet, 2))#bigrammi
bi_lett   = Counter(ngrams(tokens_lett,  2))
tri_tweet = Counter(ngrams(tokens_tweet, 3))#trigrammi
tri_lett  = Counter(ngrams(tokens_lett,  3))

print("\n=== BIGRAMMI CON STOPWORDS (top 10) ===")#dati rilevati dall'estrazione dei bigrammi non puliti dalle stopwords
print("TWITTER:")
for coppia, count in bi_tweet.most_common(10):
    print(f"  {str(coppia):<30} → {count} volte")
print("\nLETTERARIO:")
for coppia, count in bi_lett.most_common(10):
    print(f"  {str(coppia):<30} → {count} volte")

print("\n=== TRIGRAMMI (top 10) ===")#dati rilevati dall'estrazione dei bigrammi non puliti dalle stopwords
print("TWITTER:")
for t, c in tri_tweet.most_common(10):
    print(f"  {str(t):<42} → {c} volte")
print("\nLETTERARIO:")
for t, c in tri_lett.most_common(10):
    print(f"  {str(t):<42} → {c} volte")

print("\n=== ADDESTRAMENTO MODELLI ===")
n = 2  # ordine del modello: n=2 -> bigrammi, P(parola | 1 parola di contesto)

# aggiunge i marcatori <s>/</s> di padding per ogni sequenza e genera gli n-grammi ( da 1 a n=2 ) per l'addestramento del modello 
train_tw_mle, vocab_tw_mle = padded_everygram_pipeline(n, sequenze_tweet)
train_lt_mle, vocab_lt_mle = padded_everygram_pipeline(n, sequenze_lett)
modello_tweet = MLE(n)#stima la prob condizionata alla frequenza relativa stimata nel corpus
modello_tweet.fit(train_tw_mle, vocab_tw_mle)
modello_lett = MLE(n)
modello_lett.fit(train_lt_mle, vocab_lt_mle)

# rigenerata per Laplace: i generatori Python si esauriscono dopo il primo uso
train_tw_lp, vocab_tw_lp = padded_everygram_pipeline(n, sequenze_tweet)
train_lt_lp, vocab_lt_lp = padded_everygram_pipeline(n, sequenze_lett)

modello_tweet_lp = Laplace(n)  # Laplace: aggiunge +1 fittizio al numeratore e al denominatore cardinalità univoca del vocabolario a ogni conteggio (smoothing)
modello_tweet_lp.fit(train_tw_lp, vocab_tw_lp)
modello_lett_lp = Laplace(n)
modello_lett_lp.fit(train_lt_lp, vocab_lt_lp)

print(f"Vocabolario Twitter:    {len(modello_tweet.vocab)} parole")  #risultati del fitting sul modello, includendo i token di padding
print(f"Vocabolario Letterario: {len(modello_lett.vocab)} parole")

# .score(parola, [contesto]) = P(parola | contesto), stimata dalle frequenze osservate
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

print("\n=== GENERAZIONE TESTO (MLE) ===")#grazie alle prob ottenute dalla mle del modello basandosi sui bigrammi visti in addestramento

def genera_testo(modello, n_parole=30):
    """Campiona n_parole token dal modello e rimuove gli artefatti tipici dei bigrammi (padding, lettere isolate)."""
    testo_raw = modello.generate(n_parole, random_seed=42)

    testo_filtrato = []
    for token in testo_raw:
        if token in ['<s>', '</s>', '<UNK>']:
            continue
        if len(token) == 1 and token not in ['i', 'a']: #eccezione per la i e la nella pulizia della frase
            continue
        testo_filtrato.append(token)

    return ' '.join(testo_filtrato) #costruzione della frase pulita

print("\nStile TWITTER:")
print(f"  {genera_testo(modello_tweet, 40)}")#

print("\nStile LETTERARIO:")
print(f"  {genera_testo(modello_lett, 40)}")

# seed diversi = campioni diversi dello stesso stile
print("\nConfronto generazione per dominio:")
for seed in [42, 99, 7, 123]: 
    tw_raw  = modello_tweet.generate(15, random_seed=seed)
    lt_raw  = modello_lett.generate(15, random_seed=seed)

    tw_filt = [t for t in tw_raw  if t not in ['<s>','</s>','<UNK>'] and not (len(t)==1 and t not in ['i','a'])]
    lt_filt = [t for t in lt_raw  if t not in ['<s>','</s>','<UNK>'] and not (len(t)==1 and t not in ['i','a'])]

    print(f"\n  seed={seed}")
    print(f"    TWITTER:    {' '.join(tw_filt)}")
    print(f"    LETTERARIO: {' '.join(lt_filt)}")

print("\n=== PERPLEXITY CROSS-DOMAIN ===")#confrontiamo il modello tweetter e il modello letterario su delle frasi prestabilite per valutarne la perplexity dei modelli

def calcola_perplexity(modello, tokens, n=2):
    """perplexity() si aspetta n-grammi (tuple), non token grezzi: senza questa conversione
    indicizza per errore i caratteri delle stringhe invece di calcolare probabilita' reali."""
    ngr = list(ngrams(pad_both_ends(tokens, n=n), n))#fai padding sulle frasi pre-impostate, dopodichè crea n-grammi con n= 2
    return modello.perplexity(ngr)#calcolo della perplexity dei bi-grammi creati con la funzione ngrams sul modello con smoohing di laplace

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
    tokens_frase = word_tokenize(frase) #tokenizzazione frasi pre impostate
    # perplexity bassa = frase piu prevedibile per quel dominio
    pp_tw   = calcola_perplexity(modello_tweet_lp, tokens_frase, n)#calcola la perplexiy dei modelli di laplace sulle frasi pre-impostate, n = 2 lunghezza degli n-grammi
    pp_lett = calcola_perplexity(modello_lett_lp, tokens_frase, n)

    # normalizzazione empirica per |vocabolario| per consentire un confronto tra i dati coerente alle grandezze dei vocabolari(la perplexity e' gia' normalizzata
    # per token: dividere anche per |V| non e' prassi standard, ma qui serve a rendere
    # confrontabili domini con vocabolari di dimensione molto diversa)
    pp_tw_n   = pp_tw   / len(modello_tweet_lp.vocab)
    pp_lett_n = pp_lett / len(modello_lett_lp.vocab)

    verdetto_atteso = "TW" if nome.startswith("tw") else "LT" #expectation
    verdetto        = "TW" if pp_tw_n < pp_lett_n else "LT"   #predizione
    corretto        = "✓" if verdetto == verdetto_atteso else "✗" #etichetta congrua a predizione
    if verdetto == verdetto_atteso:
        corretti += 1
    totale += 1

    print(f"{nome:<12} | {pp_tw:>10.1f} | {pp_lett:>8.1f} | {verdetto} {corretto}")

print(f"\nAccuratezza classificatore: {corretti}/{totale} = {corretti/totale*100:.0f}%")

print("\n=== CLASSIFICATORE CON LOG-LIKELIHOOD ===")
print("Log-likelihood: più alta = il modello conosce meglio questo testo\n")

def log_likelihood(modello, tokens):
    """Log-probabilità media per token (somma dei log dei bigrammi, divisa per il numero di transizioni):
    più alta (meno negativa) = modello migliore. Richiede un modello con smoothing (Laplace): con MLE
    ogni bigramma mai visto avrebbe probabilita' 0 e dominerebbe la somma tramite il backoff sotto."""
    score = 0.0

    # catena di Markov di ordine 1: ogni parola dipende solo dalla precedente
    for i in range(1, len(tokens)):
        contesto = [tokens[i-1]]# prendo la parola prima della i-esima parola token
        parola   = tokens[i]#prende il token nella i-esima posizione
        prob = modello.score(parola, contesto)# assegno uno scor alla dupla di parola e contesto secondo il modello addestrato
        if prob > 0:
            score += math.log(prob)#log della probabilità
        else:
            # backoff di sicurezza: con Laplace non dovrebbe mai attivarsi (score sempre maggiore 0)
            score += math.log(1e-10)# lo riempiamo di rumore pur di non avere uno zero nel rapporto
    return score / (len(tokens) - 1)#aggiorna il valore score che sarà il punteggio di probabilità lewgato alla frase i-esima nel ciclo delle frasi analizzate con uno score medio calcolato su tutti i bigrammi-1 della frase

def classifica_loglik(testo, mod_tw, mod_lt):
    """Assegna il testo al dominio (Twitter o Letterario) il cui modello lo spiega meglio."""
    tokens = word_tokenize(testo.lower())
    ll_tw   = log_likelihood(mod_tw,   tokens)
    ll_lett = log_likelihood(mod_lt,   tokens)

    verdetto   = "TWITTER" if ll_tw > ll_lett else "LETTERARIO"  # vince il punteggio più alto (meno negativo)
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
    classifica_loglik(testo, modello_tweet_lp, modello_lett_lp)

print("\n=== MLE vs LAPLACE ===")

# Confronto diretto sullo stesso caso limite: una parola mai vista in training.
parola_rara = "xyzword"
print(f"Parola mai vista: '{parola_rara}'")
print(f"  MLE     P = {modello_tweet.score(parola_rara, ['i']):.6f}")   # 0 esatto: MLE non generalizza oltre i dati osservati
print(f"  Laplace P = {modello_tweet_lp.score(parola_rara, ['i']):.6f}")  # > 0 grazie allo smoothing

# MLE: parola ignota -> probabilità zero -> perplexity infinita
frase_rara = word_tokenize("i xyzword lol")
pp_mle = calcola_perplexity(modello_tweet, frase_rara, n)
pp_lap = calcola_perplexity(modello_tweet_lp, frase_rara, n)  # Laplace regge il calcolo grazie allo smoothing

print(f"\nPerplexity MLE     su frase con parola rara: {pp_mle}")
print(f"Perplexity Laplace su frase con parola rara: {pp_lap:.2f}")

print("\n=== CONFRONTO n=1, n=2, n=3 ===")

frase_tw = word_tokenize("i love you so much thank you")   # tipica frase Twitter
frase_lt = word_tokenize("she had been very well disposed")  # tipica frase letteraria

# n crescente = modello piu specifico: la PP letteraria cresce piu in fretta di quella Twitter
for n_test in [1, 2, 3]:
    tr_tmp, voc_tmp = padded_everygram_pipeline(n_test, sequenze_tweet)
    mod_tmp = Laplace(n_test)  # Laplace necessario: la frase letteraria contiene n-grammi mai visti in questo training
    mod_tmp.fit(tr_tmp, voc_tmp)

    pp_tw = calcola_perplexity(mod_tmp, frase_tw, n_test)
    pp_lt = calcola_perplexity(mod_tmp, frase_lt, n_test)

    print(f"\nn={n_test}:")
    print(f"  PP su frase Twitter:    {pp_tw:.2f}")
    print(f"  PP su frase Letterario: {pp_lt:.2f}")

print("\n=== ANALISI LINGUISTICA ===")

# TTR (type token ratio) = parole uniche / parole totali: più alto = vocabolario più vario2
N = min(len(tokens_tweet), len(tokens_lett))
ttr_tweet = len(set(tokens_tweet[:N])) / N
ttr_lett  = len(set(tokens_lett[:N]))  / N

print(f"\nType-Token Ratio (su campioni di {N} token):")
print(f"  Twitter:    {ttr_tweet:.4f}")
print(f"  Letterario: {ttr_lett:.4f}")
if ttr_tweet > ttr_lett:
    print("  → Twitter ha vocabolario più vario (slang, abbreviazioni)")
else:
    print("  → Letterario ha vocabolario più vario a parità di token campionati")

# lunghezza media: tweet interi vs frasi del romanzo (sent_tokenize)
lung_tw  = [len(word_tokenize(t)) for t in tweets_raw]
lung_lt  = [len(word_tokenize(f)) for f in frasi_lett_raw]

media_tw = sum(lung_tw) / len(lung_tw)
media_lt = sum(lung_lt) / len(lung_lt)

print(f"\nLunghezza media:")
print(f"  Tweet:            {media_tw:.1f} parole")
print(f"  Frase letteraria: {media_lt:.1f} parole")
print(f"  → Frasi letterarie {media_lt - media_tw:.1f} parole più lunghe in media")

print("\n=== GENERAZIONE GRAFICI AVANZATI ===")
try:
    c_tw = '#2980b9'
    c_lt = '#e67e22'

    fig, axes = plt.subplots(2, 2, figsize=(16, 13), facecolor='#f8f9fa')
    fig.suptitle('Analisi Comparativa N-Gram: Twitter vs Dominio Letterario',
                 fontsize=16, fontweight='bold', color='#1a252f', y=0.98)

    # --- Grafico 1: top bigrammi Twitter ---
    top_tw = bi_tweet_filtrati.most_common(10)[::-1]  # invertito: il più frequente in alto
    y_labels_tw = [f"{p[0]} {p[1]}" for p, _ in top_tw]
    counts_tw = [c for _, c in top_tw]

    bars_tw = axes[0,0].barh(y_labels_tw, counts_tw, color=c_tw, alpha=0.85, height=0.6)
    axes[0,0].set_title('Top 10 Bigrammi: Twitter\n(Senza Stopwords)', fontsize=12, fontweight='bold', pad=10)
    axes[0,0].set_xlabel('Frequenza Assoluta', fontsize=10)
    axes[0,0].grid(axis='x', linestyle='--', alpha=0.5)
    axes[0,0].bar_label(bars_tw, padding=5, fontsize=9, color='#475569')

    # --- Grafico 2: top bigrammi letterari ---
    top_lt = bi_lett_filtrati.most_common(10)[::-1]
    y_labels_lt = [f"{p[0]} {p[1]}" for p, _ in top_lt]
    counts_lt = [c for _, c in top_lt]

    bars_lt = axes[0,1].barh(y_labels_lt, counts_lt, color=c_lt, alpha=0.85, height=0.6)
    axes[0,1].set_title('Top 10 Bigrammi: Romanzo (Emma)\n(Senza Stopwords)', fontsize=12, fontweight='bold', pad=10)
    axes[0,1].set_xlabel('Frequenza Assoluta', fontsize=10)
    axes[0,1].grid(axis='x', linestyle='--', alpha=0.5)
    axes[0,1].bar_label(bars_lt, padding=5, fontsize=9, color='#475569')

    # --- Grafico 3: log-likelihood a confronto (barre affiancate) ---
    testi_graf = [
        ("i love you so much",           "TW"),
        ("i miss you feel so sad",        "TW"),
        ("she had been very well",        "LT"),
        ("it was a very good thing",      "LT"),
    ]

    ll_tw_vals = []
    ll_lett_vals = []
    labels_graf = []

    for testo, tipo in testi_graf:
        tok = word_tokenize(testo.lower())
        ll_tw_vals.append(log_likelihood(modello_tweet_lp, tok))
        ll_lett_vals.append(log_likelihood(modello_lett_lp, tok))
        labels_graf.append(f"[{tipo}] {testo}")

    x = np.arange(len(labels_graf))
    w = 0.35

    axes[1,0].bar(x - w/2, ll_tw_vals, w, label='Modello Twitter', color=c_tw, alpha=0.85)
    axes[1,0].bar(x + w/2, ll_lett_vals, w, label='Modello Letterario', color=c_lt, alpha=0.85)

    axes[1,0].set_xticks(x)
    axes[1,0].set_xticklabels(labels_graf, rotation=12, ha='right', fontsize=9)
    axes[1,0].set_title('Log-Likelihood Cross-Domain\n(Barre più vicine allo 0 in alto = Modello Vincente)', fontsize=12, fontweight='bold', pad=10)
    axes[1,0].set_ylabel('Log-Likelihood', fontsize=10)
    axes[1,0].grid(axis='y', linestyle='--', alpha=0.5)
    axes[1,0].legend(frameon=True, facecolor='#ffffff', edgecolor='none')
    axes[1,0].set_ylim(top=0)

    # --- Grafico 4: TTR e lunghezza media, doppio asse Y ---
    categorie = ['Twitter (Social)', 'Letterario (Austen)']
    ttr_vals = [ttr_tweet, ttr_lett]
    lung_vals = [media_tw, media_lt]

    x2 = np.arange(len(categorie))

    color_ttr = '#16a085'
    axes[1,1].bar(x2 - 0.2, ttr_vals, 0.35, label='Type-Token Ratio (TTR)', color=color_ttr, alpha=0.8)
    axes[1,1].set_ylabel('Richiesta Lessicale (TTR)', color=color_ttr, fontweight='bold')
    axes[1,1].tick_params(axis='y', labelcolor=color_ttr)
    axes[1,1].set_ylim(0, max(ttr_vals) * 1.2)

    ax4_twin = axes[1,1].twinx()  # secondo asse Y: le due metriche hanno scale molto diverse
    color_lung = '#8e44ad'
    ax4_twin.bar(x2 + 0.2, lung_vals, 0.35, label='Lunghezza Media Frase', color=color_lung, alpha=0.8)
    ax4_twin.set_ylabel('Lunghezza Media Frase (Parole)', color=color_lung, fontweight='bold')
    ax4_twin.tick_params(axis='y', labelcolor=color_lung)
    ax4_twin.set_ylim(0, max(lung_vals) * 1.2)

    axes[1,1].set_xticks(x2)
    axes[1,1].set_xticklabels(categorie, fontsize=10, fontweight='bold')
    axes[1,1].set_title('Metriche Linguistiche Strutturali a Confronto', fontsize=12, fontweight='bold', pad=10)

    lines1, labels1 = axes[1,1].get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    axes[1,1].legend(lines1 + lines2, labels1 + labels2, loc='upper center', frameon=True, facecolor='#ffffff')

    for ax in axes.flat:
        ax.set_facecolor('#ffffff')
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        ax.spines['left'].set_color('#bdc3c7')
        ax.spines['bottom'].set_color('#bdc3c7')

    cartella_script = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.'
    percorso_salvataggio = os.path.join(cartella_script, 'confronto_risultati_laboratorio.png')

    plt.tight_layout()
    plt.savefig(percorso_salvataggio, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"Grafico salvato con successo in: {percorso_salvataggio}")

except Exception as e:
    print(f"Errore durante la generazione del grafico dello Step 13: {e}")

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
