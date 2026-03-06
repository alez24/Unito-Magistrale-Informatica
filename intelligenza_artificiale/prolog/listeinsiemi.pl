% intersezione di due set: intersez(+L1,+L2,-LI)
intersez([],_,[]).
intersez(_,[],[]).
intersez([Head|Tail],L2,[Head|ITemp]):-
    member(Head,L2),!,
    intersez(Tail,L2,ITemp).
intersez([_|Tail],L2,ITemp):-
    intersez(Tail,L2,ITemp).

% unione: unione(+L1,+L2,-LU)
unione([],L2,L2):-!.
unione(L1,[],L1):-!.
unione([Head|Tail],L2,UTemp):-
    member(Head,L2),!,
    unione(Tail,L2,UTemp).
unione([Head|Tail],L2,[Head|UTemp]):-
    unione(Tail,L2,UTemp).

% Differenza: diff(+L1,+L2,-LD)
diff([],_,[]):-!.
diff([Head|Tail],L2,[Head|DTemp]):-
    \+member(Head,L2),!,
    diff(Tail,L2,DTemp).
diff([_|Tail],L2,DTemp):-
    diff(Tail,L2,DTemp).