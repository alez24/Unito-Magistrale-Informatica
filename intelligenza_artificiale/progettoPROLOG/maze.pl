:- module(maze, []).
:- use_module(search).

%%  Labirinto 5x8 (colonne 0..4, righe 0..7)
%%  Coordinate: pos(Col, Row), origine in alto-sinistra
%%
%%  Mura extra (oltre ai bordi):
%%    colonna 4 completamente bloccata (crea zona irraggiungibile)
%%    alcune pareti interne
%%
%%  Uscite: pos(0,0) e pos(4,7)
%%  L'uscita pos(4,7) non e' raggiungibile da pos(0,7) a causa della colonna 4.

:- discontiguous maze_wall/2.

maze_cols(5).
maze_rows(8).

exit(pos(0,0)).
exit(pos(4,7)).

%% Mura interne (coppie di celle adiacenti bloccate in entrambe le direzioni)
maze_wall(pos(0,4), pos(1,4)).
maze_wall(pos(1,0), pos(1,1)).
maze_wall(pos(1,2), pos(1,3)).
maze_wall(pos(1,4), pos(2,4)).
maze_wall(pos(1,6), pos(1,7)).
maze_wall(pos(2,4), pos(3,4)).
maze_wall(pos(3,1), pos(3,2)).
maze_wall(pos(3,4), pos(4,4)).
%% Tutta la colonna 4 e' separata dal resto (blocca l'uscita destra)
maze_wall(pos(3,0), pos(4,0)).
maze_wall(pos(3,1), pos(4,1)).
maze_wall(pos(3,2), pos(4,2)).
maze_wall(pos(3,3), pos(4,3)).
maze_wall(pos(3,4), pos(4,4)).
maze_wall(pos(3,5), pos(4,5)).
maze_wall(pos(3,6), pos(4,6)).
maze_wall(pos(3,7), pos(4,7)).

blocked(A, B) :- maze_wall(A, B).
blocked(A, B) :- maze_wall(B, A).

in_bounds(pos(C, R)) :-
    maze_cols(Cols), maze_rows(Rows),
    C >= 0, C < Cols,
    R >= 0, R < Rows.

maze_move(pos(C, R), pos(C1, R), 1) :- C1 is C + 1.
maze_move(pos(C, R), pos(C1, R), 1) :- C1 is C - 1.
maze_move(pos(C, R), pos(C, R1), 1) :- R1 is R + 1.
maze_move(pos(C, R), pos(C, R1), 1) :- R1 is R - 1.

maze_successors(State, NS, Cost) :-
    maze_move(State, NS, Cost),
    in_bounds(NS),
    \+ blocked(State, NS).

maze_goal(State) :- exit(State).

maze_heuristic(State, H) :-
    findall(D, (exit(E), manhattan(State, E, D)), Ds),
    min_list(Ds, H).

manhattan(pos(C1,R1), pos(C2,R2), D) :-
    D is abs(C1-C2) + abs(R1-R2).

%%  Esegui entrambi gli algoritmi su un caso e stampa il confronto
run_maze(Start) :-
    format("~n=== LABIRINTO: start=~w ===~n", [Start]),

    % A*
    statistics(runtime, [T0a|_]),
    (a_star(maze_goal, maze_successors, maze_heuristic, Start, PathA, CostA, StatsA) ->
        statistics(runtime, [T1a|_]),
        TimeA is T1a - T0a,
        length(PathA, LenA),
        StatsA = stats(ExpA, MaxOpenA),
        format("A*   : costo=~w  nodi-percorso=~w  espansi=~w  max-open=~w  tempo=~wms~n",
               [CostA, LenA, ExpA, MaxOpenA, TimeA])
    ;
        statistics(runtime, [T1a|_]),
        TimeA is T1a - T0a,
        format("A*   : nessuna soluzione trovata  tempo=~wms~n", [TimeA])
    ),

    % IDA*
    statistics(runtime, [T0i|_]),
    (ida_star(maze_goal, maze_successors, maze_heuristic, Start, PathI, CostI, StatsI) ->
        statistics(runtime, [T1i|_]),
        TimeI is T1i - T0i,
        length(PathI, LenI),
        StatsI = stats(ItrsI, TotExpI),
        format("IDA* : costo=~w  nodi-percorso=~w  iterazioni=~w  espansi=~w  tempo=~wms~n",
               [CostI, LenI, ItrsI, TotExpI, TimeI])
    ;
        statistics(runtime, [T1i|_]),
        TimeI is T1i - T0i,
        format("IDA* : nessuna soluzione trovata  tempo=~wms~n", [TimeI])
    ).

%%  Demo: mostra il percorso trovato da A*
show_path_astar(Start) :-
    (a_star(maze_goal, maze_successors, maze_heuristic, Start, Path, Cost, _) ->
        format("Percorso A* da ~w (costo ~w):~n", [Start, Cost]),
        maplist([P]>>(format("  ~w~n",[P])), Path)
    ;
        format("Nessun percorso da ~w~n", [Start])
    ).

:- initialization(main, main).

main :-
    format("~n*** DOMINIO LABIRINTO ***~n"),
    % Caso 1: raggiunge uscita pos(0,0)
    run_maze(pos(2,5)),
    % Caso 2: parte da zona isolata dalla colonna-4 – nessuna uscita raggiungibile
    run_maze(pos(4,3)),
    % Caso 3: partenza vicino all'uscita
    run_maze(pos(1,1)),
    halt.
