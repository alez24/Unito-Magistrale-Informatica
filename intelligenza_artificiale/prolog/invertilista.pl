inverti(Lista,LInv):-
    inv(Lista,[],LInv).

inv([],LInv,LInv).
inv([Head|Tail],Temp,LInv):-
    inv(Tail,[Head|Temp],LInv).