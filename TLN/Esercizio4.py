# ============================================================
# LAB 4 - Modeling social media and literary language with N-grams
# TLN - Daniele Radicioni, UNITO
# ============================================================

# ============================================================
# STEP 0: Installazione e import
# ============================================================
import nltk
import re
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk import bigrams, trigrams, ngrams
from nltk.lm import MLE, Laplace
from nltk.lm.preprocessing import padded_everygram_pipeline

# Scarica tutto il necessario (solo la prima volta)
nltk.download('twitter_samples')
nltk.download('gutenberg')
nltk.download('punkt')
nltk.download('punkt_tab')

print("Import completati con successo!")

# ============================================================
# STEP 1: Carica i dati
# ============================================================

from nltk.corpus import twitter_samples, gutenberg

# --- TWITTER ---
tweets_raw = twitter_samples.strings('tweets.20150430-223406.json')

print(f"Numero tweet caricati: {len(tweets_raw)}")
print(f"Esempio tweet 1: {tweets_raw[0]}")
print(f"Esempio tweet 2: {tweets_raw[1]}")
print(f"Esempio tweet 3: {tweets_raw[2]}")

# --- LETTERARIO ---
testo_letterario_raw = gutenberg.raw('austen-emma.txt')

print(f"\nLunghezza testo letterario: {len(testo_letterario_raw)} caratteri")
print(f"Prime 200 parole:\n{testo_letterario_raw[:300]}")

# ============================================================
# STEP 2: Pulizia dei testi
# ============================================================

def pulisci_tweet(testo):
    """
    Pulisce un singolo tweet rimuovendo:
    - URL (https://...)
    - Menzioni (@utente)
    - Hashtag (#) - tiene la parola, rimuove il simbolo
    - Punteggiatura e caratteri speciali
    - Rende tutto minuscolo
    """
    testo = re.sub(r'http\S+', '', testo)          # rimuovi URL
    testo = re.sub(r'@\w+', '', testo)              # rimuovi @menzioni
    testo = re.sub(r'#', '', testo)                 # rimuovi simbolo #
    testo = re.sub(r'[^a-zA-Z\s]', '', testo)      # solo lettere e spazi
    testo = testo.lower().strip()                   # minuscolo + strip
    return testo

def pulisci_letterario(testo):
    """
    Pulisce il testo letterario rimuovendo:
    - Punteggiatura
    - Numeri
    - Rende tutto minuscolo
    """
    testo = re.sub(r'[^a-zA-Z\s]', '', testo)
    testo = testo.lower().strip()
    return testo

# Applica la pulizia
tweets_puliti = [pulisci_tweet(t) for t in tweets_raw]
# Rimuovi tweet vuoti dopo la pulizia
tweets_puliti = [t for t in tweets_puliti if len(t) > 0]

testo_lett_pulito = pulisci_letterario(testo_letterario_raw)

# Mostra confronto prima/dopo
print("=== CONFRONTO PRIMA/DOPO PULIZIA ===")
print(f"\nTweet PRIMA: {tweets_raw[0]}")
print(f"Tweet DOPO:  {tweets_puliti[0]}")

print(f"\nLetterario PRIMA: {testo_letterario_raw[:100]}")
print(f"Letterario DOPO:  {testo_lett_pulito[:100]}")

# ============================================================
# STEP 3: Tokenizzazione
# ============================================================

# Unisci tutti i tweet in un unico testo
testo_tweet_unito = ' '.join(tweets_puliti)

# Tokenizza
tokens_tweet = word_tokenize(testo_tweet_unito)
tokens_lett  = word_tokenize(testo_lett_pulito)

print("=== TOKENIZZAZIONE ===")
print(f"\nPrimi 15 token TWITTER: {tokens_tweet[:15]}")
print(f"Primi 15 token LETTERARIO: {tokens_lett[:15]}")
print(f"\nTotale token Twitter:    {len(tokens_tweet)}")
print(f"Totale token Letterario: {len(tokens_lett)}")

# Vocabolario (parole uniche)
vocab_tweet_set = set(tokens_tweet)
vocab_lett_set  = set(tokens_lett)

print(f"\nParole uniche Twitter:    {len(vocab_tweet_set)}")
print(f"Parole uniche Letterario: {len(vocab_lett_set)}")

# ============================================================
# STEP 4: N-gram - Costruzione e analisi
# ============================================================

print("\n=== ANALISI N-GRAM ===")

# --- UNIGRAMMI ---
uni_tweet = Counter(ngrams(tokens_tweet, 1))
uni_lett  = Counter(ngrams(tokens_lett, 1))

print("\n--- UNIGRAMMI (top 10) ---")
print("TWITTER:")
for parola, count in uni_tweet.most_common(10):
    print(f"  {parola[0]:<15} → {count} volte")

print("\nLETTERARIO:")
for parola, count in uni_lett.most_common(10):
    print(f"  {parola[0]:<15} → {count} volte")

# --- BIGRAMMI ---
bi_tweet = Counter(ngrams(tokens_tweet, 2))
bi_lett  = Counter(ngrams(tokens_lett, 2))

print("\n--- BIGRAMMI (top 10) ---")
print("TWITTER:")
for coppia, count in bi_tweet.most_common(10):
    print(f"  {str(coppia):<30} → {count} volte")

print("\nLETTERARIO:")
for coppia, count in bi_lett.most_common(10):
    print(f"  {str(coppia):<30} → {count} volte")

# --- TRIGRAMMI ---
tri_tweet = Counter(ngrams(tokens_tweet, 3))
tri_lett  = Counter(ngrams(tokens_lett, 3))

print("\n--- TRIGRAMMI (top 10) ---")
print("TWITTER:")
for tripletta, count in tri_tweet.most_common(10):
    print(f"  {str(tripletta):<40} → {count} volte")

print("\nLETTERARIO:")
for tripletta, count in tri_lett.most_common(10):
    print(f"  {str(tripletta):<40} → {count} volte")

# ============================================================
# STEP 5: Addestramento modello MLE
# ============================================================

print("\n=== ADDESTRAMENTO MODELLO MLE ===")

n = 2  # bigrammi

# Prepara i dati
train_tweet, vocab_tw = padded_everygram_pipeline(n, [tokens_tweet])
train_lett,  vocab_lt = padded_everygram_pipeline(n, [tokens_lett])

# Addestra i modelli
modello_tweet = MLE(n)
modello_tweet.fit(train_tweet, vocab_tw)

modello_lett = MLE(n)
modello_lett.fit(train_lett, vocab_lt)

print("Modelli addestrati!")
print(f"Vocabolario Twitter:    {len(modello_tweet.vocab)} parole")
print(f"Vocabolario Letterario: {len(modello_lett.vocab)} parole")

# Interroga il modello
print("\n--- PROBABILITA' CONDIZIONALI ---")

# Probabilità tipiche Twitter
print("\nModello TWITTER:")
print(f"  P('love'  | 'i')    = {modello_tweet.score('love', ['i']):.4f}")
print(f"  P('wait'  | 'cant') = {modello_tweet.score('wait', ['cant']):.4f}")
print(f"  P('much'  | 'so')   = {modello_tweet.score('much', ['so']):.4f}")
print(f"  P('mr'    | 'said') = {modello_tweet.score('mr', ['said']):.4f}")

# Probabilità tipiche Letterario
print("\nModello LETTERARIO:")
print(f"  P('mr'    | 'said') = {modello_lett.score('mr', ['said']):.4f}")
print(f"  P('been'  | 'had')  = {modello_lett.score('been', ['had']):.4f}")
print(f"  P('love'  | 'i')    = {modello_lett.score('love', ['i']):.4f}")
print(f"  P('wait'  | 'cant') = {modello_lett.score('wait', ['cant']):.4f}")

# ============================================================
# STEP 6: Perplexity
# ============================================================

print("\n=== PERPLEXITY ===")

# Prepara frasi di test
frasi_test = {
    "tweet_1": "omg i cant wait so excited lol",
    "tweet_2": "i love this so much cant stop laughing",
    "lett_1":  "the young lady had been sitting quietly in the room",
    "lett_2":  "she was a woman of mean understanding little information",
}

print("\nFrase | Modello Twitter | Modello Letterario")
print("-" * 60)

for nome, frase in frasi_test.items():
    tokens_frase = word_tokenize(frase)
    
    try:
        pp_tw   = modello_tweet.perplexity(tokens_frase)
        pp_lett = modello_lett.perplexity(tokens_frase)
        print(f"{nome:<10} | {pp_tw:>15.2f} | {pp_lett:>18.2f}")
    except Exception as e:
        print(f"{nome:<10} | Errore: {e}")

print("\nInterpretazione:")
print("- Valore BASSO = modello conosce bene questo tipo di testo")
print("- Valore ALTO  = modello sorpreso da questo tipo di testo")

# ============================================================
# STEP 7: Generazione testo
# ============================================================

print("\n=== GENERAZIONE TESTO ===")

# Genera testo nello stile Twitter
testo_generato_tw = modello_tweet.generate(20, random_seed=42)
print(f"\nStile TWITTER (20 parole):")
print(' '.join(testo_generato_tw))

# Genera testo nello stile letterario
testo_generato_lt = modello_lett.generate(20, random_seed=42)
print(f"\nStile LETTERARIO (20 parole):")
print(' '.join(testo_generato_lt))

# ============================================================
# STEP 8: Confronto finale
# ============================================================

print("\n=== CONFRONTO FINALE TRA I DUE DOMINI ===")

print("\n1. VOCABOLARIO:")
print(f"   Twitter:    {len(vocab_tweet_set):>6} parole uniche")
print(f"   Letterario: {len(vocab_lett_set):>6} parole uniche")

print("\n2. TOP 5 BIGRAMMI PIU' CARATTERISTICI:")
print("   Twitter (linguaggio colloquiale):")
for coppia, count in bi_tweet.most_common(5):
    print(f"     {str(coppia)}")
print("   Letterario (linguaggio formale):")
for coppia, count in bi_lett.most_common(5):
    print(f"     {str(coppia)}")

print("\n3. PERPLEXITY CROSS-DOMAIN (riassunto):")
print("   Un modello addestrato su Twitter è molto sorpreso dal testo letterario")
print("   e viceversa → i due domini sono statisticamente molto diversi")

print("\n\nLab completato!")