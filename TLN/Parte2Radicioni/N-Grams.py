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
import numpy as np           
import matplotlib                  
import matplotlib.pyplot as plt
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


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
#caricamento dati positivi e negativi da twitter, estraendo i testi dal file JSON e restituendo una lista di stringhe (una stringa per ogni tweet)
tweets_pos = twitter_samples.strings('positive_tweets.json')
tweets_neg = twitter_samples.strings('negative_tweets.json')
tweets_raw = tweets_pos + tweets_neg #unione delle due liste

testo_letterario_raw = gutenberg.raw('austen-emma.txt') #accede al corpus gutenberg , restituendo un unica maxi stringa contenente l'intero libro

#stampa a schermo : n, totale di tweet, primo tweet positivo, primo tweet neggativo
print(f"Tweet caricati: {len(tweets_raw)}")
print(f"Esempio positivo: {tweets_pos[0]}")
print(f"Esempio negativo: {tweets_neg[0]}")

# ============================================================
# STEP 2: Pulizia
# ============================================================
#funzione specifica di pulizia dei tweet. Eliminando elementi social ch distorcono le frequenze degli N-grammi
def pulisci_tweet(testo):
    testo = re.sub(r'http\S+', '', testo)
    testo = re.sub(r'@\w+', '', testo)
    testo = re.sub(r'#', '', testo)
    testo = re.sub(r'[^a-zA-Z\s]', '', testo)
    testo = testo.lower().strip()
    return testo
#Funzione di pulizia del testo classico.
def pulisci_letterario(testo):
    testo = re.sub(r'[^a-zA-Z\s]', '', testo)
    testo = testo.lower().strip()
    return testo

tweets_puliti     = [pulisci_tweet(t) for t in tweets_raw] #Usa una List Comprehension per ciclare su ogni singolo tweet della lista 'tweets_raw', passarlo alla funzione 'pulisci_tweet' e salvare il risultato in una nuova lista 'tweets_puliti'.
tweets_puliti     = [t for t in tweets_puliti if len(t) > 0] # Filtro di sicurezza: elimina dalla lista i tweet che, dopo la pulizia, sono rimasti completamente vuoti
testo_lett_pulito = pulisci_letterario(testo_letterario_raw) #applica la pulizia mirata al testo letterario

print("\n=== PULIZIA ===")
print(f"Tweet PRIMA: {tweets_raw[0]}")#stampa a schermo il tweet originale
print(f"Tweet DOPO:  {tweets_puliti[0]}")#stampa a schermo il tweet pulito

# ============================================================
# STEP 3: Tokenizzazione
# ============================================================
testo_tweet_unito = ' '.join(tweets_puliti)#unisce tutte le stringhe della lista dei tweet_puliti in un unica maxi stringa e le divide esclusivamente da uno spazio
tokens_tweet = word_tokenize(testo_tweet_unito)# prende la mega stringa restituendo una lista di token
tokens_lett  = word_tokenize(testo_lett_pulito)# prende la stringa del testo letterario e restituisce una stringa di token

#set : struttura dati che elimina i duplicati, creando gli insiemi delle parole uniche per entrambe i tipi di testo
vocab_tweet_set = set(tokens_tweet)
vocab_lett_set  = set(tokens_lett)

print("\n=== TOKENIZZAZIONE ===")
print(f"Token Twitter:            {len(tokens_tweet)}")#numero totale di token dei tweet
print(f"Token Letterario:         {len(tokens_lett)}")#numero totale dei token letterario
print(f"Parole uniche Twitter:    {len(vocab_tweet_set)}")#numero parole uniche di twitter
print(f"Parole uniche Letterario: {len(vocab_lett_set)}")#numero parole uniche letterario

# ============================================================
# STEP 4: Stopwords removal
# ============================================================
#rimozione delle stopword riconosciute dal vocabolario inglese
stop = set(stopwords.words('english'))

tokens_tweet_filtrati = [t for t in tokens_tweet if t not in stop]#filtra la lista dei token usando una list comprehension, conserva la t-esima parola solo se NON è stopwword
tokens_lett_filtrati  = [t for t in tokens_lett  if t not in stop]

#costruzione dei bi-grammi (coppie consecutive sensate di parole) senza stopwords
bi_tweet_filtrati = Counter(ngrams(tokens_tweet_filtrati, 2))
bi_lett_filtrati  = Counter(ngrams(tokens_lett_filtrati,  2))


#stampa dei risultati
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
#estrazione e conteggio dei bi-grammi mantenendo il testo originale (con tutte le stopwords presenti)
bi_tweet  = Counter(ngrams(tokens_tweet, 2))
bi_lett   = Counter(ngrams(tokens_lett,  2))
#estrazione e conteggio dei tri-grammi mantenendo il testo originale (con tutte le stopwords presenti)
tri_tweet = Counter(ngrams(tokens_tweet, 3))
tri_lett  = Counter(ngrams(tokens_lett,  3))


#stampa e confronto dei bigrammi integrali per effettuare un confronto tra tipologia di testi
print("\n=== BIGRAMMI CON STOPWORDS (top 10) ===")
print("TWITTER:")
for coppia, count in bi_tweet.most_common(10):
    print(f"  {str(coppia):<30} → {count} volte")
print("\nLETTERARIO:")
for coppia, count in bi_lett.most_common(10):
    print(f"  {str(coppia):<30} → {count} volte")

#stampa e confronto dei trigrammi integrali per effettuare un confronto tra tipologia di testi
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
#definisce l'ordine del modello di linguaggio, n=2 crea un modello a bigrammi, ovvero la probabilità di una parola diopende esclusivamente da una parola precedente
n = 2
#addestramento modelli MLE (maximum likelihood estimation) per generazione e probabilità
#padded_everygram_pipeline genera i token di padding e calcola bigrammi e unigrammi necessari, restituisce il testo strutturato per l'addestramento (train_tw_mle) e l'oggetto vocabolario complessivo (vocab_tw_mle)
train_tw_mle, vocab_tw_mle = padded_everygram_pipeline(n, [tokens_tweet])
train_lt_mle, vocab_lt_mle = padded_everygram_pipeline(n, [tokens_lett])
modello_tweet = MLE(n)#iniziallizza il modello, impostando l'ordinen= x ( dalla prima riga dello step 6)
modello_tweet.fit(train_tw_mle, vocab_tw_mle)# Addestra il modello accoppiando le sequenze di parole estratte al rispettivo vocabolario
modello_lett = MLE(n)
modello_lett.fit(train_lt_mle, vocab_lt_mle)

# addestramento modello laplace
# NOTA: Ricreiamo la pipeline perché i generatori in Python si consumano dopo il primo utilizzo
train_tw_lp, vocab_tw_lp = padded_everygram_pipeline(n, [tokens_tweet])
train_lt_lp, vocab_lt_lp = padded_everygram_pipeline(n, [tokens_lett])

# Inizializza il modello Laplace, aggiunge fittiziamente +1 a tutti i conteggi.
modello_tweet_lp = Laplace(n)
modello_tweet_lp.fit(train_tw_lp, vocab_tw_lp)
modello_lett_lp = Laplace(n)
modello_lett_lp.fit(train_lt_lp, vocab_lt_lp)

#controllo dimensione vocabolario (Nota: .vocab contiene anche i token speciali di padding aggiunti dalla pipeline)
print(f"Vocabolario Twitter:    {len(modello_tweet.vocab)} parole")
print(f"Vocabolario Letterario: {len(modello_lett.vocab)} parole")

# CALCOLO DELLE PROBABILITA' CONDIZIONALI 
# .score('parola_target', ['contesto']) calcola la probabilità condizionale empirica P(parola_target | contesto)
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
    Funzione ausiliaria che interroga il modello, genera una sequenza casuale
    di parole (basata sulle probabilità apprese) e ripulisce l'output 
    dai tecnicismi algoritmici per renderlo leggibile.
    """
    #.generate() avvia il campionamento statistico autoregressivo -> genera 'n_parole' stringhe consecutive basandosi sulle distribuzioni di frequenza MLE
    # il random_seed garantisce la riproducibilità ad ogni esecuzione
    testo_raw = modello.generate(n_parole, random_seed=42)

    # Filtraggio post-generazione
    testo_filtrato = []
    for token in testo_raw:
        #se il modello da in output i token tra le parentesi quadre, li ignora e passa oltre per non sporcare la frase
        if token in ['<s>', '</s>', '<UNK>']:
            continue
        #filtro per gli artefatti :se il token è lungo 1 solo carattere, ma NON è il pronome "i" o l'articolo "a", viene scartato. Casistica frequente nei modelli bi-grammi
        if len(token) == 1 and token not in ['i', 'a']:
            continue
        #se il token supera tutti i controlli viene inserito nella lista finale
        testo_filtrato.append(token)

    return ' '.join(testo_filtrato)#unisce la lista di parole filtrate in un'unica stringa leggibile

#GENERAZIONE DEI DUE STILI
print("\nStile TWITTER:")
print(f"  {genera_testo(modello_tweet, 40)}")

print("\nStile LETTERARIO:")
print(f"  {genera_testo(modello_lett, 40)}")

# Confronto con parole iniziali diverse, modificando i seed si obbliga il modello a prendere strade probabilistiche differenti
print("\nConfronto generazione per dominio:")
for seed in [42, 99, 7, 123]:
    #genera 15 parole usando il seed del ciclo corrente
    tw_raw  = modello_tweet.generate(15, random_seed=seed)
    lt_raw  = modello_lett.generate(15, random_seed=seed)

    #applica lo stesso filtro di rimozione di simboli di padding e lettere singole
    tw_filt = [t for t in tw_raw  if t not in ['<s>','</s>','<UNK>'] and not (len(t)==1 and t not in ['i','a'])]
    lt_filt = [t for t in lt_raw  if t not in ['<s>','</s>','<UNK>'] and not (len(t)==1 and t not in ['i','a'])]
    
    #stampa dei risultati
    print(f"\n  seed={seed}")
    print(f"    TWITTER:    {' '.join(tw_filt)}")
    print(f"    LETTERARIO: {' '.join(lt_filt)}")

# ============================================================
# STEP 8: Perplexity cross-domain
# ============================================================
print("\n=== PERPLEXITY CROSS-DOMAIN ===")

#definisce un dizionario di fase di test
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

#stampa l'intestaztione della tabella di output per incolonnare i risultati
print(f"\n{'Frase':<12} | {'PP Twitter':>10} | {'PP Lett.':>8} | Verdetto")
print("-" * 55)

#inizializza i contatori per calcolare l'accuratezza finale del sistema come classificatore
corretti = 0
totale   = 0

#cicla su ogni frase del dizionario di test
for nome, frase in frasi_test.items():
    #tokenizza la frase corrente
    tokens_frase = word_tokenize(frase)
    #.perplexity() calcola l'indice di 'perplessità' dei modelli davanti a questa sequenza
    pp_tw   = modello_tweet_lp.perplexity(tokens_frase)
    pp_lett = modello_lett_lp.perplexity(tokens_frase)

    # PENALIZZAZIONE / NORMALIZZAZIONE
    # Dividiamo il punteggio di .perplexity per la dimensione totale del rispettivo vocabolario.
    # Serve a compensare il fatto che un modello con un vocabolario gigantesco tende ad avere 
    # una perplexity matematicamente più alta a prescindere dalla bontà del testo.
    pp_tw_n   = pp_tw   / len(modello_tweet_lp.vocab)
    pp_lett_n = pp_lett / len(modello_lett_lp.vocab)

    # Stabilisce l'etichetta reale (Ground Truth): se la chiave inizia con "tw", l'origine è TWITTER, altrimenti LETTERARIO (LT).
    verdetto_atteso = "TW" if nome.startswith("tw") else "LT"
    # REGOLA DI DECISIONE: Il modello che ha perplexity normalizzata MINORE è quello che 
    # fa meno fatica a spiegare la frase. Quindi il verdetto punta al modello più "sicuro".
    verdetto        = "TW" if pp_tw_n < pp_lett_n else "LT"
    # Verifica se il verdetto emesso coincide con l'origine reale della frase.
    corretto        = "✓" if verdetto == verdetto_atteso else "✗"
    # Se il verdetto è esatto, incrementa il contatore delle risposte corrette
    if verdetto == verdetto_atteso:
        corretti += 1
    totale += 1

    #stampa i risultati della frase corrente nella tabella
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
    Calcola la log-likelihood di una sequenza di token, restituisce un numero negativo.
    Più alta (meno negativa) = il modello spiega meglio il testo.
    Usiamo Laplace per evitare log(0).
    """

    # Inizializza l'accumulatore. Poiché nei logaritmi le probabilità si sommano, partiamo da 0.0 (che corrisponde alla probabilità del 100%, ovvero log(1) = 0).
    score = 0.0
    
    #Scorre tutti i token della frase a partire dal secondo (indice 1), 
    # simulando il comportamento di una catena di Markov di ordine 1 (bigrammi).
    for i in range(1, len(tokens)):
        contesto = [tokens[i-1]]#il contesto è la parola precedente
        parola   = tokens[i]#parola target è la parola corrente
        prob = modello.score(parola, contesto)# Interroga il modello per ottenere la probabilità condizionale P(w_i | w_{i-1})
        # Se la probabilità è maggiore di zero la combinazione esiste nel testo di addestramento
        if prob > 0:
            # Calcola il logaritmo naturale della probabilità e lo SOMMA allo score totale.
            score += math.log(prob)
        # GESTIONE DELLE PAROLE MAI VISTE (Backoff manuale): se la coppia ha probabilità zero, 
            # invece di far fallire il calcolo, assegna una probabilità piccolissima fittizia (10^-10).
            # Il logaritmo di un numero così piccolo applicherà una fortissima penalità negativa allo score.
        else:
            score += math.log(1e-10)  # valore piccolo per parole mai viste
    return score

def classifica_loglik(testo, mod_tw, mod_lt):
    """
    Prende un testo stringa e stabilisce se assomiglia di più 
    al dominio Twitter o a quello Letterario.
    """

    #converte il testo in minuscolo e lo tokenizza
    tokens = word_tokenize(testo.lower())
    # Calcola il punteggio di verosimiglianza logaritmica per i modelli
    ll_tw   = log_likelihood(mod_tw,   tokens)
    ll_lett = log_likelihood(mod_lt,   tokens)

    # REGOLA DI DECISIONE: Vince il modello che ottiene il punteggio MAGGIORE (più alto) ricordando che sono numeri negativi,
    verdetto   = "TWITTER" if ll_tw > ll_lett else "LETTERARIO"
    differenza = abs(ll_tw - ll_lett)#calcola la distanza matematica tra i due giudizi

    #stampa i risultati
    print(f"  Testo: '{testo}'")
    print(f"    Log-lik Twitter:    {ll_tw:.3f}")
    print(f"    Log-lik Letterario: {ll_lett:.3f}")
    print(f"    Verdetto: {verdetto} (differenza {differenza:.2f})")
    print()

#test
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

# Avvia il loop di classificazione su tutti i testi d'esempio
for testo in testi_classificare:
    classifica_loglik(testo, modello_tweet, modello_lett)

# ============================================================
# STEP 10: MLE vs Laplace
# ============================================================
print("\n=== MLE vs LAPLACE ===")

#definiamo una stringa che rappresenta un token out-of-vocabulary (parola mai vista dal modello)
parola_rara = "xyzword"
print(f"Parola mai vista: '{parola_rara}'")
# Interroga il modello MLE per calcolare P(xyzword | i).Poiché la combinazione ("i", "xyzword") non è mai apparsa nel training set, lo score sarà esattamente 0.000000.
print(f"  MLE     P = {modello_tweet.score(parola_rara, ['i']):.6f}")
#interroga il modello 'Laplace' che grazie alla correzione darà una frazione di probabilità residua molto piccola ma comunque maggiore di 0
print(f"  Laplace P = {modello_tweet_lp.score(parola_rara, ['i']):.6f}")

# Tokenizza una frase di test ("i xyzword lol") che contiene al suo interno la parola sconosciuta
frase_rara = word_tokenize("i xyzword lol")
try:
    # Prova a calcolare la Perplexity della frase usando il modello MLE, calcolo destinato a fallire matematicamente a causa della divisione per zero.
    pp_mle = modello_tweet.perplexity(frase_rara)
except:
    #Se il calcolo fallisce (scatta l'eccezione), assegniamo manualmente alla variabile il valore matematico di Infinito (float('inf')).
    pp_mle = float('inf')
    # Calcola la Perplexity usando il modello Laplace, lo smoothing permette di completare l'operazione restituendo un punteggio numerico reale e stabile.
pp_lap = modello_tweet_lp.perplexity(frase_rara)

#stampa dei risultati
print(f"\nPerplexity MLE     su frase con parola rara: {pp_mle}")
print(f"Perplexity Laplace su frase con parola rara: {pp_lap:.2f}")

# ============================================================
# STEP 11: Confronto n=1,2,3
# ============================================================
print("\n=== CONFRONTO n=1, n=2, n=3 ===")

# Definisce le due frasi civetta (banco di prova) già tokenizzate.
# 'frase_tw' sequenza tipica di twitter.
# 'frase_lt' spezzone formale e strutturato della letteratura di addestramento.
frase_tw = word_tokenize("i love you so much thank you")
frase_lt = word_tokenize("she had been very well disposed")

# Avvia un ciclo for per testare tre configurazioni di complessità crescente:
# n_test = 1 (Unigrammi), n_test = 2 (Bigrammi), n_test = 3 (Trigrammi)
for n_test in [1, 2, 3]:
    # Crea una pipeline temporanea (tr_tmp, voc_tmp) basandosi SOLO sui dati di Twitter.
    # L'algoritmo estrae gli n-grammi adatti all'ordine corrente
    tr_tmp, voc_tmp = padded_everygram_pipeline(n_test, [tokens_tweet])
    mod_tmp = Laplace(n_test)# Inizializza un modello temporaneo usando lo smoothing di Laplace, è necessario laplace perchè la frase letteraria conterrà sequenze o paorle sconosciute
    mod_tmp.fit(tr_tmp, voc_tmp)# Addestra il modello corrente unicamente sulle strutture e sul vocabolario estratti da Twitter

    pp_tw = mod_tmp.perplexity(frase_tw)# Calcola la Perplexity della frase Twitter usando il modello Twitter corrente.
    pp_lt = mod_tmp.perplexity(frase_lt)# Calcola la Perplexity della frase Letteraria usando lo STESSO modello Twitter corrente.

    print(f"\nn={n_test}:")
    print(f"  PP su frase Twitter:    {pp_tw:.2f}")
    print(f"  PP su frase Letterario: {pp_lt:.2f}")

# ============================================================
# STEP 12: Analisi linguistica
# ============================================================
print("\n=== ANALISI LINGUISTICA ===")

#CALCOLO DEL TYPE-TOKEN RATIO (TTR)
# Calcolo del TTR per i domini dividendo il numero di parole uniche (ovvero i Types) per il numero totale di parole del corpus ( ovvero i Tokens).
ttr_tweet = len(vocab_tweet_set) / len(tokens_tweet)
ttr_lett  = len(vocab_lett_set)  / len(tokens_lett)

print(f"\nType-Token Ratio:")
print(f"  Twitter:    {ttr_tweet:.4f}")
print(f"  Letterario: {ttr_lett:.4f}")
# Struttura di controllo condizionale che commenta l'output a schermo: se il TTR di Twitter è più alto, significa che nei social c'è un'alta concentrazione di parole uniche
if ttr_tweet > ttr_lett:
    print("  → Twitter ha vocabolario più vario (slang, abbreviazioni)")

# CALCOLO DELLA LUNGHEZZA MEDIA DELLE FRASI/UNITA'
lung_tw  = [len(word_tokenize(t)) for t in tweets_raw]# Crea una lista ('lung_tw') contenente la lunghezza (il numero di parole) di ogni singolo tweet del dataset originale. Usa una List Comprehension che cicla su 'tweets_raw' e applica 'word_tokenize(t)' a ogni tweet.
frasi_lt = sent_tokenize(testo_letterario_raw)# Usa 'sent_tokenize' di NLTK per segmentare il gigantesco testo continuo del romanzo in una lista di singole frasi, basandosi sulla punteggiatura forte (. ! ?). 'frasi_lt' sarà una lista di stringhe (una per ogni frase).
lung_lt  = [len(word_tokenize(f)) for f in frasi_lt]# Crea una lista ('lung_lt') contenente la lunghezza (in parole) di ciascuna frase isolata del romanzo.

# CALCOLO DELLA MEDIA ARITMETICA DELLA LUNGHEZZA DI TWEET E FRASI DELLA LETTERATURA
media_tw = sum(lung_tw) / len(lung_tw)
media_lt = sum(lung_lt) / len(lung_lt)

 #stampa dei risultati
print(f"\nLunghezza media:")
print(f"  Tweet:            {media_tw:.1f} parole")
print(f"  Frase letteraria: {media_lt:.1f} parole")
print(f"  → Frasi letterarie {media_lt - media_tw:.1f} parole più lunghe in media")

# ============================================================
# STEP 13: Grafici (Sostituzione Avanzata)
# ============================================================
print("\n=== GENERAZIONE GRAFICI AVANZATI ===")
try:
    # Palette colori dedicata (Azzurro/Blu per Twitter, Arancio/Mattone per il Letterario)
    c_tw = '#2980b9'  # Steel blue moderno
    c_lt = '#e67e22'  # Coral/Orange elegante

    # Creiamo una griglia 2x2 coordinata
    fig, axes = plt.subplots(2, 2, figsize=(16, 13), facecolor='#f8f9fa')
    fig.suptitle('Analisi Comparativa N-Gram: Twitter vs Dominio Letterario', 
                 fontsize=16, fontweight='bold', color='#1a252f', y=0.98)

    # --------------------------------------------------------
    # GRAFICO 1: Top 10 Bigrammi Twitter (Orizzontale)
    # --------------------------------------------------------
    top_tw = bi_tweet_filtrati.most_common(10)[::-1] # Invertiamo per avere il primo in alto
    y_labels_tw = [f"{p[0]} {p[1]}" for p, _ in top_tw]
    counts_tw = [c for _, c in top_tw]
    
    bars_tw = axes[0,0].barh(y_labels_tw, counts_tw, color=c_tw, alpha=0.85, height=0.6)
    axes[0,0].set_title('Top 10 Bigrammi: Twitter\n(Senza Stopwords)', fontsize=12, fontweight='bold', pad=10)
    axes[0,0].set_xlabel('Frequenza Assoluta', fontsize=10)
    axes[0,0].grid(axis='x', linestyle='--', alpha=0.5)
    axes[0,0].bar_label(bars_tw, padding=5, fontsize=9, color='#475569')

    # --------------------------------------------------------
    # GRAFICO 2: Top 10 Bigrammi Letterario (Orizzontale)
    # --------------------------------------------------------
    top_lt = bi_lett_filtrati.most_common(10)[::-1]
    y_labels_lt = [f"{p[0]} {p[1]}" for p, _ in top_lt]
    counts_lt = [c for _, c in top_lt]
    
    bars_lt = axes[0,1].barh(y_labels_lt, counts_lt, color=c_lt, alpha=0.85, height=0.6)
    axes[0,1].set_title('Top 10 Bigrammi: Romanzo (Emma)\n(Senza Stopwords)', fontsize=12, fontweight='bold', pad=10)
    axes[0,1].set_xlabel('Frequenza Assoluta', fontsize=10)
    axes[0,1].grid(axis='x', linestyle='--', alpha=0.5)
    axes[0,1].bar_label(bars_lt, padding=5, fontsize=9, color='#475569')

    # --------------------------------------------------------
    # GRAFICO 3: Log-Likelihood Classificatore (Barre a specchio negative)
    # --------------------------------------------------------
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
        ll_tw_vals.append(log_likelihood(modello_tweet, tok))
        ll_lett_vals.append(log_likelihood(modello_lett, tok))
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

    # --------------------------------------------------------
    # GRAFICO 4: Metriche Linguistiche con Doppio Asse Y (Twinx)
    # --------------------------------------------------------
    categorie = ['Twitter (Social)', 'Letterario (Austen)']
    ttr_vals = [ttr_tweet, ttr_lett]
    lung_vals = [media_tw, media_lt]
    
    x2 = np.arange(len(categorie))
    
    # Primo asse (Sinistro): Type-Token Ratio
    color_ttr = '#16a085'
    axes[1,1].bar(x2 - 0.2, ttr_vals, 0.35, label='Type-Token Ratio (TTR)', color=color_ttr, alpha=0.8)
    axes[1,1].set_ylabel('Richiesta Lessicale (TTR)', color=color_ttr, fontweight='bold')
    axes[1,1].tick_params(axis='y', labelcolor=color_ttr)
    axes[1,1].set_ylim(0, max(ttr_vals) * 1.2)
    
    # Creazione del second asse Y condiviso (Destro)
    ax4_twin = axes[1,1].twinx()
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

    # Pulizia estetica finale (Spines removal)
    for ax in axes.flat:
        ax.set_facecolor('#ffffff')
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        ax.spines['left'].set_color('#bdc3c7')
        ax.spines['bottom'].set_color('#bdc3c7')
    
    # Calcolo dinamico del percorso sicuro usando il modulo os già importato in cima
    cartella_script = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    percorso_salvataggio = os.path.join(cartella_script, 'confronto_risultati_laboratorio.png')
    
    plt.tight_layout()
    plt.savefig(percorso_salvataggio, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"Grafico salvato con successo in: {percorso_salvataggio}")

except Exception as e:
    print(f"Errore durante la generazione del grafico dello Step 13: {e}")
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