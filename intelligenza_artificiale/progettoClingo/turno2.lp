% ============================================================
% ISTANZA TURNO 2
%
% Dopo il turno 1: Lorenzo e Simone hanno vinto (2 punti ciascuno),
%   Emma e Diego hanno perso (0 punti), Giada ha avuto il BYE (2 punti).
% Nuovi iscritti: Jacopo, Thomas, Desiree (tutti a 0 punti).
%
% Numero giocatori: 8 (pari) -> nessun BYE in questo turno
%
% Incontri avvenuti nel turno 1:
%   Lorenzo vs Emma  (vince Lorenzo)
%   Simone vs Diego  (vince Simone)
%   Giada: BYE       (vittoria automatica)
%
% Esegui con: clingo torneo.lp turno2.lp
% ============================================================

% --- Giocatori registrati (vecchi + nuovi) ---
player(lorenzo).
player(emma).
player(simone).
player(diego).
player(giada).
player(jacopo).
player(thomas).
player(desiree).

% --- Classifica aggiornata dopo il turno 1 ---
score(lorenzo, 2).
score(simone,  2).
score(giada,   2).
score(emma,    0).
score(diego,   0).
score(jacopo,  0).
score(thomas,  0).
score(desiree, 0).

% --- Incontri gia' avvenuti (turno 1) ---
played(emma,   lorenzo).   % Lorenzo ha vinto
played(diego,  simone).    % Simone ha vinto
% Il BYE di Giada non genera un fatto played/2

% --- Giocatori che hanno gia' avuto il BYE ---
had_bye(giada).
