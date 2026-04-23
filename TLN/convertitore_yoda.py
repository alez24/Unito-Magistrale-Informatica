"""
=============================================================
  CONVERTITORE LESSICALE ITALIANO → YODA (IT-YO)
=============================================================
"""
import argparse

# ===========================================================
# GRAMMATICA CFG IN CNF
# ===========================================================

BINARY_RULES = {
    ('NP',  'VP'):   ['S'],
    ('Det', 'N'):    ['NP'],
    ('Num', 'N'):    ['NP'],       # NP → Num N  ("novecento anni")
    ('NP',  'PP'):   ['NP'],       # NP → NP PP  ("novecento anni di età")
    ('V',   'NP'):   ['VP', 'VP1'],# VP → V NP, VP1 → V NP
    ('V',   'PP'):   ['VP'],
    ('V',   'Adj'):  ['VP'],       # VP → V Adj  (copulativo: "siamo illuminati")
    ('VP1', 'Adv'):  ['VP'],       # VP → VP1 Adv  ("hai amici lì")
    ('Prep','NP'):   ['PP'],
}

LEXICON = {
    # ARTICOLI / DETERMINANTI 
    'il':      ['Det'], 'la':      ['Det'], 'lo':      ['Det'],
    'i':       ['Det'], 'le':      ['Det'], 'gli':     ['Det'],
    'un':      ['Det'], 'una':     ['Det'], 'uno':     ['Det'], 
    # dimostrativi (usati come determinanti)
    'questo':  ['Det'], 'questa':  ['Det'], 'quello':  ['Det'], 'quella':  ['Det'],

    # NOMI PROPRI E PRONOMI (NP diretti) 
    'Mario':   ['N', 'NP'], 'Luigi':   ['N', 'NP'], 'Maria':   ['N', 'NP'],
    'Giulia':  ['N', 'NP'], 'Luca':    ['N', 'NP'], 'Roma':    ['N', 'NP'],
    'Yoda':    ['N', 'NP'], 'Luke':    ['N', 'NP'], 'Vader':   ['N', 'NP'],
    # pronomi
    'Io':      ['NP'], 'Tu':      ['NP'], 'Lui':     ['NP'], 'Lei':     ['NP'],
    'Noi':     ['NP'], 'Voi':     ['NP'], 'Loro':    ['NP'], 'Egli':    ['NP'],

    # NOMI COMUNI (N) 
    'mela':    ['N'], 'libro':   ['N'], 'gatto':   ['N'], 'cane':    ['N'],
    'uomo':    ['N'], 'donna':   ['N'], 'bambino': ['N'], 'studente':['N'],
    'pane':    ['N'], 'acqua':   ['N'], 'amici':   ['N', 'NP'], 'anni':  ['N'],
    'età':     ['N', 'NP'],              'uomo':   ['N', 'NP'],
    'spada':   ['N'], 'forza':   ['N'], 'maestro': ['N'], 'allievo': ['N'],
    'casa':    ['N'], 'macchina':['N'], 'strada':  ['N'], 'albero':  ['N'],
    'sole':    ['N'], 'luna':    ['N'], 'cielo':   ['N'], 'terra':   ['N'],
    'ragazzo': ['N'], 'ragazza': ['N'], 'cibo':    ['N'], 'vino':    ['N'],
    'paura':   ['N'], 'rabbia':  ['N'], 'guerra':  ['N'], 'pace':    ['N'],
    'lato':    ['N'], 'cavaliere':['N'],

    # VERBI (V) 
    'mangia':  ['V'], 'legge':   ['V'], 'vede':    ['V'], 'prende':  ['V'],
    'porta':   ['V'], 'ama':     ['V'], 'saluta':  ['V'], 'hai':     ['V'],
    'avrai':   ['V'], 'siamo':   ['V'],
    'usa':     ['V'], 'sente':   ['V'], 'scrive':  ['V'], 'beve':    ['V'],
    'dorme':   ['V'], 'corre':   ['V'], 'pensa':   ['V'], 'crede':   ['V'],
    'conosce': ['V'], 'trova':   ['V'], 'cerca':   ['V'], 'è':       ['V'],
    'sono':    ['V'], 'era':     ['V'], 'sarà':    ['V'], 'teme':    ['V'],
    'vuole':   ['V'], 'può':     ['V'], 'deve':    ['V'], 'vince':   ['V'],

    # PREPOSIZIONI (Prep) 
    'a':       ['Prep'], 'di':      ['Prep'], 'con':     ['Prep'],
    'su':      ['Prep'], 'per':     ['Prep'], 'in':      ['Prep'],
    'da':      ['Prep'], 'tra':     ['Prep'], 'fra':     ['Prep'],
    'verso':   ['Prep'], 'contro':  ['Prep'],

    #  NUMERALI (Num) 
    'uno':         ['Num'], 'due':         ['Num'], 'tre':         ['Num'],
    'quattro':     ['Num'], 'dieci':       ['Num'], 'cento':       ['Num'],
    'novecento':   ['Num'], 'mille':       ['Num'],

    # AGGETTIVI (Adj)
    'illuminati':  ['Adj'], 'potente':     ['Adj'], 'oscuro':      ['Adj'],
    'saggio':      ['Adj'], 'giovane':     ['Adj'], 'vecchio':     ['Adj'],
    'forte':       ['Adj'], 'debole':      ['Adj'], 'bello':       ['Adj'],
    'brutto':      ['Adj'], 'grande':      ['Adj'], 'piccolo':     ['Adj'],
    'rosso':       ['Adj'], 'nero':        ['Adj','N'], 'bianco':      ['Adj'],
    'buono':       ['Adj'], 'cattivo':     ['Adj'], 'luminoso':    ['Adj'],
   

    # AVVERBI (Adv)
    'lì':      ['Adv'], 'qui':     ['Adv'], 'ora':     ['Adv'],
    'sempre':  ['Adv'], 'mai':     ['Adv'], 'bene':    ['Adv'],
    'male':    ['Adv'], 'molto':   ['Adv'], 'poco':    ['Adv'],
    'forse':   ['Adv'], 'oggi':    ['Adv'], 'domani':  ['Adv'],
}

# ===========================================================
# ALBERO DI DERIVAZIONE
# ===========================================================

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
# ALGORITMO CKY 
# ===========================================================


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

    # cerchiamo 'S' nella cella [0][n-1]
    if 'S' in table[0][n-1]:
        return table[0][n-1]['S']
    else:
        return None


# ===========================================================
# TRASFORMAZIONE DELL'ALBERO: SVX → XSV
# ===========================================================

def trasforma_in_yoda(nodo):
    """
    Trasforma ricorsivamente l'albero di derivazione italiano in un albero Italiano-Yoda (ordine XSV).
    Regola principale: quando troviamo S → NP VP con VP → V Comp (dove Comp è NP o PP), riordiniamo in S_yoda → Comp NP V
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

        if vp.label == 'VP' and len(vp.children) == 2:
            child0 = vp.children[0]
            child1 = vp.children[1]

            # Caso 1: VP → V NP/PP/Adj (standard e copulativo)
            # "mangia la mela", "siamo illuminati"
            if child0.label == 'V' and child1.label in ('NP', 'PP', 'Adj'):
                verbo = child0
                compl = child1
                nodo.label = 'S_yoda'
                nodo.children = [compl, sogg, verbo]

            # Caso 2: VP → VP1 Adv ("hai amici lì")
            # VP1 → V NP: il complemento NP va in testa, Adv resta in coda
            elif child0.label == 'VP1' and child1.label == 'Adv':
                vp1 = child0
                adv = child1
                if len(vp1.children) == 2 and vp1.children[0].label == 'V':
                    verbo = vp1.children[0]
                    compl = vp1.children[1]
                    nodo.label = 'S_yoda'
                    nodo.children = [compl, sogg, verbo, adv]

        # VP → V solo (verbo intransitivo)
        elif vp.label == 'VP' and len(vp.children) == 1:
            verbo = vp.children[0]
            nodo.label = 'S_yoda'
            nodo.children = [sogg, verbo]

    return nodo


# ===========================================================
# STAMPA DELLE FOGLIE INVERTITE
# ===========================================================



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

    # Parsing CKY
    print("\n[Fase 1] Parsing CKY...")
    albero = cky_parse(parole)

    if albero is None:
        print("  ✗ Parsing fallito: la frase non è riconosciuta dalla grammatica G1.")
        print("  → Suggerimento: aggiungi le parole mancanti al lessico LEXICON.")
        return None

    print(" Albero di derivazione trovato:")
    albero.pretty_print(indent=2)

    # Trasformazione SVX → XSV
    print("\n[Fase 2] Trasformazione in ordine Yoda...")
    albero_yoda = trasforma_in_yoda(albero)
    print(" Albero Yoda:")
    albero_yoda.pretty_print(indent=2)

    # Raccolta delle foglie
    print("\n[Fase 3] Raccolta foglie (frase Yoda)...")
    foglie = raccogli_foglie(albero_yoda)

    # Post-processing: maiuscole/minuscole stile frase
    # I nomi propri (es. Mario) restano maiuscoli, il resto diventa minuscolo,
    # poi si capitalizza la prima parola della frase Yoda.
    nomi_propri = {w for w, tags in LEXICON.items() if 'N' in tags and 'NP' in tags and w[0].isupper()}
    foglie = [w if w in nomi_propri else w.lower() for w in foglie]
    if foglie:
        foglie[0] = foglie[0].capitalize()
    frase_yoda = ' '.join(foglie)

    print(f"\n  OUTPUT: {frase_yoda}")
    print(f"{'='*55}\n")

    return frase_yoda



# ===========================================================
# TEST
# ===========================================================

if __name__ == '__main__':
    # Inizializzazione parser
    parser = argparse.ArgumentParser(
        description="Convertitore Italiano → Italiano-Yoda",
        epilog="Esempio d'uso: python yoda.py 'Tu hai amici lì'"
    )
    
    # argomento per la frase
    # nargs='?' significa che l'argomento è opzionale
    parser.add_argument(
        "frase", 
        type=str, 
        nargs='?', 
        help="La frase in italiano da convertire"
    )
    
    # Aggiunge flag --test per eseguire frasi preimpostate
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Esegue le frasi d'esame e i test predefiniti"
    )

    # Legge argomenti da terminale
    args = parser.parse_args()

    print("\n" + "="*55)
    print("  CONVERTITORE ITALIANO → ITALIANO-YODA")
    print("="*55)

    # logica di esecuzione
    if args.test:
        #flag --test
        frasi_esame = [
            ("Tu hai amici lì",                    "Amici tu hai lì"),
            ("Tu avrai novecento anni di età",      "Novecento anni di età tu avrai"),
            ("Noi siamo illuminati",                "Illuminati noi siamo"),
        ]
        print("\n--- ESECUZIONE TEST D'ESAME ---")
        for frase, atteso in frasi_esame:
            risultato = converti_in_yoda(frase)
            if risultato == atteso:
                print(f"  CORRETTO (atteso: '{atteso}')")
            else:
                print(f" ERRORE: atteso '{atteso}', ottenuto '{risultato}'")
                
    elif args.frase:
        # frase da tastiera
        converti_in_yoda(args.frase)
        
    else:
        # Se non ha passato né frase da tastiera né flag --test, mostra l'help
        parser.print_help()
