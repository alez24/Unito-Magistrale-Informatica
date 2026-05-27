;;; ============================================================
;;; WUMPUS WORLD AGENT - Greedy (senza Certainty Factors)
;;; Agente semplificato per confronto con agent.clp
;;;
;;; Strategia: esplora il primo vicino non pericoloso,
;;; evita celle dove ha rilevato brezza o odore.
;;; Tutte le regole di azione leggono posizione/energia dalla
;;; percezione corrente (non da agent-state) per evitare problemi
;;; di ordine di esecuzione con valori non ancora aggiornati.
;;; ============================================================

(defmodule MAIN (export ?ALL))

(deftemplate MAIN::cell
    (slot x         (type INTEGER))
    (slot y         (type INTEGER))
    (slot visited   (type SYMBOL) (default no))
    (slot dangerous (type SYMBOL) (default no))
)

(deftemplate MAIN::agent-state
    (slot x      (type INTEGER) (default 1))
    (slot y      (type INTEGER) (default 1))
    (slot energy (type INTEGER) (default 9999))
)

(deftemplate MAIN::percept
    (slot x       (type INTEGER))
    (slot y       (type INTEGER))
    (slot steps   (type INTEGER))
    (slot breeze  (type SYMBOL))
    (slot stench  (type SYMBOL))
    (slot glitter (type SYMBOL))
    (slot energy  (type INTEGER))
)

(deftemplate MAIN::action
    (slot move (type SYMBOL))
)

(deftemplate MAIN::pending-action
    (slot move     (type SYMBOL))
    (slot priority (type INTEGER) (default 0))
)

(deftemplate MAIN::grid-size
    (slot n (type INTEGER) (default 4))
)

;;; --- Inizializzazione ---
(defrule MAIN::init
    (not (agent-state))
=>
    (assert (agent-state))
    (assert (cell (x 1) (y 1) (visited yes) (dangerous no)))
)

;;; --- Aggiorna stato agente solo se cambia (evita loop da modify) ---
(defrule MAIN::update-state
    (declare (salience 100))
    (percept (x ?x) (y ?y) (energy ?e))
    ?a <- (agent-state (x ?ax) (y ?ay) (energy ?ae))
    (test (or (neq ?ax ?x) (neq ?ay ?y) (neq ?ae ?e)))
=>
    (modify ?a (x ?x) (y ?y) (energy ?e))
)

;;; Segna cella corrente come visitata solo se non lo era gia'
(defrule MAIN::mark-current-visited
    (declare (salience 95))
    (percept (x ?x) (y ?y))
    ?c <- (cell (x ?x) (y ?y) (visited no))
=>
    (modify ?c (visited yes) (dangerous no))
)

(defrule MAIN::create-current-cell
    (declare (salience 95))
    (percept (x ?x) (y ?y))
    (not (cell (x ?x) (y ?y)))
=>
    (assert (cell (x ?x) (y ?y) (visited yes) (dangerous no)))
)

;;; --- Crea celle vicine nei limiti della griglia ---
(defrule MAIN::ensure-north
    (declare (salience 90))
    (percept (x ?x) (y ?y))
    (grid-size (n ?n))
    (test (<= (+ ?y 1) ?n))
    (not (cell (x ?x) (y ?ny&:(= ?ny (+ ?y 1)))))
=>
    (assert (cell (x ?x) (y (+ ?y 1)) (visited no) (dangerous no)))
)

(defrule MAIN::ensure-south
    (declare (salience 90))
    (percept (x ?x) (y ?y))
    (test (> (- ?y 1) 0))
    (not (cell (x ?x) (y ?ny&:(= ?ny (- ?y 1)))))
=>
    (assert (cell (x ?x) (y (- ?y 1)) (visited no) (dangerous no)))
)

(defrule MAIN::ensure-east
    (declare (salience 90))
    (percept (x ?x) (y ?y))
    (grid-size (n ?n))
    (test (<= (+ ?x 1) ?n))
    (not (cell (x ?nx&:(= ?nx (+ ?x 1))) (y ?y)))
=>
    (assert (cell (x (+ ?x 1)) (y ?y) (visited no) (dangerous no)))
)

(defrule MAIN::ensure-west
    (declare (salience 90))
    (percept (x ?x) (y ?y))
    (test (> (- ?x 1) 0))
    (not (cell (x ?nx&:(= ?nx (- ?x 1))) (y ?y)))
=>
    (assert (cell (x (- ?x 1)) (y ?y) (visited no) (dangerous no)))
)

;;; --- Marca vicini come pericolosi se brezza o odore ---
(defrule MAIN::danger-north
    (declare (salience 85))
    (percept (x ?x) (y ?y) (breeze ?b) (stench ?s))
    (test (or (eq ?b yes) (eq ?s yes)))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (dangerous no))
    (test (= ?cx ?x))
    (test (= ?cy (+ ?y 1)))
=>
    (modify ?c (dangerous yes))
)

(defrule MAIN::danger-south
    (declare (salience 85))
    (percept (x ?x) (y ?y) (breeze ?b) (stench ?s))
    (test (or (eq ?b yes) (eq ?s yes)))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (dangerous no))
    (test (= ?cx ?x))
    (test (= ?cy (- ?y 1)))
=>
    (modify ?c (dangerous yes))
)

(defrule MAIN::danger-east
    (declare (salience 85))
    (percept (x ?x) (y ?y) (breeze ?b) (stench ?s))
    (test (or (eq ?b yes) (eq ?s yes)))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (dangerous no))
    (test (= ?cx (+ ?x 1)))
    (test (= ?cy ?y))
=>
    (modify ?c (dangerous yes))
)

(defrule MAIN::danger-west
    (declare (salience 85))
    (percept (x ?x) (y ?y) (breeze ?b) (stench ?s))
    (test (or (eq ?b yes) (eq ?s yes)))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (dangerous no))
    (test (= ?cx (- ?x 1)))
    (test (= ?cy ?y))
=>
    (modify ?c (dangerous yes))
)

;;; --- Selezione azione (usa percept per posizione/energia) ---

;;; Grab se c'e' oro
(defrule MAIN::grab
    (declare (salience 60))
    (percept (glitter yes))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 60))))
=>
    (assert (pending-action (move grab) (priority 60)))
)

;;; Quit se energia bassa (legge da percept, non da agent-state)
(defrule MAIN::quit-low-energy
    (declare (salience 55))
    (percept (energy ?e))
    (test (<= ?e 20))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 55))))
=>
    (assert (pending-action (move quit) (priority 55)))
)

;;; Muovi verso cella sicura non visitata (legge posizione da percept)
(defrule MAIN::move-north
    (declare (salience 50))
    (percept (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (dangerous no))
    (test (= ?cx ?ax))
    (test (= ?cy (+ ?ay 1)))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 50))))
=>
    (assert (pending-action (move up) (priority 50)))
)

(defrule MAIN::move-east
    (declare (salience 50))
    (percept (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (dangerous no))
    (test (= ?cx (+ ?ax 1)))
    (test (= ?cy ?ay))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 50))))
=>
    (assert (pending-action (move right) (priority 50)))
)

(defrule MAIN::move-south
    (declare (salience 50))
    (percept (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (dangerous no))
    (test (= ?cx ?ax))
    (test (= ?cy (- ?ay 1)))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 50))))
=>
    (assert (pending-action (move down) (priority 50)))
)

(defrule MAIN::move-west
    (declare (salience 50))
    (percept (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (dangerous no))
    (test (= ?cx (- ?ax 1)))
    (test (= ?cy ?ay))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 50))))
=>
    (assert (pending-action (move left) (priority 50)))
)

;;; Fallback: esci
(defrule MAIN::fallback
    (declare (salience 1))
    (percept)
    (not (action))
    (not (pending-action))
=>
    (assert (pending-action (move quit) (priority 0)))
)

;;; Rimuovi azioni con priorita' inferiore
(defrule MAIN::cleanup-lower
    (declare (salience 0))
    ?pa <- (pending-action (priority ?p1))
    (pending-action (priority ?p2))
    (test (> ?p2 ?p1))
=>
    (retract ?pa)
)

;;; Emetti azione con priorita' massima (una sola volta)
(defrule MAIN::emit
    (declare (salience -1))
    (not (action))
    ?pa <- (pending-action (move ?m) (priority ?p))
    (not (pending-action (priority ?p2&:(> ?p2 ?p))))
=>
    (assert (action (move ?m)))
    (retract ?pa)
)

;;; Pulizia percept a fine ciclo
(defrule MAIN::cleanup-percept
    (declare (salience -100))
    ?p <- (percept)
    (action)
=>
    (retract ?p)
)
