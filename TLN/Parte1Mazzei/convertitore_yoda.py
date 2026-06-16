"""
Convertitore lessicale Italiano -> Italiano-Yoda.

Esegue il parsing di una frase italiana tramite l'algoritmo CKY su una
grammatica context-free in forma normale di Chomsky, quindi trasforma
l'albero di derivazione per produrre l'ordine delle parole tipico di
Yoda (complemento - soggetto - verbo).
"""
import argparse
import json
import sys

# Garantisce l'output corretto di accenti e caratteri Unicode (es. └── ├──)
# anche su console Windows con codifica predefinita diversa da UTF-8.
sys.stdout.reconfigure(encoding='utf-8')

# Caricamento grammatica e lessico

def carica_dizionari(file_regole='regole_binarie.json', file_lessico='Lexicon.json'):
    """
    Carica le regole grammaticali e il lessico dai file JSON esterni.

    Le chiavi testuali delle regole binarie (es. "NP,VP") vengono
    convertite nelle tuple richieste dall'algoritmo CKY (es. ('NP', 'VP')).
    """
    with open(file_lessico, 'r', encoding='utf-8') as f:
        lexicon_data = json.load(f)

    with open(file_regole, 'r', encoding='utf-8') as f:
        rules_data = json.load(f)

    binary_rules_data = {}
    for key, value in rules_data.items():
        elemento1, elemento2 = key.split(',')
        tupla_chiave = (elemento1.strip(), elemento2.strip())
        binary_rules_data[tupla_chiave] = value

    return binary_rules_data, lexicon_data


BINARY_RULES, LEXICON = carica_dizionari()

# Albero di derivazione

class Nodo:
    """Nodo dell'albero di derivazione sintattica."""

    def __init__(self, label, children=None, word=None):
        self.label = label
        self.children = children or []
        self.word = word

    def is_leaf(self):
        return len(self.children) == 0

    def __repr__(self):
        if self.is_leaf():
            return f"[{self.label}: '{self.word}']"
        figli = ', '.join(repr(c) for c in self.children)
        return f"[{self.label} -> {figli}]"

    def pretty_print(self, prefix="", is_last=True, is_root=True):
        """Stampa l'albero in formato leggibile su terminale."""
        if is_root:
            print(self.label)
            new_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            if self.is_leaf():
                print(f"{prefix}{connector}{self.label}: '{self.word}'")
            else:
                print(f"{prefix}{connector}{self.label}")
            new_prefix = prefix + ("    " if is_last else "│   ")

        for i, child in enumerate(self.children):
            last_child = (i == len(self.children) - 1)
            child.pretty_print(new_prefix, is_last=last_child, is_root=False)


# Algoritmo CKY

def cky_parse(sentence, binary_rules=BINARY_RULES, lexicon=LEXICON):
    """
    Esegue il parsing CKY su una lista di parole.

    Restituisce il primo albero di derivazione trovato con radice 'S',
    oppure None se la frase non è riconosciuta dalla grammatica.
    """
    words = sentence
    n = len(words)

    # table[i][j] = dizionario {simbolo grammaticale: nodo già costruito}
    table = [[{} for _ in range(n)] for _ in range(n)]

    for i, word in enumerate(words):
        if word in lexicon:
            for pos_tag in lexicon[word]:
                leaf = Nodo(label=word, word=word)
                table[i][i][pos_tag] = Nodo(label=pos_tag, children=[leaf])

    for span in range(2, n + 1):
        for i in range(n - span + 1):
            j = i + span - 1
            for k in range(i, j):
                for (B, C), parents in binary_rules.items():
                    if B in table[i][k] and C in table[k + 1][j]:
                        for A in parents:
                            if A not in table[i][j]:
                                node_B = table[i][k][B]
                                node_C = table[k + 1][j][C]
                                table[i][j][A] = Nodo(
                                    label=A,
                                    children=[node_B, node_C]
                                )

    if 'S' in table[0][n - 1]:
        return table[0][n - 1]['S']
    return None


# Trasformazione dell'albero: SVX -> XSV

def trasforma_in_yoda(nodo):
    """
    Applica ricorsivamente la trasformazione sintattica Yoda
    all'albero di derivazione, anteponendo il complemento al
    soggetto e al verbo (S -> NP VP diventa S_yoda -> compl, sogg, verbo).
    """
    if nodo.is_leaf():
        return nodo

    nuovi_figli = [trasforma_in_yoda(f) for f in nodo.children]
    nodo.children = nuovi_figli

    if nodo.label == 'S' and len(nodo.children) == 2:
        sogg = nodo.children[0]
        vp = nodo.children[1]

        if vp.label == 'VP' and len(vp.children) == 2:
            child0 = vp.children[0]
            child1 = vp.children[1]

            # Caso 1: VP -> V (NP | PP | Adj)
            if child0.label == 'V' and child1.label in ('NP', 'PP', 'Adj'):
                verbo = child0
                compl = child1
                nodo.label = 'S_yoda'
                nodo.children = [compl, sogg, verbo]

            # Caso 2: VP -> VP1 Adv, con VP1 -> V NP
            elif child0.label == 'VP1' and child1.label == 'Adv':
                vp1 = child0
                adv = child1
                if len(vp1.children) == 2 and vp1.children[0].label == 'V':
                    verbo = vp1.children[0]
                    compl = vp1.children[1]
                    nodo.label = 'S_yoda'
                    nodo.children = [compl, sogg, verbo, adv]

        # Caso 3: VP -> V (verbo intransitivo, nessun complemento da anteporre)
        elif vp.label == 'VP' and len(vp.children) == 1:
            verbo = vp.children[0]
            nodo.label = 'S_yoda'
            nodo.children = [sogg, verbo]

    return nodo


# Estrazione della frase finale

def raccogli_foglie(nodo):
    """Visita l'albero in profondità e restituisce le parole foglia, da sinistra a destra."""
    if nodo.is_leaf():
        return [nodo.word]

    parole = []
    for figlio in nodo.children:
        parole.extend(raccogli_foglie(figlio))
    return parole


def converti_in_yoda(frase_stringa):
    """
    Converte una frase italiana nella sua versione in ordine Yoda.

    Esegue il parsing CKY, trasforma l'albero risultante e ricompone
    la frase a partire dalle foglie dell'albero trasformato.
    """
    parole = frase_stringa.strip().split()

    print("\n" + "-" * 50)
    print(f"Frase originale:  {frase_stringa}")
    print("-" * 50)

    albero = cky_parse(parole)

    if albero is None:
        print("Esito:            parsing fallito, frase non riconosciuta dalla grammatica.")
        return None

    print("\n[1] Albero di derivazione:\n")
    albero.pretty_print()

    print("\n[2] Trasformazione in ordine Yoda:\n")
    albero_yoda = trasforma_in_yoda(albero)
    albero_yoda.pretty_print()

    foglie = raccogli_foglie(albero_yoda)

    # Normalizzazione maiuscole/minuscole: i nomi propri restano invariati,
    # le altre parole sono minuscole; la prima parola della frase è capitalizzata.
    nomi_propri = {w for w, tags in LEXICON.items() if 'N' in tags and 'NP' in tags and w[0].isupper()}
    foglie = [w if w in nomi_propri else w.lower() for w in foglie]
    if foglie:
        foglie[0] = foglie[0].capitalize()
    frase_yoda = ' '.join(foglie)

    print(f"\n[3] Frase in Yoda: {frase_yoda}")
    print("-" * 50)

    return frase_yoda


# Interfaccia da riga di comando

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convertitore Italiano -> Italiano-Yoda",
        epilog="Esempio d'uso: python convertitore_yoda.py 'Tu hai amici lì'"
    )
    parser.add_argument(
        "frase",
        type=str,
        nargs='?',
        help="Frase italiana da convertire"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Esegue una suite di frasi di esempio con esito atteso"
    )

    args = parser.parse_args()

    print("CONVERTITORE ITALIANO -> ITALIANO-YODA")

    if args.test:
        frasi_esempio = [
            ("Tu hai amici lì",                "Amici tu hai lì"),
            ("Tu avrai novecento anni di età", "Novecento anni di età tu avrai"),
            ("Noi siamo illuminati",           "Illuminati noi siamo"),
        ]
        print(f"Modalità test: {len(frasi_esempio)} frasi di esempio")

        esiti = []
        for frase, atteso in frasi_esempio:
            risultato = converti_in_yoda(frase)
            esito = (risultato == atteso)
            esiti.append(esito)
            stato = "CORRETTO" if esito else "ERRORE"
            print(f"Esito:            {stato} (atteso: '{atteso}', ottenuto: '{risultato}')")

        print(f"\nRiepilogo test: {sum(esiti)}/{len(esiti)} superati")

    elif args.frase:
        converti_in_yoda(args.frase)
