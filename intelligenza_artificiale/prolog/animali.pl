:- discontiguous uccello/1.

gatto(tom).
uccello(titty).
pinguino(tux).
mangia(titty,pavesino).

graffia(X):-gatto(X). %lettera maiuscola in Prolog indica variabile
vola(X):- uccello(X),\+pinguino(X). %\+ è la negazione in Prolog, quindi questa regola dice che un uccello può volare se non è un pinguino
uccello(X):-pinguino(X).
felino(X):-gatto(X).