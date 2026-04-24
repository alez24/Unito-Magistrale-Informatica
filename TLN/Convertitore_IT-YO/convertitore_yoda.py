"""
=============================================================
  CONVERTITORE LESSICALE ITALIANO → YODA (IT-YO)
=============================================================
"""
import argparse
import json

# ===========================================================
# GRAMMATICA CFG IN CNF
# ===========================================================

def carica_dizionari(file_regole='regole_binarie.json', file_lessico='Lexicon.json'):
    """
    Carica le regole grammaticali e il lessico dai file JSON esterni.
    Converte le chiavi testuali delle regole (es. "NP,VP") nelle
    tuple richieste dall'algoritmo CKY (es. ('NP', 'VP')).
    """
    # Carica Lexicon
    with open(file_lessico, 'r', encoding='utf-8') as f:
        lexicon_data = json.load(f)
        
    # Carica regole 
    with open(file_regole, 'r', encoding='utf-8') as f:
        rules_data = json.load(f)
        
    # Riconversione delle chiavi in Tuple per l'algoritmo CKY
    binary_rules_data = {}
    for key, value in rules_data.items():
        # Splitta la stringa "Cat1,Cat2" in due elementi
        elemento1, elemento2 = key.split(',')
        tupla_chiave = (elemento1.strip(), elemento2.strip())
        binary_rules_data[tupla_chiave] = value
        
    return binary_rules_data, lexicon_data

# Inizializzazione globale delle strutture dati
BINARY_RULES, LEXICON = carica_dizionari()

# ===========================================================
# ALBERO DI DERIVAZIONE
# ===========================================================

class Nodo:
    """nodo geneerico dell'albero di derivazione."""

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

def pretty_print(self, prefix="", is_last=True):
        """Stampa albero leggibile nel terminale."""
        # Se alla radice non stampa i connettori (prefix = vuoto)
        if not prefix:
            print(self.label)
            new_prefix = ""
        else:
            #connettori grafici
            connector = "└── " if is_last else "├── "
            if self.is_leaf():
                print(f"{prefix}{connector}{self.label}: '{self.word}'")
            else:
                print(f"{prefix}{connector}{self.label}")
            # Aggiorniamo prefisso per i figli successivi: se questo nodo era l'ultimo, lascia vuoto, altrimenti mette linea verticale
            new_prefix = prefix + ("    " if is_last else "│   ")
            
        # Chiamata ricorsiva sui figli
        for i, child in enumerate(self.children):
            last_child = (i == len(self.children) - 1)
            child.pretty_print(new_prefix, last_child)


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

    # Trasforma ricorsivamente i figli
    nuovi_figli = [trasforma_in_yoda(f) for f in nodo.children]
    nodo.children = nuovi_figli

    # Regola di trasformazione principale: S → NP VP
    if nodo.label == 'S' and len(nodo.children) == 2:
        sogg = nodo.children[0]   # NP (soggetto)
        vp   = nodo.children[1]   # VP

        if vp.label == 'VP' and len(vp.children) == 2:
            child0 = vp.children[0]
            child1 = vp.children[1]

            # Caso 1: VP → V NP/PP/Adj
            if child0.label == 'V' and child1.label in ('NP', 'PP', 'Adj'):
                verbo = child0
                compl = child1
                nodo.label = 'S_yoda'
                nodo.children = [compl, sogg, verbo]

            # Caso 2: VP → VP1 Adv
            # VP1 → V NP: NP va in testa, Adv resta in coda
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
    print(f" La tua frase:  {frase_stringa}")
    print(f"{'='*55}")

    # Parsing CKY
    albero = cky_parse(parole)

    if albero is None:
        print(" Parsing fallito :( -> la frase non è riconosciuta dalla grammatica.")
        return None

    print("\nAlbero di derivazione:")
    albero.pretty_print(indent=2)

    # Trasformazione SVX → XSV
    print("\nTrasformazione in ordine Yoda")
    albero_yoda = trasforma_in_yoda(albero)
    print("\nAlbero Yoda:")
    albero_yoda.pretty_print(indent=2)

    # Raccolta delle foglie
    foglie = raccogli_foglie(albero_yoda)

    # Post-processing: maiuscole/minuscole stile frase, poi capitalizza la prima parola della frase Yoda.
    nomi_propri = {w for w, tags in LEXICON.items() if 'N' in tags and 'NP' in tags and w[0].isupper()}
    foglie = [w if w in nomi_propri else w.lower() for w in foglie]
    if foglie:
        foglie[0] = foglie[0].capitalize()
    frase_yoda = ' '.join(foglie)

    print(f"\n  Frase in Yoda: {frase_yoda}")
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
    # nargs='?' -> argomento è opzionale
    parser.add_argument(
        "frase", 
        type=str, 
        nargs='?', 
    )
    
    # Aggiunge flag --test per eseguire frasi preimpostate
    parser.add_argument(
        "--test", 
        action="store_true", 
    )

    # Legge argomenti da terminale
    args = parser.parse_args()

    print("\n" + "="*55)
    print("  CONVERTITORE ITALIANO → ITALIANO-YODA")
    print("="*55)

    # logica di esecuzione
    if args.test:
        #flag --test
        frasi_esempio = [
            ("Tu hai amici lì",                    "Amici tu hai lì"),
            ("Tu avrai novecento anni di età",      "Novecento anni di età tu avrai"),
            ("Noi siamo illuminati",                "Illuminati noi siamo"),
        ]
        print("\n--- ESECUZIONE TEST ---")
        for frase, atteso in frasi_esempio:
            risultato = converti_in_yoda(frase)
            if risultato == atteso:
                print(f"  CORRETTO (atteso: '{atteso}')")
            else:
                print(f" ERRORE: atteso '{atteso}', ottenuto '{risultato}'")
                
    elif args.frase:
        #frase da tastiera
        converti_in_yoda(args.frase)
        
