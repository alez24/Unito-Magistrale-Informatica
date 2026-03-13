:- encoding(utf8).
% ============================================================
%  ATTIVITA 1 - IDA* e A* in Prolog
%  Domini: Labirinto e Puzzle dell''8
% ============================================================
%
%  Questo file implementa le strategie di ricerca informata
%  A* e IDA* in modo generico, applicandole a due domini:
%
%    1) Labirinto (griglia con muri e almeno due uscite)
%    2) Puzzle dell''8 (griglia 3x3 con tessere numerate)
%
%  L''interfaccia generica move/4, heuristic/3, goal/2 permette
%  di scrivere A* e IDA* una sola volta e riutilizzarli su
%  qualsiasi dominio.
%
%  Euristica usata: distanza di Manhattan (ammissibile e consistente)
%  per entrambi i domini.
%
%  Uso rapido:  ?- run_all.
% ============================================================

% ============================================================
%  UTILITA GENERALI
% ============================================================
%  Predicati ausiliari per operazioni su liste, usati
%  internamente dalle euristiche e dagli algoritmi.
% ============================================================

% min_list(+Lista, -Min)
% Caso base: lista con un solo elemento, il minimo e' l''elemento stesso.
% Passo ricorsivo: confronta la testa con il minimo del resto.
min_list([X], X).
min_list([X|Rest], Min) :-
    min_list(Rest, M1),
    Min is min(X, M1).

% sumlist(+Lista, -Somma)
% Somma tutti gli elementi di una lista numerica.
% Usato dall''euristica del puzzle per sommare le distanze Manhattan.
sumlist([], 0).
sumlist([H|T], S) :- sumlist(T, S1), S is S1 + H.

% numlist(+Low, +High, -List)
% Genera la lista di interi da Low a High (inclusi).
% Usato nella generazione casuale del labirinto.
numlist(L, H, []) :- L > H, !.
numlist(L, H, [L|T]) :- L1 is L + 1, numlist(L1, H, T).

% ============================================================
%  DOMINIO 1 - LABIRINTO
% ============================================================
%
%  RAPPRESENTAZIONE DELLO STATO:
%    Ogni cella e' rappresentata come pos(Riga, Colonna).
%    Lo stato e' semplicemente la posizione corrente dell''agente.
%
%  STRUTTURA:
%    - wall(R, C)      : la cella (R,C) e' un muro (non percorribile)
%    - maze_exit(pos(R,C)) : la cella (R,C) e' un''uscita
%    - maze_start(pos(R,C)): posizione iniziale
%
%  Il testo richiede almeno due uscite, non necessariamente
%  raggiungibili. Questo labirinto statico ne ha due:
%    pos(5,5) e pos(1,5).
%
%  Labirinto di esempio (5x5, S=start, E=uscita, #=muro):
%
%    Col:  1   2   3   4   5
%   Riga
%    1:    S   .   .   #   E    <- uscita in pos(1,5)
%    2:    .   #   .   #   .
%    3:    .   #   .   .   .
%    4:    .   .   #   .   .
%    5:    .   #   .   .   E    <- uscita in pos(5,5)
%
%  MOSSE: su, giu', sinistra, destra (costo uniforme = 1).
%  Una mossa e' valida se la cella di arrivo e' dentro la griglia
%  e non e' un muro.
% ============================================================

:- dynamic maze_size_dyn/2.
:- dynamic wall/2.
:- dynamic maze_exit/1.
maze_size_dyn(5, 5).

% maze_size(-Righe, -Colonne)
% Restituisce le dimensioni attuali del labirinto (default 5x5).
maze_size(R, C) :- maze_size_dyn(R, C).

% set_maze_size(+Righe, +Colonne)
% Permette di cambiare dinamicamente la dimensione del labirinto.
% Esempio: ?- set_maze_size(10, 10).
set_maze_size(R, C) :-
    retractall(maze_size_dyn(_, _)),
    assertz(maze_size_dyn(R, C)).

% Muri (celle non percorribili)
% Corrispondono ai '#' nello schema sopra.
wall(1, 4).
wall(2, 2). wall(2, 4).
wall(3, 2).
wall(4, 3).
wall(5, 2).

% Uscite del labirinto (almeno due, come richiesto dal testo).
% NOTA: il testo specifica che le uscite non sono necessariamente
% raggiungibili. In questo caso entrambe sono raggiungibili.
maze_exit(pos(5, 5)).
maze_exit(pos(1, 5)).

% Stato iniziale: angolo in alto a sinistra.
maze_start(pos(1, 1)).

% ============================================================
%  GENERAZIONE CASUALE DEL LABIRINTO
% ============================================================
%
%  generate_random_maze/0 - genera un labirinto casuale 5x5,
%  lo stampa e aggiorna dinamicamente i fatti wall/2 e maze_exit/2.
%  La probabilita' di ogni cella di essere un muro e' ~30%.
%  Si garantisce che start e uscite non siano muri.
%
%  Uso: ?- generate_random_maze.
%       ?- generate_random_maze, run_all.

:- dynamic dyn_wall/2.
:- dynamic dyn_exit/1.

% Genjera il labirinto casuale garantendo che sia risolvibile
generate_random_maze :-
    generate_until_solvable,
    print_random_maze.

generate_until_solvable :-
    maze_size(Rows, Cols),
    retractall(dyn_wall(_, _)),
    retractall(dyn_exit(_)),
    numlist(1, Rows, Rs),
    numlist(1, Cols, Cs),
    forall(
        (member(R, Rs), member(C, Cs),
         \+ (R =:= 1, C =:= 1),
         \+ (R =:= 1, C =:= Cols),
         \+ (R =:= Rows, C =:= Cols)
        ),
        (   maybe(0.40) -> assertz(dyn_wall(R, C)) ; true )
    ),
    assertz(dyn_exit(pos(1, Cols))),
    assertz(dyn_exit(pos(Rows, Cols))),
    maze_start(Start),
    (   reachable_exit(Start)
    ->  true
    ;   write('Labirinto irrisolvibile, rigenero...'), nl,
        generate_until_solvable
    ).

% BFS semplice per verificare raggiungibilita' di un''uscita
reachable_exit(Start) :-
    bfs([Start], [Start]).

bfs([Current|_], _) :-
    dyn_exit(Current), !.
bfs([Current|Queue], Visited) :-
    findall(Next,
        (maze_move_dyn(Current, Next, _),
         \+ member(Next, Visited)),
        Neighbors),
    append(Queue, Neighbors, NewQueue),
    append(Visited, Neighbors, NewVisited),
    NewQueue \= [],
    bfs(NewQueue, NewVisited).

% Stampa il labirinto con i fatti dinamici
print_random_maze :-
    maze_size(Rows, Cols),
    write('+'), print_dashes(Cols), nl,
    print_rand_rows(1, Rows, Cols),
    write('+'), print_dashes(Cols), nl.

print_dashes(0).
print_dashes(N) :- N > 0, write('---+'), N1 is N-1, print_dashes(N1).

print_rand_rows(R, MaxR, _) :- R > MaxR, !.
print_rand_rows(R, MaxR, Cols) :-
    write('|'),
    print_rand_cols(R, 1, Cols),
    nl, R1 is R+1,
    print_rand_rows(R1, MaxR, Cols).

print_rand_cols(_, C, MaxC) :- C > MaxC, !.
print_rand_cols(R, C, MaxC) :-
    (   R =:= 1, C =:= 1          -> write(' S |')
    ;   dyn_exit(pos(R, C))        -> write(' E |')
    ;   dyn_wall(R, C)             -> write(' # |')
    ;                                 write('   |')
    ),
    C1 is C+1,
    print_rand_cols(R, C1, MaxC).

% Versione di run_all che usa il labirinto casuale
run_all_random :-
    generate_random_maze, nl,
    % Ridefinisce temporaneamente wall/2 e maze_exit/1
    % usando i predicati dinamici tramite override
    write('--- A* sul labirinto casuale ---'), nl,
    maze_start(Start),
    (   astar_dyn(Start, PathA, CostA, ExpA)
    ->  format('Percorso A*: ~w~n', [PathA]),
        format('Costo: ~w | Nodi espansi: ~w~n', [CostA, ExpA])
    ;   write('A*: nessuna soluzione raggiungibile.~n')
    ), nl,
    write('--- IDA* sul labirinto casuale ---'), nl,
    (   idastar_dyn(Start, PathI, CostI, ItersI)
    ->  format('Percorso IDA*: ~w~n', [PathI]),
        format('Costo: ~w | Iterazioni: ~w~n', [CostI, ItersI])
    ;   write('IDA*: nessuna soluzione raggiungibile.~n')
    ).

% A* e IDA* che usano dyn_wall/dyn_exit invece dei fatti statici
maze_move_dyn(pos(R,C), pos(R1,C), 1) :-
    R1 is R-1, maze_size(MaxR,_), R1>=1, R1=<MaxR, \+ dyn_wall(R1,C).
maze_move_dyn(pos(R,C), pos(R1,C), 1) :-
    R1 is R+1, maze_size(MaxR,_), R1>=1, R1=<MaxR, \+ dyn_wall(R1,C).
maze_move_dyn(pos(R,C), pos(R,C1), 1) :-
    C1 is C-1, maze_size(_,MaxC), C1>=1, C1=<MaxC, \+ dyn_wall(R,C1).
maze_move_dyn(pos(R,C), pos(R,C1), 1) :-
    C1 is C+1, maze_size(_,MaxC), C1>=1, C1=<MaxC, \+ dyn_wall(R,C1).

maze_h_dyn(pos(R,C), H) :-
    findall(D, (dyn_exit(pos(Re,Ce)), D is abs(R-Re)+abs(C-Ce)), Ds),
    min_list(Ds, H).

astar_dyn(Start, Path, Cost, Expanded) :-
    maze_h_dyn(Start, H),
    astar_loop_dyn([f(H,0,Start,[Start])], [], Path, Cost, 0, Expanded).

astar_loop_dyn([f(_,G,S,Rev)|_], _Closed, Path, G, Exp, Exp) :-
    dyn_exit(S), reverse(Rev, Path).
astar_loop_dyn([f(_,G,S,Rev)|Open], Closed, Path, Cost, Exp0, Exp) :-
    \+ dyn_exit(S),
    (   member(S, Closed)
    ->  astar_loop_dyn(Open, Closed, Path, Cost, Exp0, Exp)
    ;   Exp1 is Exp0+1,
        findall(f(F1,G1,S1,[S1|Rev]),
            (maze_move_dyn(S,S1,SC), \+ member(S1,Closed),
             G1 is G+SC, maze_h_dyn(S1,H1), F1 is G1+H1),
            Succs),
        insert_all(Succs, Open, Open1),
        astar_loop_dyn(Open1, [S|Closed], Path, Cost, Exp1, Exp)
    ).

idastar_dyn(Start, Path, Cost, Iters) :-
    maze_h_dyn(Start, H0),
    idastar_loop_dyn(Start, H0, Path, Cost, 0, Iters).

idastar_loop_dyn(Start, Bound, Path, Cost, I0, Iters) :-
    idastar_search_dyn(Start, 0, Bound, [Start], RP, RC, NB),
    (   RP \= failure
    ->  Path=RP, Cost=RC, Iters is I0+1
    ;   NB =\= 1.0e308,
        I1 is I0+1,
        idastar_loop_dyn(Start, NB, Path, Cost, I1, Iters)
    ).

idastar_search_dyn(S, G, _, Rev, Path, G, _) :-
    dyn_exit(S), reverse(Rev, Path), !.
idastar_search_dyn(S, G, Bound, Rev, Path, Cost, NB) :-
    maze_h_dyn(S, H), F is G+H,
    (   F > Bound
    ->  Path=failure, Cost=0, NB=F
    ;   findall(s(S1,SC),
            (maze_move_dyn(S,S1,SC), \+ member(S1,Rev)), Succs),
        search_succs_dyn(Succs, G, Bound, Rev, Path, Cost, 1.0e308, NB)
    ).

search_succs_dyn([], _, _, _, failure, 0, MN, MN).
search_succs_dyn([s(S,SC)|Rest], G, Bound, Rev, Path, Cost, MN0, MN) :-
    G1 is G+SC,
    idastar_search_dyn(S, G1, Bound, [S|Rev], SP, SC2, SN),
    (   SP \= failure
    ->  Path=SP, Cost=SC2, MN=MN0
    ;   MN1 is min(MN0,SN),
        search_succs_dyn(Rest, G, Bound, Rev, Path, Cost, MN1, MN)
    ).


% maze_move(+StatoCorrente, -StatoSuccessore, -Costo)
%
% Genera le mosse valide: su, giu', sinistra, destra.
% Ogni mossa ha costo uniforme 1.
% Una mossa e' valida se:
%   1) la cella risultante e' dentro i limiti della griglia
%   2) la cella risultante non e' un muro
%
% Mossa SU: la riga diminuisce di 1
maze_move(pos(R, C), pos(R1, C), 1) :-
    R1 is R - 1,
    maze_size(MaxR, _),
    R1 >= 1, R1 =< MaxR,
    \+ wall(R1, C).
% Mossa GIU': la riga aumenta di 1
maze_move(pos(R, C), pos(R1, C), 1) :-
    R1 is R + 1,
    maze_size(MaxR, _),
    R1 >= 1, R1 =< MaxR,
    \+ wall(R1, C).
% Mossa SINISTRA: la colonna diminuisce di 1
maze_move(pos(R, C), pos(R, C1), 1) :-
    C1 is C - 1,
    maze_size(_, MaxC),
    C1 >= 1, C1 =< MaxC,
    \+ wall(R, C1).
% Mossa DESTRA: la colonna aumenta di 1
maze_move(pos(R, C), pos(R, C1), 1) :-
    C1 is C + 1,
    maze_size(_, MaxC),
    C1 >= 1, C1 =< MaxC,
    \+ wall(R, C1).

% maze_heuristic(+Stato, -H)
%
% Euristica ammissibile per il labirinto: distanza Manhattan minima
% fra la posizione corrente e TUTTE le uscite disponibili.
%
% AMMISSIBILITA': la Manhattan non sovrastima mai il costo reale
% perche' nel labirinto ci si muove solo in orizzontale/verticale
% con costo 1 per passo, e la Manhattan conta esattamente i passi
% minimi senza ostacoli. Eventuali muri possono solo allungare
% il percorso reale => h(n) <= h*(n) sempre.
%
% Prendiamo il minimo tra le distanze verso le uscite perche'
% basta raggiungere una qualsiasi uscita.
maze_heuristic(pos(R, C), H) :-
    findall(D,
        (maze_exit(pos(Re, Ce)),
         D is abs(R - Re) + abs(C - Ce)),
        Ds),
    min_list(Ds, H).

% maze_goal(+Stato)
% Lo stato e' un goal se corrisponde a una delle uscite.
maze_goal(State) :- maze_exit(State).

% ============================================================
%  DOMINIO 2 - PUZZLE DELL'8
% ============================================================
%
%  RAPPRESENTAZIONE DELLO STATO:
%    Lo stato e' una lista di 9 elementi che rappresenta la griglia
%    3x3 letta riga per riga da sinistra a destra, dall''alto in basso.
%    La casella vuota e' rappresentata dal numero 0.
%
%  MAPPING INDICE -> POSIZIONE (indici 0-based):
%       Col: 0   1   2
%    Riga 0:  [0] [1] [2]
%    Riga 1:  [3] [4] [5]
%    Riga 2:  [6] [7] [8]
%
%    Riga = Indice // 3    (divisione intera)
%    Col  = Indice mod 3
%
%  Stato iniziale (dall''immagine del testo):
%    7 3 1         Stato goal (dall''immagine del testo):
%    5 _ 6   =>    1 2 3
%    8 2 4         4 5 6
%                  7 8 _
%
%  MOSSE: si "sposta" la casella vuota (0) scambiandola con un
%  vicino adiacente (su, giu', sinistra, destra). Costo = 1.
% ============================================================

% Stato iniziale e goal corrispondenti alle configurazioni nell''immagine.
puzzle_start([7,3,1,5,0,6,8,2,4]).
puzzle_goal([1,2,3,4,5,6,7,8,0]).

% blank_pos(+Stato, -Posizione)
% Trova l''indice 0-based della casella vuota (valore 0) nella lista.
blank_pos(State, Pos) :-
    nth0(Pos, State, 0).

% puzzle_move(+Stato, -NuovoStato, -Costo)
%
% Genera tutti gli stati successori validi spostando la casella vuota
% nelle 4 direzioni possibili. Ogni mossa ha costo 1.
%
% Griglia con indici:
%   [0] [1] [2]
%   [3] [4] [5]
%   [6] [7] [8]
%
% Vincoli per ogni direzione:
%   SU:       Blank >= 3 (non siamo nella prima riga)
%   GIU':     Blank =< 5 (non siamo nell''ultima riga)
%   SINISTRA: Blank mod 3 > 0 (non siamo nella prima colonna)
%   DESTRA:   Blank mod 3 < 2 (non siamo nell''ultima colonna)
%
puzzle_move(State, NewState, 1) :-
    blank_pos(State, Blank),
    (   % SU: la casella vuota scende di 3 indici (va nella riga sopra)
        Blank >= 3, Swap is Blank - 3
    ;   % GIU': la casella vuota sale di 3 indici (va nella riga sotto)
        Blank =< 5, Swap is Blank + 3
    ;   % SINISTRA: la casella vuota si sposta a sinistra di 1
        Col is Blank mod 3, Col > 0, Swap is Blank - 1
    ;   % DESTRA: la casella vuota si sposta a destra di 1
        Col is Blank mod 3, Col < 2, Swap is Blank + 1
    ),
    swap_elements(State, Blank, Swap, NewState).

% swap_elements(+Lista, +IndiceI, +IndiceJ, -NuovaLista)
% Scambia gli elementi alle posizioni I e J della lista.
% Prima estrae i due valori EI e EJ, poi ricostruisce la lista
% mettendo EJ dove c''era EI e viceversa.
swap_elements(State, I, J, NewState) :-
    nth0(I, State, EI),
    nth0(J, State, EJ),
    swap_build(State, 0, I, J, EI, EJ, NewState).

% swap_build/7 - Ricostruzione ricorsiva della lista con lo scambio.
% Scorre la lista elemento per elemento (Idx = contatore):
%   - se Idx == I: inserisce EJ al posto dell''elemento originale
%   - se Idx == J: inserisce EI al posto dell''elemento originale
%   - altrimenti: copia l''elemento invariato
swap_build([], _, _, _, _, _, []).
swap_build([_|T], Idx, I, J, EI, EJ, [EJ|Rest]) :-
    Idx =:= I, !,
    Idx1 is Idx + 1,
    swap_build(T, Idx1, I, J, EI, EJ, Rest).
swap_build([_|T], Idx, I, J, EI, EJ, [EI|Rest]) :-
    Idx =:= J, !,
    Idx1 is Idx + 1,
    swap_build(T, Idx1, I, J, EI, EJ, Rest).
swap_build([H|T], Idx, I, J, EI, EJ, [H|Rest]) :-
    Idx1 is Idx + 1,
    swap_build(T, Idx1, I, J, EI, EJ, Rest).

% puzzle_heuristic(+Stato, -H)
%
% Euristica: somma delle distanze Manhattan di ogni tessera.
%
% Per ogni tessera T (escluso lo 0 = vuoto):
%   1) Trova la posizione attuale di T nello stato corrente (Idx)
%   2) Trova la posizione goal di T nello stato obiettivo (GoalIdx)
%   3) Converte gli indici lineari in coordinate (riga, colonna)
%   4) Calcola |riga_attuale - riga_goal| + |col_attuale - col_goal|
%
% H = somma di tutte le distanze Manhattan.
%
% AMMISSIBILITA': ogni tessera deve percorrere ALMENO la sua
% distanza Manhattan per raggiungere la posizione goal (non ci sono
% scorciatoie nella griglia). Poiche' ad ogni mossa si sposta UNA
% sola tessera di UN passo, la somma delle Manhattan e' un lower
% bound sul numero di mosse necessarie => h(n) <= h*(n) sempre.
puzzle_heuristic(State, H) :-
    puzzle_goal(Goal),
    findall(D,
        (nth0(Idx, State, Tile),
         Tile \= 0,                              % ignora la casella vuota
         nth0(GoalIdx, Goal, Tile),               % posizione goal di questa tessera
         R1 is Idx // 3, C1 is Idx mod 3,         % coordinate attuali
         R2 is GoalIdx // 3, C2 is GoalIdx mod 3, % coordinate goal
         D is abs(R1 - R2) + abs(C1 - C2)),       % distanza Manhattan
        Ds),
    sumlist(Ds, H).

% puzzle_goal_check(+Stato)
% Vero se lo stato corrisponde alla configurazione goal.
puzzle_goal_check(State) :- puzzle_goal(State).

% ============================================================
%  GENERAZIONE CASUALE DEL PUZZLE DELL'8
% ============================================================
%
%  Genera una configurazione iniziale casuale RISOLVIBILE.
%
%  Non tutte le permutazioni di [0..8] sono risolvibili: esattamente
%  meta' (181440 su 362880) lo sono. Una permutazione e' risolvibile
%  se e solo se il numero di INVERSIONI e' PARI.
%
%  Inversione: una coppia (A, B) con A prima di B nella lista,
%  A > B, e nessuno dei due e' 0 (la casella vuota non conta).
%
%  Algoritmo:
%    1) Genera una permutazione casuale di [0,1,...,8]
%    2) Conta le inversioni (ignorando lo 0)
%    3) Se il numero e' pari => risolvibile, la usa
%    4) Se e' dispari => scambia due tessere non-zero per renderla pari
%
%  Uso:
%    ?- generate_random_puzzle(S), print_puzzle(S).
%    ?- run_puzzle_random.
% ============================================================

% generate_random_puzzle(-Stato)
% Genera una permutazione casuale risolvibile di [0..8].
generate_random_puzzle(State) :-
    random_permutation([0,1,2,3,4,5,6,7,8], Perm),
    (   solvable(Perm)
    ->  State = Perm
    ;   % Se non risolvibile, scambia le prime due tessere non-zero
        % per invertire la parita' delle inversioni
        fix_parity(Perm, State)
    ).

% solvable(+Permutazione)
% Vero se il numero di inversioni (escluso lo 0) e' pari.
solvable(Perm) :-
    count_inversions(Perm, N),
    N mod 2 =:= 0.

% count_inversions(+Lista, -NumInversioni)
% Conta le coppie (A, B) dove A appare prima di B, A > B,
% e nessuno dei due e' 0.
count_inversions(List, N) :-
    findall(1,
        (   append(_, [A|Rest], List),
            member(B, Rest),
            A \= 0, B \= 0,
            A > B
        ),
        Ones),
    length(Ones, N).

% fix_parity(+Perm, -Fixed)
% Scambia due tessere adiacenti non-zero per cambiare la parita'.
% Cerca le prime due posizioni non-zero e le scambia.
fix_parity(Perm, Fixed) :-
    nth0(I1, Perm, V1), V1 \= 0,
    nth0(I2, Perm, V2), V2 \= 0,
    I2 > I1, !,
    swap_elements(Perm, I1, I2, Fixed).

% run_puzzle_random/0
% Genera un puzzle casuale risolvibile, lo visualizza,
% poi confronta A* e IDA* sulla stessa configurazione.
%
% Esempio: ?- run_puzzle_random.
run_puzzle_random :-
    generate_random_puzzle(Start),
    nl, write('========================================='), nl,
    write('  PUZZLE CASUALE - Confronto A* vs IDA*'), nl,
    write('========================================='), nl, nl,
    write('Configurazione iniziale:'), nl,
    print_puzzle(Start), nl,
    write('Configurazione goal:'), nl,
    print_puzzle([1,2,3,4,5,6,7,8,0]), nl,
    % A*
    write('=== A* ==='), nl,
    statistics(walltime, [T0|_]),
    (   astar(puzzle, Start, PathA, CostA, ExpA)
    ->  statistics(walltime, [T1|_]),
        TimeA is T1 - T0,
        length(PathA, LenA), StepsA is LenA - 1,
        format('Passi: ~w~n', [StepsA]),
        format('Costo: ~w~n', [CostA]),
        format('Nodi espansi: ~w~n', [ExpA]),
        format('Tempo (ms): ~w~n', [TimeA])
    ;   write('Nessuna soluzione (errore: dovrebbe essere risolvibile!)'), nl
    ), nl,
    % IDA*
    write('=== IDA* ==='), nl,
    statistics(walltime, [T2|_]),
    (   idastar(puzzle, Start, PathI, CostI, ItersI)
    ->  statistics(walltime, [T3|_]),
        TimeI is T3 - T2,
        length(PathI, LenI), StepsI is LenI - 1,
        format('Passi: ~w~n', [StepsI]),
        format('Costo: ~w~n', [CostI]),
        format('Iterazioni IDA*: ~w~n', [ItersI]),
        format('Tempo (ms): ~w~n', [TimeI])
    ;   write('Nessuna soluzione (errore: dovrebbe essere risolvibile!)'), nl
    ), nl,
    write('========================================='), nl.

% ============================================================
%  A* GENERICO
% ============================================================
%
%  ALGORITMO A*:
%    A* e' un algoritmo di ricerca informata che esplora lo spazio
%    degli stati espandendo sempre il nodo con il valore f minimo,
%    dove f(n) = g(n) + h(n):
%      - g(n) = costo del percorso dallo start al nodo n
%      - h(n) = stima euristica del costo da n al goal
%
%    A* e' OTTIMALE (trova la soluzione di costo minimo) se l''euristica
%    e' ammissibile: h(n) <= costo_reale(n, goal) per ogni n.
%
%    A* e' COMPLETO: se esiste una soluzione, la trova.
%
%  STRUTTURE DATI:
%    - Frontiera (Open): lista ordinata per f crescente (coda di priorita')
%      Ogni nodo e': f(F, G, Stato, PercorsoInverso)
%    - Lista chiusa (Closed): lista di stati gia' espansi
%      Impedisce di rivisitare stati gia' esplorati.
% ============================================================

% insert_sorted(+Nodo, +ListaOrdinata, -NuovaListaOrdinata)
% Inserisce un nodo nella posizione corretta mantenendo l''ordinamento per F.
% Se F del nuovo nodo <= F della testa, lo mette in prima posizione.
insert_sorted(Node, [], [Node]).
insert_sorted(f(F1,G1,S1,P1), [f(F2,G2,S2,P2)|Rest],
              [f(F1,G1,S1,P1), f(F2,G2,S2,P2)|Rest]) :-
    F1 =< F2, !.
insert_sorted(Node, [Head|Tail], [Head|Sorted]) :-
    insert_sorted(Node, Tail, Sorted).

% insert_all(+ListaNodi, +Frontiera, -NuovaFrontiera)
% Inserisce tutti i nodi dalla lista nella frontiera ordinata, uno alla volta.
insert_all([], Open, Open).
insert_all([Node|Rest], Open, Open2) :-
    insert_sorted(Node, Open, Open1),
    insert_all(Rest, Open1, Open2).

% astar(+Dominio, +StatoIniziale, -Percorso, -Costo, -NodiEspansi)
%
% Entry point di A*.
% 1) Calcola h(start) per il nodo iniziale
% 2) Crea la frontiera iniziale con un solo nodo: f(h, 0, start, [start])
% 3) Avvia il loop principale
astar(Domain, Start, Path, Cost, Expanded) :-
    heuristic(Domain, Start, H),
    astar_loop(Domain, [f(H, 0, Start, [Start])], [], Path, Cost, 0, Expanded).

% astar_loop - CASO BASE (goal raggiunto):
%   Il nodo in testa alla frontiera (f minimo) e' un goal.
%   Invertiamo il percorso (era costruito al contrario) e lo restituiamo.
astar_loop(Domain, [f(_F, G, State, RevPath)|_], _Closed, Path, G, Exp, Exp) :-
    goal(Domain, State),
    reverse(RevPath, Path).

% astar_loop - CASO RICORSIVO (espansione):
%   1) Estraiamo il nodo con f minimo dalla frontiera
%   2) Se e' gia' nella lista chiusa, lo scartiamo (skip)
%   3) Altrimenti lo espandiamo:
%      a) Generiamo tutti i successori validi (non in closed)
%      b) Per ogni successore calcoliamo f = g + h
%      c) Inseriamo i successori nella frontiera ordinata
%      d) Aggiungiamo lo stato corrente alla lista chiusa
astar_loop(Domain, [f(_F, G, State, RevPath)|Open], Closed, Path, Cost, Exp0, Exp) :-
    \+ goal(Domain, State),
    (   member(State, Closed)
    ->  % Stato gia' espanso: lo saltiamo senza contarlo
        astar_loop(Domain, Open, Closed, Path, Cost, Exp0, Exp)
    ;   % Espansione: incrementa il contatore, genera i successori
        Exp1 is Exp0 + 1,
        findall(f(F1, G1, S1, [S1|RevPath]),
            (   move(Domain, State, S1, StepCost),
                \+ member(S1, Closed),
                G1 is G + StepCost,
                heuristic(Domain, S1, H1),
                F1 is G1 + H1
            ), Successors),
        insert_all(Successors, Open, Open1),
        astar_loop(Domain, Open1, [State|Closed], Path, Cost, Exp1, Exp)
    ).

% ============================================================
%  IDA* GENERICO
% ============================================================
%
%  ALGORITMO IDA* (Iterative Deepening A*):
%    Combina la completezza di A* con il basso consumo di memoria
%    della ricerca in profondita' (DFS).
%
%  FUNZIONAMENTO:
%    1) Inizializza un threshold (soglia) = h(start)
%    2) Ad ogni iterazione, esegue una DFS limitata:
%       - Espande i nodi con f(n) <= threshold
%       - Se f(n) > threshold, il nodo viene "tagliato" (cutoff)
%         e il suo valore f viene registrato come candidato
%         per il prossimo threshold
%    3) Se la DFS trova il goal, termina con successo
%    4) Se la DFS fallisce, il nuovo threshold diventa il MINIMO
%       tra tutti i valori f dei nodi tagliati
%    5) Se nessun nodo e' stato tagliato (next = infinito),
%       non esiste soluzione
%
%  VANTAGGI rispetto ad A*:
%    - Memoria O(d) invece di O(b^d) (dove d = profondita', b = branching)
%    - Non serve una lista chiusa globale ne' una frontiera ordinata
%
%  SVANTAGGI:
%    - Rivisita nodi nelle iterazioni successive (lavoro ridondante)
%
%  Per evitare cicli, IDA* controlla che ogni successore non sia
%  gia' presente nel percorso corrente (path checking).
%
%  Usiamo 1.0e308 come valore "infinito" per i next bound.
% ============================================================

% idastar(+Dominio, +StatoIniziale, -Percorso, -Costo, -NumIterazioni)
%
% Entry point di IDA*.
% Calcola h(start) come threshold iniziale e avvia il loop.
idastar(Domain, Start, Path, Cost, Iters) :-
    heuristic(Domain, Start, H0),
    idastar_loop(Domain, Start, H0, Path, Cost, 0, Iters).

% idastar_loop/7 - Loop principale delle iterazioni.
%
% Ad ogni iterazione:
%   1) Lancia la DFS con il Bound corrente
%   2) Se la DFS trova una soluzione (ResultPath \= failure) => successo
%   3) Se la DFS fallisce e NextBound == infinito => nessuna soluzione
%   4) Altrimenti, rilancia con il nuovo threshold = NextBound
idastar_loop(Domain, Start, Bound, Path, Cost, Iters0, Iters) :-
    idastar_search(Domain, Start, 0, Bound, [Start], ResultPath, ResultCost, NextBound),
    (   ResultPath \= failure
    ->  Path = ResultPath, Cost = ResultCost,
        Iters is Iters0 + 1
    ;   (   NextBound =:= 1.0e308
        ->  fail  % nessuna soluzione: nessun nodo e' stato tagliato
        ;   Iters1 is Iters0 + 1,
            idastar_loop(Domain, Start, NextBound, Path, Cost, Iters1, Iters)
        )
    ).

% idastar_search/8 - DFS ricorsiva con cutoff.
%
% CASO BASE: lo stato corrente e' il goal => inverti il percorso e ritorna.
idastar_search(Domain, State, G, _Bound, RevPath, Path, G, _) :-
    goal(Domain, State),
    reverse(RevPath, Path), !.

% CASO RICORSIVO:
%   1) Calcola f = g + h per lo stato corrente
%   2) Se f > threshold => CUTOFF: ritorna failure e f come next bound
%   3) Altrimenti => genera i successori (escludendo quelli gia' nel
%      percorso per evitare cicli) e li esplora ricorsivamente
idastar_search(Domain, State, G, Bound, RevPath, Path, Cost, NextBound) :-
    heuristic(Domain, State, H),
    F is G + H,
    (   F > Bound
    ->  Path = failure, Cost = 0, NextBound = F
    ;   findall(s(S1, StepCost),
            (   move(Domain, State, S1, StepCost),
                \+ member(S1, RevPath)   % evita cicli: path checking
            ), Succs),
        search_successors(Domain, Succs, G, Bound, RevPath, Path, Cost, 1.0e308, NextBound)
    ).

% search_successors/9 - Esplora ricorsivamente la lista dei successori.
%
% CASO BASE: nessun successore rimasto => failure.
%   Restituisce il minimo next bound accumulato (MinNext).
%
% CASO RICORSIVO: per ogni successore:
%   1) Calcola g1 = g + costo_passo
%   2) Chiama idastar_search ricorsivamente
%   3) Se trova una soluzione => la propaga verso l''alto
%   4) Se fallisce => aggiorna il minimo next bound e prosegue
%      col prossimo successore
search_successors(_, [], _, _, _, failure, 0, MinNext, MinNext).
search_successors(Domain, [s(S, SC)|Rest], G, Bound, RevPath, Path, Cost, MinNext0, MinNext) :-
    G1 is G + SC,
    idastar_search(Domain, S, G1, Bound, [S|RevPath], SubPath, SubCost, SubNext),
    (   SubPath \= failure
    ->  Path = SubPath, Cost = SubCost, MinNext = MinNext0
    ;   MinNext1 is min(MinNext0, SubNext),
        search_successors(Domain, Rest, G, Bound, RevPath, Path, Cost, MinNext1, MinNext)
    ).

% ============================================================
%  INTERFACCIA GENERICA (move/4, heuristic/3, goal/2)
% ============================================================
%
%  Questi predicati "ponte" collegano l''implementazione generica
%  di A* e IDA* ai predicati specifici di ogni dominio.
%
%  Per aggiungere un nuovo dominio basta definire:
%    - move(nuovo_dominio, Stato, Succ, Costo)
%    - heuristic(nuovo_dominio, Stato, H)
%    - goal(nuovo_dominio, Stato)
% ============================================================

% move(+Dominio, +Stato, -Successore, -Costo)
move(maze, S, S1, C)   :- maze_move(S, S1, C).
move(puzzle, S, S1, C) :- puzzle_move(S, S1, C).

% heuristic(+Dominio, +Stato, -ValoreH)
heuristic(maze, S, H)   :- maze_heuristic(S, H).
heuristic(puzzle, S, H) :- puzzle_heuristic(S, H).

% goal(+Dominio, +Stato)
goal(maze, S)   :- maze_goal(S).
goal(puzzle, S) :- puzzle_goal_check(S).

% ============================================================
%  PREDICATI DI TEST E CONFRONTO PRESTAZIONI
% ============================================================
%
%  Ogni predicato run_* esegue un algoritmo su un dominio,
%  misura il tempo (walltime in ms), conta nodi espansi o
%  iterazioni, e stampa i risultati.
%
%  Il testo dell''attivita' richiede di confrontare A* e IDA*
%  sui medesimi casi di test.
% ============================================================

%  run_maze_astar/0 - esegue A* sul labirinto statico e stampa i risultati
run_maze_astar :-
    maze_start(Start),
    write('=== A* - Labirinto ==='), nl,
    statistics(walltime, [T0|_]),
    astar(maze, Start, Path, Cost, Expanded),
    statistics(walltime, [T1|_]),
    Time is T1 - T0,
    format('Percorso: ~w~n', [Path]),
    format('Costo: ~w~n', [Cost]),
    format('Nodi espansi: ~w~n', [Expanded]),
    format('Tempo (ms): ~w~n', [Time]).

%  run_maze_idastar/0 - esegue IDA* sul labirinto
run_maze_idastar :-
    maze_start(Start),
    write('=== IDA* - Labirinto ==='), nl,
    statistics(walltime, [T0|_]),
    idastar(maze, Start, Path, Cost, Iters),
    statistics(walltime, [T1|_]),
    Time is T1 - T0,
    format('Percorso: ~w~n', [Path]),
    format('Costo: ~w~n', [Cost]),
    format('Iterazioni IDA*: ~w~n', [Iters]),
    format('Tempo (ms): ~w~n', [Time]).

%  run_puzzle_astar/0 - esegue A* sul puzzle dell''8
run_puzzle_astar :-
    puzzle_start(Start),
    write('=== A* - Puzzle dell''8 ==='), nl,
    statistics(walltime, [T0|_]),
    astar(puzzle, Start, Path, Cost, Expanded),
    statistics(walltime, [T1|_]),
    Time is T1 - T0,
    length(Path, Len), Steps is Len - 1,
    format('Passi: ~w~n', [Steps]),
    format('Costo: ~w~n', [Cost]),
    format('Nodi espansi: ~w~n', [Expanded]),
    format('Tempo (ms): ~w~n', [Time]).

%  run_puzzle_idastar/0 - esegue IDA* sul puzzle dell''8
run_puzzle_idastar :-
    puzzle_start(Start),
    write('=== IDA* - Puzzle dell''8 ==='), nl,
    statistics(walltime, [T0|_]),
    idastar(puzzle, Start, Path, Cost, Iters),
    statistics(walltime, [T1|_]),
    Time is T1 - T0,
    length(Path, Len), Steps is Len - 1,
    format('Passi: ~w~n', [Steps]),
    format('Costo: ~w~n', [Cost]),
    format('Iterazioni IDA*: ~w~n', [Iters]),
    format('Tempo (ms): ~w~n', [Time]).

%  run_all_size(+Rows, +Cols) - genera labirinto RxC casuale e confronta
%  Esempio: ?- run_all_size(10, 10).
run_all_size(R, C) :-
    set_maze_size(R, C),
    generate_until_solvable,
    print_random_maze, nl,
    write('========================================='), nl,
    format('  CONFRONTO A* vs IDA* - Labirinto ~wx~w~n', [R, C]),
    write('========================================='), nl, nl,
    maze_start(Start),
    write('=== A* - Labirinto casuale ==='), nl,
    statistics(walltime, [T0|_]),
    (   astar_dyn(Start, PathA, CostA, ExpA)
    ->  statistics(walltime, [T1|_]),
        TimeA is T1 - T0,
        format('Costo: ~w~n', [CostA]),
        format('Nodi espansi: ~w~n', [ExpA]),
        format('Tempo (ms): ~w~n', [TimeA]),
        format('Percorso: ~w~n', [PathA])
    ;   write('Nessuna soluzione.~n')
    ), nl,
    write('=== IDA* - Labirinto casuale ==='), nl,
    statistics(walltime, [T2|_]),
    (   idastar_dyn(Start, PathI, CostI, ItersI)
    ->  statistics(walltime, [T3|_]),
        TimeI is T3 - T2,
        format('Costo: ~w~n', [CostI]),
        format('Iterazioni: ~w~n', [ItersI]),
        format('Tempo (ms): ~w~n', [TimeI]),
        format('Percorso: ~w~n', [PathI])
    ;   write('Nessuna soluzione.~n')
    ), nl,
    write('========================================='), nl.

%  run_all/0 - confronto completo
run_all :-
    nl, write('========================================='), nl,
    write('  CONFRONTO A* vs IDA* - Tutti i domini'), nl,
    write('========================================='), nl, nl,
    run_maze_astar, nl,
    run_maze_idastar, nl,
    run_puzzle_astar, nl,
    run_puzzle_idastar, nl,
    write('========================================='), nl.

% ============================================================
%  STAMPA GRIGLIA PUZZLE (utilita' visiva)
% ============================================================

print_puzzle([A,B,C,D,E,F,G,H,I]) :-
    format('+---+---+---+~n'),
    print_row(A,B,C),
    format('+---+---+---+~n'),
    print_row(D,E,F),
    format('+---+---+---+~n'),
    print_row(G,H,I),
    format('+---+---+---+~n').

print_row(A,B,C) :-
    print_cell(A), print_cell(B), print_cell(C),
    format('|~n').

print_cell(0) :- format('|   ').
print_cell(X) :- X \= 0, format('| ~w ', [X]).

% ============================================================
%  TEST AGGIUNTIVI
% ============================================================
%  Il testo specifica che le uscite possono essere "non necessariamente
%  raggiungibili". Questi test verificano i casi limite.
% ============================================================

% test_unsolvable_maze/0 - Test con labirinto irrisolvibile.
%
% Crea temporaneamente un labirinto 3x3 completamente bloccato da muri
% intorno allo start, in modo che nessuna uscita sia raggiungibile.
% Verifica che A* e IDA* terminino correttamente senza andare in loop.
test_unsolvable_maze :-
    nl, write('=== TEST: Labirinto irrisolvibile ==='), nl,
    write('Labirinto 3x3 con start circondato da muri:'), nl,
    write('  S # E'), nl,
    write('  # # .'), nl,
    write('  . . E'), nl, nl,
    % Salva fatti originali
    findall(w(R,C), wall(R,C), OldWalls),
    findall(e(P), maze_exit(P), OldExits),
    maze_size(OldR, OldC),
    % Ridefinisci labirinto 3x3 irrisolvibile
    retractall(wall(_, _)),
    retractall(maze_exit(_)),
    retractall(maze_size_dyn(_, _)),
    assertz(maze_size_dyn(3, 3)),
    assertz(wall(1, 2)), assertz(wall(2, 1)),
    assertz(wall(2, 2)),
    assertz(maze_exit(pos(1, 3))),
    assertz(maze_exit(pos(3, 3))),
    % Testa A*
    write('A*:  '),
    (   astar(maze, pos(1,1), _, _, _)
    ->  write('ERRORE - soluzione trovata dove non dovrebbe esistere')
    ;   write('Nessuna soluzione (corretto)')
    ), nl,
    % Testa IDA*
    write('IDA*: '),
    (   idastar(maze, pos(1,1), _, _, _)
    ->  write('ERRORE - soluzione trovata dove non dovrebbe esistere')
    ;   write('Nessuna soluzione (corretto)')
    ), nl,
    % Ripristina fatti originali
    retractall(wall(_, _)),
    retractall(maze_exit(_)),
    retractall(maze_size_dyn(_, _)),
    assertz(maze_size_dyn(OldR, OldC)),
    forall(member(w(R,C), OldWalls), assertz(wall(R,C))),
    forall(member(e(P), OldExits), assertz(maze_exit(P))),
    nl.

% test_already_at_goal/0 - Test con stato iniziale = goal.
%
% Verifica che entrambi gli algoritmi restituiscano costo 0
% quando si parte gia' dalla soluzione.
test_already_at_goal :-
    nl, write('=== TEST: Start = Goal ==='), nl,
    % Labirinto: parti da un''uscita
    write('Labirinto (start = uscita): '),
    (   astar(maze, pos(5,5), _, Cost1, _)
    ->  format('A* costo = ~w (atteso: 0)~n', [Cost1])
    ;   write('A*: fallimento inatteso'), nl
    ),
    write('                           '),
    (   idastar(maze, pos(5,5), _, Cost2, _)
    ->  format('IDA* costo = ~w (atteso: 0)~n', [Cost2])
    ;   write('IDA*: fallimento inatteso'), nl
    ),
    % Puzzle: parti dal goal
    write('Puzzle (start = goal):     '),
    (   astar(puzzle, [1,2,3,4,5,6,7,8,0], _, Cost3, _)
    ->  format('A* costo = ~w (atteso: 0)~n', [Cost3])
    ;   write('A*: fallimento inatteso'), nl
    ),
    write('                           '),
    (   idastar(puzzle, [1,2,3,4,5,6,7,8,0], _, Cost4, _)
    ->  format('IDA* costo = ~w (atteso: 0)~n', [Cost4])
    ;   write('IDA*: fallimento inatteso'), nl
    ),
    nl.

% ============================================================
%  ENTRY POINT RAPIDO
% ============================================================
%  Dalla SWI-Prolog REPL:
%    ?- run_all.                         % confronto completo (stati fissi)
%    ?- run_puzzle_random.               % puzzle casuale risolvibile
%    ?- run_all_random.                  % labirinto casuale
%    ?- run_all_size(10, 10).            % labirinto casuale 10x10
%    ?- run_maze_astar.                  % singolo test
%    ?- run_puzzle_idastar.              % singolo test
%    ?- test_unsolvable_maze.            % test irrisolvibile
%    ?- test_already_at_goal.            % test start = goal
%    ?- generate_random_puzzle(S), print_puzzle(S).  % solo genera e stampa
%    ?- print_puzzle([7,3,1,5,0,6,8,2,4]).           % visualizza griglia
% ============================================================