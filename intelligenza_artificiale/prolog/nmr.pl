uccello(X):-pinguino(X).
vola(X):-uccello(X),\+pinguino(X).
uccello(titty).
pinguino(tux).
pinguino(titty).