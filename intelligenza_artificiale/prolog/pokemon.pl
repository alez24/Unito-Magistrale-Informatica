haTipo(pichu, elettro).
haTipo(emboar, fuoco).
haTipo(piplup, acqua). 
haTipo(volcanion, fuoco).
haTipo(volcanion, acqua).
esegue(fuoco,lanciafiamme).
esegue(elettro,fulmine).
esegue(acqua,idropulsar).
esegue(acqua,surf).
esegueMossa(Pokemon,Mossa):-haTipo(Pokemon,T),esegue(T,Mossa).