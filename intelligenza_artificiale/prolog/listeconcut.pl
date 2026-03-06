/* tuttiPositivi(Lista) 
   true se e solo se tutti gli elementi di Lista sono > 0
*/
tuttiPositivi([]).
tuttiPositivi([Head|Tail]):-
    atomic(Head),
    Head > 0,
    tuttiPositivi(Tail).
tuttiPositivi([Head|Tail]):-
    is_list(Head),
    tuttiPositivi(Head),
    tuttiPositivi(Tail).

/* contaPositivi(+Lista,-Quanti) */
contaPositivi([],0).
contaPositivi([Head|Tail],Risultato):-
    Head > 0,!,
    contaPositivi(Tail,Tot),
    Risultato is Tot+1.
contaPositivi([_|Tail],Tot):-
    contaPositivi(Tail,Tot).

/* sottolista(+L,-S).
   Esempio: [[1,2,3],1,[2,3],ciccio,[fa,do],-67]
   Successo con [fa,do]
   Fallimento con -67
   Fallimento con [1,[2,3]]
*/
sottolista([Head|_],Head):-is_list(Head),!.
sottolista([_|Tail],R):-sottolista(Tail,R).

prova(X):-member(X,[1,2,3,4,5]),!,member(X,[4,5,10,50]).
prova(152).