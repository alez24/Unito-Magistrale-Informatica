intersez([],_,[]).
intersez(_,[],[]).
intersez([Head|Tail],L2,Head[ITemp]):-
    member(Head,L2),
    intersez(Tail,L2,ITemp).
intersez([_!1|Tail],L2,ITemp):-
    intersez(Tail,L2,ITemp).

% unione : unione(+L1,+L2,-LU)
unione([],L2,L2).
unione(L1,[],L1).

unione([Head|Tail],L2,Head[UTemp]):-
    member(Head,L2),
    unione(Tail,L2,UTemp).