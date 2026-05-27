% ============================================================
% ISTANZA TURNO 1
%
% Partecipanti iniziali: Lorenzo, Emma, Simone, Diego, Giada
% Classifica: tutti a 0 punti
% Incontri precedenti: nessuno
% BYE precedenti: nessuno
%
% Numero giocatori: 5 (dispari) -> un giocatore riceve il BYE
%
% Esegui con: clingo torneo.lp turno1.lp
% ============================================================

% --- Giocatori registrati ---
player(lorenzo).
player(emma).
player(simone).
player(diego).
player(giada).

% --- Classifica attuale (tutti a 0) ---
score(lorenzo, 0).
score(emma,    0).
score(simone,  0).
score(diego,   0).
score(giada,   0).

% --- Incontri gia' avvenuti: nessuno ---
% (nessun fatto played/2)

% --- BYE precedenti: nessuno ---
% (nessun fatto had_bye/1)
