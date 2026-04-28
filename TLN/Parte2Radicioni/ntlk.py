import nltk

grammar = nltk.CFG.fromstring("""
S -> SN SV
SN -> PRON
SV -> V SN
PRON -> 'Tu'
V -> 'hai'
SN -> 'amici'
""")

parser = nltk.ChartParser(grammar)
sent = ['Tu', 'hai', 'amici']
for tree in parser.parse(sent):
    print(tree)
    tree.pretty_print()