"""
=============================================================
  CONVERTITORE ITALIANO → ITALIANO-YODA (IT-YO)
=============================================================

CONCETTI CHIAVE:
  - Italiano (SVO): "Mario mangia la mela"
                     S      V      O
  - Italiano-Yoda (XSV): "La mela Mario mangia"
                           O      S      V

PIPELINE:
  1. Grammatica CFG in Forma Normale di Chomsky (CNF)
  2. Parsing con algoritmo CKY → albero di derivazione
  3. Trasformazione dell'albero: SVX → XSV
  4. Stampa delle foglie → frase Yoda

=============================================================
"""

# ===========================================================
# SEZIONE 1 — GRAMMATICA CFG IN CNF
# ===========================================================
#
# Una grammatica Context-Free (CFG) descrive la struttura
# sintattica di frasi tramite regole di riscrittura.
#
# La FORMA NORMALE DI CHOMSKY (CNF) richiede che ogni regola sia:
#   A → B C    (esattamente 2 non-terminali)
#   A → 'a'    (esattamente 1 terminale)
#
# Perché CNF? Perché l'algoritmo CKY funziona SOLO con CNF.
#
# STRUTTURA DELLA FRASE ITALIANA (SVO):
#
#   S  → NP VP          (Frase = SN + SV)
#   NP → Det N          (SN = articolo + nome)
#   NP → N              (SN = solo nome, es. "Mario")
#   VP → V NP           (SV = verbo + oggetto diretto)
#   VP → V PP           (SV = verbo + complemento preposizionale)
#   VP → V              (SV = solo verbo)
#   PP → Prep NP        (SP = preposizione + SN)
#
# LESSICO (terminali):
#   Det  → 'il' | 'la' | 'lo' | 'un' | 'una' | 'i' | 'le'
#   N    → 'Mario' | 'mela' | 'gatto' | 'libro' | ...
#   V    → 'mangia' | 'legge' | 'vede' | 'dà' | ...
#   Prep → 'a' | 'di' | 'con' | 'su' | 'per'


# ---- Strutture dati per la grammatica ----

# Regole BINARIE: A → B C
# Formato: dizionario {(B, C): [A, A2, ...]}
# (più simboli possono derivare dalla stessa coppia)
BINARY_RULES = {
    ('NP',  'VP'):   ['S'],
    ('Det', 'N'):    ['NP'],
    ('V',   'NP'):   ['VP'],
    ('V',   'PP'):   ['VP'],
    ('Prep','NP'):   ['PP'],
}

# Regole UNARIE: A → a  (solo terminali)
# Formato: dizionario {parola: [categoria1, categoria2, ...]}
LEXICON = {
    # articoli determinativi
    'il':      ['Det'],
    'la':      ['Det'],
    'lo':      ['Det'],
    'i':       ['Det'],
    'le':      ['Det'],
    # articoli indeterminativi
    'un':      ['Det'],
    'una':     ['Det'],
    # nomi propri (fungono da NP direttamente)
    'Mario':   ['N', 'NP'],
    'Luigi':   ['N', 'NP'],
    'Maria':   ['N', 'NP'],
    # nomi comuni
    'mela':    ['N'],
    'libro':   ['N'],
    'gatto':   ['N'],
    'cane':    ['N'],
    'uomo':    ['N'],
    'donna':   ['N'],
    'bambino': ['N'],
    'studente':['N'],
    'pane':    ['N'],
    'acqua':   ['N'],
    # verbi
    'mangia':  ['V'],
    'legge':   ['V'],
    'vede':    ['V'],
    'prende':  ['V'],
    'porta':   ['V'],
    'ama':     ['V'],
    'saluta':  ['V'],
    # preposizioni
    'a':       ['Prep'],
    'di':      ['Prep'],
    'con':     ['Prep'],
    'su':      ['Prep'],
    'per':     ['Prep'],
}

# ===========================================================
# SEZIONE 2 — NODO DELL'ALBERO DI DERIVAZIONE
# ===========================================================
#
# L'albero di derivazione (parse tree) rappresenta la struttura
# sintattica della frase.
#
# Esempio per "Mario mangia la mela":
#
#         S
#        / \
#       NP  VP
#       |   / \
#     Mario V  NP
#           |  / \
#        mangia Det N
#               |   |
#              la  mela
#
# Ogni nodo ha:
#   - label:    il simbolo (es. 'S', 'NP', 'Mario')
#   - children: lista di figli (vuota = foglia)
#   - word:     la parola se è una foglia lessicale


class Nodo:
    """Un nodo dell'albero di derivazione."""

    def __init__(self, label, children=None, word=None):
        self.label = label          # simbolo grammaticale o parola
        self.children = children or []  # lista di Nodi figli
        self.word = word            # parola (solo per le foglie)

    def is_leaf(self):
        return len(self.children) == 0

    def __repr__(self):
        if self.is_leaf():
            return f"[{self.label}: '{self.word}']"
        figli = ', '.join(repr(c) for c in self.children)
        return f"[{self.label} → {figli}]"

    def pretty_print(self, indent=0):
        """Stampa l'albero in modo leggibile."""
        prefix = "  " * indent
        if self.is_leaf():
            print(f"{prefix}{self.label}: '{self.word}'")
        else:
            print(f"{prefix}{self.label}")
            for child in self.children:
                child.pretty_print(indent + 1)


# ===========================================================
# SEZIONE 3 — ALGORITMO CKY (Cocke-Kasami-Younger)
# ===========================================================
#
# CKY è un algoritmo di parsing bottom-up per grammatiche CNF.
# Riempie una tabella triangolare T dove:
#   T[i][j] = insieme dei simboli che derivano la sottostringa
#              dalla parola i alla parola j (incluse).
#
# Per una frase di n parole, la tabella ha n×n celle.
# La cella T[0][n-1] (in alto a destra nella tabella triangolare)
# contiene i simboli che derivano l'intera frase.
#
# ESEMPIO con "Mario mangia la mela" (4 parole, indici 0..3):
#
#   i\j  0       1        2        3
#    0   {NP}   {S}      {}       {S}     ← Mario mangia la mela
#    1          {V,VP}   {}       {VP}    ← mangia la mela
#    2                   {Det}    {NP}    ← la mela
#    3                            {N}     ← mela
#
# Se 'S' ∈ T[0][3] → la frase è grammaticale!
#
# RICOSTRUZIONE: per ogni cella memorizziamo anche il "back pointer"
# (come ci siamo arrivati) per ricostruire l'albero di derivazione.


def cky_parse(sentence, binary_rules=BINARY_RULES, lexicon=LEXICON):
    """
    Esegue il parsing CKY su una lista di parole.
    
    Restituisce il primo albero di derivazione trovato con radice 'S',
    oppure None se la frase non è parsabile con la grammatica G1.
    """
    words = sentence  # lista di parole tokenizzate
    n = len(words)

    # table[i][j] = dizionario {simbolo: Nodo}
    # Memorizziamo il nodo già costruito per ricostruire l'albero.
    table = [[{} for _ in range(n)] for _ in range(n)]

    # ----------------------------------------------------------
    # PASSO 1: riempire la diagonale principale (celle [i][i])
    # Ogni cella [i][i] contiene i simboli che derivano la sola
    # parola words[i].
    # ----------------------------------------------------------
    for i, word in enumerate(words):
        if word in lexicon:
            for pos_tag in lexicon[word]:
                # Creo un nodo foglia
                leaf = Nodo(label=word, word=word)
                # Creo il nodo POS che punta alla foglia
                table[i][i][pos_tag] = Nodo(label=pos_tag, children=[leaf])

                # Propagazione unaria NP → N (nomi propri che sono già NP nel lessico
                # vengono gestiti direttamente nel lessico, ma aggiungiamo anche
                # la regola Det N → NP tramite le regole binarie sotto)

    # ----------------------------------------------------------
    # PASSO 2: riempire le celle [i][j] con j > i
    # Per ogni lunghezza span (da 2 a n), per ogni posizione i,
    # proviamo tutte le possibili suddivisioni k.
    # ----------------------------------------------------------
    for span in range(2, n + 1):          # lunghezza della sottostringa
        for i in range(n - span + 1):     # inizio della sottostringa
            j = i + span - 1              # fine della sottostringa
            for k in range(i, j):         # punto di suddivisione
                # Proviamo tutte le coppie (B, C) nelle regole binarie
                for (B, C), parents in binary_rules.items():
                    if B in table[i][k] and C in table[k+1][j]:
                        # Trovato! B deriva words[i..k] e C deriva words[k+1..j]
                        for A in parents:
                            if A not in table[i][j]:
                                # Costruiamo il nodo A con figli B e C
                                node_B = table[i][k][B]
                                node_C = table[k+1][j][C]
                                table[i][j][A] = Nodo(
                                    label=A,
                                    children=[node_B, node_C]
                                )

    # ----------------------------------------------------------
    # RISULTATO: cerchiamo 'S' nella cella [0][n-1]
    # ----------------------------------------------------------
    if 'S' in table[0][n-1]:
        return table[0][n-1]['S']
    else:
        return None


# ===========================================================
# SEZIONE 4 — TRASFORMAZIONE DELL'ALBERO: SVX → XSV
# ===========================================================
#
# Obiettivo: riscrivere l'albero SVO in un albero XSV (Yoda).
#
# Regola di trasformazione:
#   Un nodo S ha la struttura:    S → NP(sogg) VP
#   Un nodo VP ha la struttura:   VP → V NP(ogg)  oppure  VP → V PP
#
# Trasformazione Yoda:
#   Originale:  S → NP(sogg)  [VP → V  Complemento]
#   Yoda:       S → Complemento  NP(sogg)  V
#               ^^^^^^^^^^^^^^ il complemento sale in testa
#
# In termini di albero:
#   Prima:     S
#             / \
#           NP   VP
#           |   / \
#         Mario V   NP
#               |   / \
#            mangia Det N
#                   |   |
#                  la  mela
#
#   Dopo:      S_yoda
#             /   |   \
#           NP   NP    V
#          / \   |     |
#        Det  N Mario mangia
#         |   |
#        la  mela
#
# Nota: ignoriamo l'ambiguità e usiamo il primo albero ottenuto.


def trasforma_in_yoda(nodo):
    """
    Trasforma ricorsivamente l'albero di derivazione italiano
    in un albero Italiano-Yoda (ordine XSV).
    
    Regola principale: quando troviamo S → NP VP
    con VP → V Comp (dove Comp è NP o PP),
    riordiniamo in S_yoda → Comp NP V
    """

    # Caso base: foglia → non c'è nulla da trasformare
    if nodo.is_leaf():
        return nodo

    # Prima trasformiamo ricorsivamente i figli
    nuovi_figli = [trasforma_in_yoda(f) for f in nodo.children]
    nodo.children = nuovi_figli

    # Regola di trasformazione principale: S → NP VP
    if nodo.label == 'S' and len(nodo.children) == 2:
        sogg = nodo.children[0]   # NP (soggetto)
        vp   = nodo.children[1]   # VP

        # VP → V Complemento (NP o PP)
        if vp.label == 'VP' and len(vp.children) == 2:
            verbo = vp.children[0]        # V
            compl = vp.children[1]        # NP o PP

            # Nuovo ordine Yoda: Complemento → Soggetto → Verbo
            nodo.label = 'S_yoda'
            nodo.children = [compl, sogg, verbo]

        # VP → V solo (verbo intransitivo): V NP → NP V
        elif vp.label == 'VP' and len(vp.children) == 1:
            verbo = vp.children[0]
            nodo.label = 'S_yoda'
            nodo.children = [sogg, verbo]

    return nodo


# ===========================================================
# SEZIONE 5 — STAMPA DELLE FOGLIE (visita DFS)
# ===========================================================
#
# Una volta trasformato l'albero, la frase Yoda si ottiene
# visitando le foglie da sinistra a destra (DFS in-order).
#
# Visita DFS (Depth-First Search, pre-order):
#   - Se il nodo è una foglia → aggiungi la parola
#   - Altrimenti → visita ricorsivamente i figli nell'ordine


def raccogli_foglie(nodo):
    """
    Visita l'albero in profondità (DFS) e restituisce
    la lista delle parole nelle foglie, da sinistra a destra.
    """
    if nodo.is_leaf():
        return [nodo.word]

    parole = []
    for figlio in nodo.children:
        parole.extend(raccogli_foglie(figlio))
    return parole


def converti_in_yoda(frase_stringa):
    """
    Funzione principale: riceve una frase italiana come stringa
    e restituisce la frase Italiano-Yoda.
    """
    # Tokenizzazione: dividiamo la stringa in parole
    parole = frase_stringa.strip().split()

    print(f"\n{'='*55}")
    print(f"  INPUT:  {frase_stringa}")
    print(f"{'='*55}")

    # Fase 1: Parsing CKY
    print("\n[Fase 1] Parsing CKY...")
    albero = cky_parse(parole)

    if albero is None:
        print("  ✗ Parsing fallito: la frase non è riconosciuta dalla grammatica G1.")
        print("  → Suggerimento: aggiungi le parole mancanti al lessico LEXICON.")
        return None

    print("  ✓ Albero di derivazione trovato:")
    albero.pretty_print(indent=2)

    # Fase 2: Trasformazione SVX → XSV
    print("\n[Fase 2] Trasformazione in ordine Yoda...")
    albero_yoda = trasforma_in_yoda(albero)
    print("  ✓ Albero Yoda:")
    albero_yoda.pretty_print(indent=2)

    # Fase 3: Raccolta delle foglie
    print("\n[Fase 3] Raccolta foglie (frase Yoda)...")
    foglie = raccogli_foglie(albero_yoda)
    frase_yoda = ' '.join(foglie)

    print(f"\n  OUTPUT: {frase_yoda}")
    print(f"{'='*55}\n")

    return frase_yoda


# ===========================================================
# SEZIONE 6 — ESEMPI E TEST
# ===========================================================

if __name__ == '__main__':

    frasi_di_esempio = [
        "Mario mangia la mela",
        "Luigi legge il libro",
        "Maria vede il gatto",
        "il bambino prende il pane",
        "la donna ama il cane",
        "Mario saluta Luigi",
    ]

    print("\n" + "="*55)
    print("  CONVERTITORE ITALIANO → ITALIANO-YODA")
    print("="*55)
    print("\nOrdine originale:  SVO (Soggetto Verbo Oggetto)")
    print("Ordine Yoda:       XSV (Oggetto Soggetto Verbo)")

    for frase in frasi_di_esempio:
        converti_in_yoda(frase)

    # Test di frase non riconoscibile
    print("\n--- Test con frase fuori dalla grammatica ---")
    converti_in_yoda("il computer elabora i dati")
