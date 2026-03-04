/*tutti postitivi(lista)
    true se e solo se tutti gli elementi di lista sono > 0

    */

    tuttiPositivi([]).
    tuttiPositivi([Head|Tail]) :-
        atomic(Head),
        Head > 0,
        tuttiPositivi(Tail).
    tuttiPositivi([Head|Tail]):-
        is_list(Head),
        tuttiPositivi(Head),
        tuttiPositivi(Tail).


    ContaPositivi([], 0).
    ContaPositivi([Head|Tail], Risultato) :-
        atomic(Head),
        Head > 0,
        ContaPositivi(Tail, Tot),
        Risultato is Tot + 1.
    ContaPositivi([Head|Tail], Risultato) :-
        atomic(Head),
        Head =< 0,
        ContaPositivi(Tail, Risultato).
    ContaPositivi([Head|Tail], Risultato) :-
        is_list(Head),
        ContaPositivi(Head, Tot1),
        ContaPositivi(Tail, Tot2),
        Risultato is Tot1 + Tot2.