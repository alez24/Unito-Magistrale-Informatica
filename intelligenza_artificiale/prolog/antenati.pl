genitore(edoardo,gianni).
genitore(edoardo,clara).
genitore(edoardo,susanna).
genitore(edoardo,umberto).
genitore(edoardo,mariasole).
genitore(edoardo,giorgio).
genitore(edoardo,cristiana).
genitore(virginiaBourbon,gianni).
genitore(virginiaBourbon,clara).
genitore(virginiaBourbon,susanna).
genitore(virginiaBourbon,umberto).
genitore(virginiaBourbon,mariasole).
genitore(virginiaBourbon,giorgio).
genitore(virginiaBourbon,cristiana).
genitore(gianni,margherita).
genitore(marellaCaracciolo,margherita).
genitore(gianni,edoardo2).
genitore(marellaCaracciolo,edoardo2).
genitore(margherita,johnElkann).
genitore(alainElkann,johnElkann).
genitore(margherita,lapoElkann).
genitore(alainElkann,lapoElkann).
genitore(margherita,ginevraElkann).
genitore(alainElkann,ginevraElkann).
genitore(umberto,giovanni).
genitore(antonellaBechiPiaggio,giovanni).
genitore(umberto,andrea).
genitore(umberto,anna).
genitore(allegraCaracciolo,andrea).
genitore(allegraCaracciolo,anna).

nonno(X,Y) :- genitore(X,Z), genitore(Z,Y).

antenato(X,Y) :- antenato(X,Z), genitore(Z,Y).

fratelli_unilaterali(X,Y):-
    X==Y,
    genitore(GenComune,X),
    genitore(GenComune,Y),
    genitore(GenX,X),
    GenX==GenComune,
    genitore(GenY,Y),
    genitore(GenY,Y),
    GenY==GenComune,
    GenY==GenX,
    X==Y.