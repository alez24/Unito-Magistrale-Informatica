% ============================================================
% TORNEO POKEMON - Sistema Svizzero
% Answer Set Programming con Clingo
%
% Uso:
%   python -m clingo torneo.lp turno1.lp 1 --opt-mode=optN
%   python -m clingo torneo.lp turno2.lp 1 --opt-mode=optN
%
%   1 = prima soluzione ottimale trovata
%   0 al posto di 1 = tutte le soluzioni ottimali
%
% Input atteso nel file istanza:
%   player(nome).          -> giocatore registrato
%   score(nome, punti).    -> classifica attuale (0 se nuovo)
%   played(p1, p2).        -> incontro gia' avvenuto (qualsiasi ordine)
%   had_bye(nome).         -> giocatore che ha gia' avuto il BYE
%
% Output:
%   match(P1, P2)  -> incontro tra P1 e P2
%   bye(P)         -> P ottiene il BYE (vittoria automatica)
% ============================================================


% ============================================================
% NORMALIZZAZIONE E ORDINAMENTO
% ============================================================

% Incontro gia' avvenuto: simmetrico (qualsiasi ordine)
played_already(P1, P2) :- played(P1, P2).
played_already(P1, P2) :- played(P2, P1).

% Indice canonico: pid(P, I) dove I e' il numero di giocatori
% lessicograficamente minori di P. Garantisce un ordine totale
% e permette di generare ogni coppia in una sola direzione canonica.
pid(P, I) :- player(P),
             I = #count{ Q : player(Q), Q != P, Q < P }.


% ============================================================
% GENERAZIONE
% ============================================================

% Genera match solo in forma canonica pid(P1) < pid(P2):
% ogni coppia appare una sola volta, evitando match(A,B) e match(B,A)
{ match(P1, P2) } :-
    player(P1), player(P2),
    pid(P1, I1), pid(P2, I2), I1 < I2,
    not played_already(P1, P2).

% BYE: solo per chi non lo ha mai ricevuto
{ bye(P) } :- player(P), not had_bye(P).


% ============================================================
% VINCOLI HARD
% ============================================================

% Helper: un giocatore e' impegnato se compare in qualsiasi posizione
in_match(P) :- match(P, _).
in_match(P) :- match(_, P).

% Ogni giocatore: esattamente un match OPPURE il BYE
:- player(P), not in_match(P), not bye(P).
:- player(P), in_match(P), bye(P).

% Ogni giocatore al massimo in un match (tre casi di conflitto)
:- match(P, Q1), match(P, Q2), Q1 != Q2.   % P primo arg in due match
:- match(P1, Q), match(P2, Q), P1 != P2.   % Q secondo arg in due match
:- match(P, _),  match(_, P).              % P compare in entrambi i ruoli

% Un solo BYE per turno
:- 2 <= #count{ P : bye(P) }.

% Parita': BYE esattamente quando il numero di giocatori e' dispari
player_count(N) :- N = #count{ P : player(P) }.
:- player_count(N), 0 == N \ 2, bye(_).        % pari  -> nessun BYE
:- player_count(N), 1 == N \ 2, not bye(_).    % dispari -> un BYE obbligatorio


% ============================================================
% OTTIMIZZAZIONE
% ============================================================

% Differenza assoluta di punteggio per ogni match
score_diff(P1, P2, D) :-
    match(P1, P2), score(P1, S1), score(P2, S2),
    S1 >= S2, D = S1 - S2.

score_diff(P1, P2, D) :-
    match(P1, P2), score(P1, S1), score(P2, S2),
    S2 > S1, D = S2 - S1.

% Minimizza la somma totale delle differenze: favorisce gli abbinamenti
% tra giocatori con lo stesso punteggio (spareggio)
#minimize { D, P1, P2 : score_diff(P1, P2, D) }.


% ============================================================
% OUTPUT
% ============================================================

#show match/2.
#show bye/1.
