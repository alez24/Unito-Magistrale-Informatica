:- module(search, [a_star/7, ida_star/7]).

%%  a_star(+IsGoal, +Successors, +Heuristic, +Start, -Path, -Cost, -Stats)
%%
%%  IsGoal    : call(IsGoal, State)             -- true if State is a goal
%%  Successors: call(Successors, State, NS, C)  -- NS is successor of State with step-cost C
%%  Heuristic : call(Heuristic, State, H)       -- admissible heuristic value H
%%  Start     : initial state
%%  Path      : list of states from Start to goal (inclusive)
%%  Cost      : total path cost (g-value at goal)
%%  Stats     : stats(Expanded, MaxOpenSize)
%%
:- meta_predicate a_star(1, 3, 2, +, -, -, -).

a_star(IsGoal, Successors, Heuristic, Start, Path, Cost, stats(Expanded, MaxOpen)) :-
    call(Heuristic, Start, H0),
    F0 is 0 + H0,
    Open0 = [f(F0, 0, Start, [Start])],
    a_star_loop(IsGoal, Successors, Heuristic, Open0, [], 0, 1,
                Path, Cost, Expanded, MaxOpen).

a_star_loop(IsGoal, _, _, [f(_, G, State, RevPath)|_], _, Exp, MaxOpen,
            Path, G, Exp, MaxOpen) :-
    call(IsGoal, State),
    reverse(RevPath, Path).

a_star_loop(IsGoal, Successors, Heuristic, [f(_, G, State, RevPath)|Rest],
            Closed, Exp0, MaxOpen0, Path, Cost, Expanded, MaxOpen) :-
    \+ call(IsGoal, State),
    (memberchk(State, Closed) ->
        a_star_loop(IsGoal, Successors, Heuristic, Rest, Closed, Exp0, MaxOpen0,
                    Path, Cost, Expanded, MaxOpen)
    ;
        Exp1 is Exp0 + 1,
        findall(f(F, G1, NS, [NS|RevPath]),
                (call(Successors, State, NS, C),
                 \+ memberchk(NS, Closed),
                 G1 is G + C,
                 call(Heuristic, NS, H),
                 F is G1 + H),
                Children),
        insert_all(Children, Rest, Open1),
        length(Open1, OpenSize),
        MaxOpen1 is max(MaxOpen0, OpenSize),
        a_star_loop(IsGoal, Successors, Heuristic, Open1, [State|Closed],
                    Exp1, MaxOpen1, Path, Cost, Expanded, MaxOpen)
    ).

insert_all([], Open, Open).
insert_all([Node|Nodes], Open, Result) :-
    insert_sorted(Node, Open, Open1),
    insert_all(Nodes, Open1, Result).

insert_sorted(Node, [], [Node]).
insert_sorted(Node, [H|T], [Node,H|T]) :-
    Node = f(F1, _, _, _), H = f(F2, _, _, _),
    F1 =< F2, !.
insert_sorted(Node, [H|T], [H|T1]) :-
    insert_sorted(Node, T, T1).


%%  ida_star(+IsGoal, +Successors, +Heuristic, +Start, -Path, -Cost, -Stats)
%%
%%  Same interface as a_star/7.
%%  Stats: stats(Iterations, TotalExpanded)
%%
:- meta_predicate ida_star(1, 3, 2, +, -, -, -).

ida_star(IsGoal, Successors, Heuristic, Start, Path, Cost, stats(Iters, TotalExp)) :-
    call(Heuristic, Start, H0),
    ida_star_iter(IsGoal, Successors, Heuristic, Start, H0, 0, 0,
                  Path, Cost, Iters, TotalExp).

ida_star_iter(IsGoal, Successors, Heuristic, Start, Threshold, Iters0, Exp0,
              Path, Cost, Iters, TotalExp) :-
    Iters1 is Iters0 + 1,
    ida_dfs(IsGoal, Successors, Heuristic, Start, [Start], 0, Threshold, Exp0,
            Result, Exp1),
    (Result = found(RevPath, Cost) ->
        reverse(RevPath, Path),
        Iters = Iters1,
        TotalExp = Exp1
    ;
        Result = next(NextThreshold),
        ida_star_iter(IsGoal, Successors, Heuristic, Start, NextThreshold, Iters1, Exp1,
                      Path, Cost, Iters, TotalExp)
    ).

% ida_dfs(+IsGoal, +Successors, +Heuristic, +State, +RevPath, +G, +Threshold,
%         +Exp0, -Result, -Exp)
% Result = found(RevPath, Cost) | next(MinExceeded)
ida_dfs(IsGoal, _, _, State, RevPath, G, _, Exp, found(RevPath, G), Exp) :-
    call(IsGoal, State), !.

ida_dfs(_, _, Heuristic, State, _, G, Threshold, Exp, next(F), Exp) :-
    call(Heuristic, State, H),
    F is G + H,
    F > Threshold, !.

ida_dfs(IsGoal, Successors, Heuristic, State, RevPath, G, Threshold, Exp0, Result, Exp) :-
    Exp1 is Exp0 + 1,
    findall(s(NS, C),
            (call(Successors, State, NS, C), \+ memberchk(NS, RevPath)),
            Children),
    dfs_children(IsGoal, Successors, Heuristic, Children, RevPath, G, Threshold,
                 Exp1, Result, Exp).

dfs_children(_, _, _, [], _, _, _, Exp, next(inf), Exp).

dfs_children(IsGoal, Successors, Heuristic, [s(NS, C)|Rest], RevPath, G, Threshold,
             Exp0, Result, Exp) :-
    G1 is G + C,
    ida_dfs(IsGoal, Successors, Heuristic, NS, [NS|RevPath], G1, Threshold, Exp0,
            ChildResult, Exp1),
    (ChildResult = found(_, _) ->
        Result = ChildResult, Exp = Exp1
    ;
        ChildResult = next(T1),
        dfs_children(IsGoal, Successors, Heuristic, Rest, RevPath, G, Threshold,
                     Exp1, RestResult, Exp2),
        (RestResult = found(_, _) ->
            Result = RestResult, Exp = Exp2
        ;
            RestResult = next(T2),
            (T1 == inf -> Min = T2 ; T2 == inf -> Min = T1 ; Min is min(T1, T2)),
            Result = next(Min), Exp = Exp2
        )
    ).