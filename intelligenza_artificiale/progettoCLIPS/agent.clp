;;; ============================================================
;;; WUMPUS WORLD AGENT - CLIPS con Certainty Factors
;;; Moduli: MAIN, PERCEPT, INFER, DECIDE
;;;
;;; Uso: python3 wumpus.py -m map.json -a agent.clp
;;; ============================================================


;;; ============================================================
;;; MODULO MAIN
;;; ============================================================
(defmodule MAIN (export ?ALL))

(deftemplate MAIN::cell
    (slot x          (type INTEGER))
    (slot y          (type INTEGER))
    (slot visited    (type SYMBOL) (default no))
    (slot safe       (type SYMBOL) (default unknown))
    (slot pit-cf     (type FLOAT)  (default 0.0))
    (slot wumpus-cf  (type FLOAT)  (default 0.0))
)

(deftemplate MAIN::agent-state
    (slot x            (type INTEGER) (default 1))
    (slot y            (type INTEGER) (default 1))
    (slot steps        (type INTEGER) (default 0))
    (slot energy       (type INTEGER) (default 0))
    (slot wumpus-alive (type SYMBOL)  (default yes))
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

;;; Impedisce che le regole INFER sparino piu' volte per la stessa cella
;;; nel medesimo ciclo (CLIPS reasserta il fatto dopo modify, causando loop)
(deftemplate MAIN::cf-done
    (slot x    (type INTEGER))
    (slot y    (type INTEGER))
    (slot kind (type SYMBOL))   ; pit o wumpus
)

;;; Dimensione della griglia (iniettata da Python all'avvio)
(deftemplate MAIN::grid-size
    (slot n (type INTEGER) (default 4))
)

;;; --- Inizializzazione ---
(defrule MAIN::init
    (not (agent-state))
=>
    (assert (agent-state (x 1) (y 1)))
    (assert (cell (x 1) (y 1) (visited yes) (safe yes)
                  (pit-cf -1.0) (wumpus-cf -1.0)))
)

;;; Quando arriva un percept e non c'e' ancora un'azione, attiva PERCEPT
(defrule MAIN::handle-percept
    (percept)
    (agent-state)
    (not (action))
=>
    (focus PERCEPT)
)

;;; Pulizia fine ciclo: ritira percept e marker cf-done
(defrule MAIN::cleanup-cf-done
    (declare (salience -90))
    ?f <- (cf-done)
    (action)
=>
    (retract ?f)
)

(defrule MAIN::cleanup-percept
    (declare (salience -100))
    ?p <- (percept)
    (action)
=>
    (retract ?p)
)


;;; ============================================================
;;; MODULO PERCEPT
;;; ============================================================
(defmodule PERCEPT (import MAIN ?ALL) (export ?ALL))

;;; Aggiorna stato agente solo se i valori sono cambiati
;;; (guard necessario: modify ri-asserta il fatto causando loop infinito)
(defrule PERCEPT::update-agent
    (declare (salience 20))
    (percept (x ?x) (y ?y) (steps ?s) (energy ?e))
    ?a <- (agent-state (x ?ax) (y ?ay) (steps ?as) (energy ?ae))
    (test (or (neq ?ax ?x) (neq ?ay ?y) (neq ?as ?s) (neq ?ae ?e)))
=>
    (modify ?a (x ?x) (y ?y) (steps ?s) (energy ?e))
)

;;; Marca cella corrente come sicura solo se non gia' visitata
;;; (evita il loop da re-attivazione dopo modify)
(defrule PERCEPT::update-current-cell
    (declare (salience 10))
    (percept (x ?x) (y ?y))
    ?c <- (cell (x ?x) (y ?y) (visited no))
=>
    (modify ?c (visited yes) (safe yes) (pit-cf -1.0) (wumpus-cf -1.0))
)

(defrule PERCEPT::create-current-cell
    (declare (salience 10))
    (percept (x ?x) (y ?y))
    (not (cell (x ?x) (y ?y)))
=>
    (assert (cell (x ?x) (y ?y) (visited yes) (safe yes)
                  (pit-cf -1.0) (wumpus-cf -1.0)))
)

;;; Crea celle vicine nei limiti della griglia (usa grid-size per il bound)
(defrule PERCEPT::ensure-north
    (declare (salience 5))
    (percept (x ?x) (y ?y))
    (grid-size (n ?n))
    (test (<= (+ ?y 1) ?n))
    (not (cell (x ?x) (y ?ny&:(= ?ny (+ ?y 1)))))
=>
    (assert (cell (x ?x) (y (+ ?y 1))
                  (visited no) (safe unknown) (pit-cf 0.0) (wumpus-cf 0.0)))
)

(defrule PERCEPT::ensure-south
    (declare (salience 5))
    (percept (x ?x) (y ?y))
    (test (> (- ?y 1) 0))
    (not (cell (x ?x) (y ?ny&:(= ?ny (- ?y 1)))))
=>
    (assert (cell (x ?x) (y (- ?y 1))
                  (visited no) (safe unknown) (pit-cf 0.0) (wumpus-cf 0.0)))
)

(defrule PERCEPT::ensure-east
    (declare (salience 5))
    (percept (x ?x) (y ?y))
    (grid-size (n ?n))
    (test (<= (+ ?x 1) ?n))
    (not (cell (x ?nx&:(= ?nx (+ ?x 1))) (y ?y)))
=>
    (assert (cell (x (+ ?x 1)) (y ?y)
                  (visited no) (safe unknown) (pit-cf 0.0) (wumpus-cf 0.0)))
)

(defrule PERCEPT::ensure-west
    (declare (salience 5))
    (percept (x ?x) (y ?y))
    (test (> (- ?x 1) 0))
    (not (cell (x ?nx&:(= ?nx (- ?x 1))) (y ?y)))
=>
    (assert (cell (x (- ?x 1)) (y ?y)
                  (visited no) (safe unknown) (pit-cf 0.0) (wumpus-cf 0.0)))
)

;;; Transizione a INFER (salience bassa: ultima regola)
(defrule PERCEPT::to-infer
    (declare (salience -1))
    (percept)
=>
    (focus INFER)
)


;;; ============================================================
;;; MODULO INFER - aggiorna CF una sola volta per cella per ciclo
;;;
;;; Ogni regola usa (not (cf-done (x ?cx)(y ?cy)(kind X))) come guard
;;; e asserta (cf-done ...) per bloccare la ri-attivazione dopo modify.
;;;
;;; Formule CF:
;;;   evidenza positiva: CF_new = CF + (1 - CF) * 0.5
;;;   evidenza negativa: CF_new = CF + (-1 - CF) * 0.7
;;; ============================================================
(defmodule INFER (import MAIN ?ALL) (export ?ALL))

;;; --- BREZZA: incrementa CF pit dei vicini ---

(defrule INFER::breeze-north
    (declare (salience 10))
    (percept (x ?x) (y ?y) (breeze yes))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (pit-cf ?cf))
    (test (= ?cx ?x))
    (test (= ?cy (+ ?y 1)))
    (not (cf-done (x ?cx) (y ?cy) (kind pit)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind pit)))
    (modify ?c (pit-cf (+ ?cf (* (- 1.0 ?cf) 0.5))))
)

(defrule INFER::breeze-south
    (declare (salience 10))
    (percept (x ?x) (y ?y) (breeze yes))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (pit-cf ?cf))
    (test (= ?cx ?x))
    (test (= ?cy (- ?y 1)))
    (not (cf-done (x ?cx) (y ?cy) (kind pit)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind pit)))
    (modify ?c (pit-cf (+ ?cf (* (- 1.0 ?cf) 0.5))))
)

(defrule INFER::breeze-east
    (declare (salience 10))
    (percept (x ?x) (y ?y) (breeze yes))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (pit-cf ?cf))
    (test (= ?cx (+ ?x 1)))
    (test (= ?cy ?y))
    (not (cf-done (x ?cx) (y ?cy) (kind pit)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind pit)))
    (modify ?c (pit-cf (+ ?cf (* (- 1.0 ?cf) 0.5))))
)

(defrule INFER::breeze-west
    (declare (salience 10))
    (percept (x ?x) (y ?y) (breeze yes))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (pit-cf ?cf))
    (test (= ?cx (- ?x 1)))
    (test (= ?cy ?y))
    (not (cf-done (x ?cx) (y ?cy) (kind pit)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind pit)))
    (modify ?c (pit-cf (+ ?cf (* (- 1.0 ?cf) 0.5))))
)

;;; --- NESSUNA BREZZA: abbassa CF pit dei vicini ---

(defrule INFER::no-breeze-north
    (declare (salience 10))
    (percept (x ?x) (y ?y) (breeze no))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (pit-cf ?cf))
    (test (= ?cx ?x))
    (test (= ?cy (+ ?y 1)))
    (not (cf-done (x ?cx) (y ?cy) (kind pit)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind pit)))
    (modify ?c (pit-cf (+ ?cf (* (- -1.0 ?cf) 0.7))))
)

(defrule INFER::no-breeze-south
    (declare (salience 10))
    (percept (x ?x) (y ?y) (breeze no))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (pit-cf ?cf))
    (test (= ?cx ?x))
    (test (= ?cy (- ?y 1)))
    (not (cf-done (x ?cx) (y ?cy) (kind pit)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind pit)))
    (modify ?c (pit-cf (+ ?cf (* (- -1.0 ?cf) 0.7))))
)

(defrule INFER::no-breeze-east
    (declare (salience 10))
    (percept (x ?x) (y ?y) (breeze no))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (pit-cf ?cf))
    (test (= ?cx (+ ?x 1)))
    (test (= ?cy ?y))
    (not (cf-done (x ?cx) (y ?cy) (kind pit)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind pit)))
    (modify ?c (pit-cf (+ ?cf (* (- -1.0 ?cf) 0.7))))
)

(defrule INFER::no-breeze-west
    (declare (salience 10))
    (percept (x ?x) (y ?y) (breeze no))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (pit-cf ?cf))
    (test (= ?cx (- ?x 1)))
    (test (= ?cy ?y))
    (not (cf-done (x ?cx) (y ?cy) (kind pit)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind pit)))
    (modify ?c (pit-cf (+ ?cf (* (- -1.0 ?cf) 0.7))))
)

;;; --- ODORE: incrementa CF wumpus ---

(defrule INFER::stench-north
    (declare (salience 10))
    (percept (x ?x) (y ?y) (stench yes))
    (agent-state (wumpus-alive yes))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (wumpus-cf ?cf))
    (test (= ?cx ?x))
    (test (= ?cy (+ ?y 1)))
    (not (cf-done (x ?cx) (y ?cy) (kind wumpus)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind wumpus)))
    (modify ?c (wumpus-cf (+ ?cf (* (- 1.0 ?cf) 0.5))))
)

(defrule INFER::stench-south
    (declare (salience 10))
    (percept (x ?x) (y ?y) (stench yes))
    (agent-state (wumpus-alive yes))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (wumpus-cf ?cf))
    (test (= ?cx ?x))
    (test (= ?cy (- ?y 1)))
    (not (cf-done (x ?cx) (y ?cy) (kind wumpus)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind wumpus)))
    (modify ?c (wumpus-cf (+ ?cf (* (- 1.0 ?cf) 0.5))))
)

(defrule INFER::stench-east
    (declare (salience 10))
    (percept (x ?x) (y ?y) (stench yes))
    (agent-state (wumpus-alive yes))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (wumpus-cf ?cf))
    (test (= ?cx (+ ?x 1)))
    (test (= ?cy ?y))
    (not (cf-done (x ?cx) (y ?cy) (kind wumpus)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind wumpus)))
    (modify ?c (wumpus-cf (+ ?cf (* (- 1.0 ?cf) 0.5))))
)

(defrule INFER::stench-west
    (declare (salience 10))
    (percept (x ?x) (y ?y) (stench yes))
    (agent-state (wumpus-alive yes))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (wumpus-cf ?cf))
    (test (= ?cx (- ?x 1)))
    (test (= ?cy ?y))
    (not (cf-done (x ?cx) (y ?cy) (kind wumpus)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind wumpus)))
    (modify ?c (wumpus-cf (+ ?cf (* (- 1.0 ?cf) 0.5))))
)

;;; --- NESSUN ODORE: abbassa CF wumpus ---

(defrule INFER::no-stench-north
    (declare (salience 10))
    (percept (x ?x) (y ?y) (stench no))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (wumpus-cf ?cf))
    (test (= ?cx ?x))
    (test (= ?cy (+ ?y 1)))
    (not (cf-done (x ?cx) (y ?cy) (kind wumpus)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind wumpus)))
    (modify ?c (wumpus-cf (+ ?cf (* (- -1.0 ?cf) 0.7))))
)

(defrule INFER::no-stench-south
    (declare (salience 10))
    (percept (x ?x) (y ?y) (stench no))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (wumpus-cf ?cf))
    (test (= ?cx ?x))
    (test (= ?cy (- ?y 1)))
    (not (cf-done (x ?cx) (y ?cy) (kind wumpus)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind wumpus)))
    (modify ?c (wumpus-cf (+ ?cf (* (- -1.0 ?cf) 0.7))))
)

(defrule INFER::no-stench-east
    (declare (salience 10))
    (percept (x ?x) (y ?y) (stench no))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (wumpus-cf ?cf))
    (test (= ?cx (+ ?x 1)))
    (test (= ?cy ?y))
    (not (cf-done (x ?cx) (y ?cy) (kind wumpus)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind wumpus)))
    (modify ?c (wumpus-cf (+ ?cf (* (- -1.0 ?cf) 0.7))))
)

(defrule INFER::no-stench-west
    (declare (salience 10))
    (percept (x ?x) (y ?y) (stench no))
    ?c <- (cell (x ?cx) (y ?cy) (visited no) (wumpus-cf ?cf))
    (test (= ?cx (- ?x 1)))
    (test (= ?cy ?y))
    (not (cf-done (x ?cx) (y ?cy) (kind wumpus)))
=>
    (assert (cf-done (x ?cx) (y ?cy) (kind wumpus)))
    (modify ?c (wumpus-cf (+ ?cf (* (- -1.0 ?cf) 0.7))))
)

;;; --- Classifica le celle dopo l'aggiornamento CF ---

(defrule INFER::mark-safe
    (declare (salience 5))
    ?c <- (cell (visited no) (safe unknown) (pit-cf ?pcf) (wumpus-cf ?wcf))
    (test (< ?pcf -0.5))
    (test (< ?wcf -0.5))
=>
    (modify ?c (safe yes))
)

(defrule INFER::mark-dangerous-pit
    (declare (salience 5))
    ?c <- (cell (visited no) (safe unknown) (pit-cf ?pcf))
    (test (> ?pcf 0.6))
=>
    (modify ?c (safe no))
)

(defrule INFER::mark-dangerous-wumpus
    (declare (salience 5))
    ?c <- (cell (visited no) (safe unknown) (wumpus-cf ?wcf))
    (test (> ?wcf 0.6))
=>
    (modify ?c (safe no))
)

;;; Transizione a DECIDE
(defrule INFER::to-decide
    (declare (salience -1))
    (percept)
=>
    (focus DECIDE)
)


;;; ============================================================
;;; MODULO DECIDE - selezione azione con priorita'
;;; ============================================================
(defmodule DECIDE (import MAIN ?ALL) (export ?ALL))

;;; Priorita' 100: raccogli oro
(defrule DECIDE::grab-gold
    (declare (salience 100))
    (percept (glitter yes))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 100))))
=>
    (assert (pending-action (move grab) (priority 100)))
)

;;; Priorita' 90: esci se energia troppo bassa
(defrule DECIDE::quit-low-energy
    (declare (salience 90))
    (agent-state (energy ?e))
    (test (<= ?e 30))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 90))))
=>
    (assert (pending-action (move quit) (priority 90)))
)

;;; Priorita' 80: muoviti verso cella sicura non visitata
(defrule DECIDE::move-safe-north
    (declare (salience 80))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe yes))
    (test (= ?cx ?ax))
    (test (= ?cy (+ ?ay 1)))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 80))))
=>
    (assert (pending-action (move up) (priority 80)))
)

(defrule DECIDE::move-safe-east
    (declare (salience 80))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe yes))
    (test (= ?cx (+ ?ax 1)))
    (test (= ?cy ?ay))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 80))))
=>
    (assert (pending-action (move right) (priority 80)))
)

(defrule DECIDE::move-safe-south
    (declare (salience 80))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe yes))
    (test (= ?cx ?ax))
    (test (= ?cy (- ?ay 1)))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 80))))
=>
    (assert (pending-action (move down) (priority 80)))
)

(defrule DECIDE::move-safe-west
    (declare (salience 80))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe yes))
    (test (= ?cx (- ?ax 1)))
    (test (= ?cy ?ay))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 80))))
=>
    (assert (pending-action (move left) (priority 80)))
)

;;; Priorita' 60: pit-guess (CF pit moderata, CF wumpus bassa)
(defrule DECIDE::pit-guess-north
    (declare (salience 60))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe unknown) (pit-cf ?pcf) (wumpus-cf ?wcf))
    (test (= ?cx ?ax))
    (test (= ?cy (+ ?ay 1)))
    (test (> ?pcf 0.3))
    (test (< ?wcf 0.3))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 60))))
=>
    (assert (pending-action (move pit-north) (priority 60)))
)

(defrule DECIDE::pit-guess-east
    (declare (salience 60))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe unknown) (pit-cf ?pcf) (wumpus-cf ?wcf))
    (test (= ?cx (+ ?ax 1)))
    (test (= ?cy ?ay))
    (test (> ?pcf 0.3))
    (test (< ?wcf 0.3))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 60))))
=>
    (assert (pending-action (move pit-east) (priority 60)))
)

(defrule DECIDE::pit-guess-south
    (declare (salience 60))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe unknown) (pit-cf ?pcf) (wumpus-cf ?wcf))
    (test (= ?cx ?ax))
    (test (= ?cy (- ?ay 1)))
    (test (> ?pcf 0.3))
    (test (< ?wcf 0.3))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 60))))
=>
    (assert (pending-action (move pit-south) (priority 60)))
)

(defrule DECIDE::pit-guess-west
    (declare (salience 60))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe unknown) (pit-cf ?pcf) (wumpus-cf ?wcf))
    (test (= ?cx (- ?ax 1)))
    (test (= ?cy ?ay))
    (test (> ?pcf 0.3))
    (test (< ?wcf 0.3))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 60))))
=>
    (assert (pending-action (move pit-west) (priority 60)))
)

;;; Priorita' 10: esplora cella a rischio basso-moderato
(defrule DECIDE::explore-north
    (declare (salience 10))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe unknown) (pit-cf ?pcf) (wumpus-cf ?wcf))
    (test (= ?cx ?ax))
    (test (= ?cy (+ ?ay 1)))
    (test (< ?pcf 0.5))
    (test (< ?wcf 0.5))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 10))))
=>
    (assert (pending-action (move up) (priority 10)))
)

(defrule DECIDE::explore-east
    (declare (salience 10))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe unknown) (pit-cf ?pcf) (wumpus-cf ?wcf))
    (test (= ?cx (+ ?ax 1)))
    (test (= ?cy ?ay))
    (test (< ?pcf 0.5))
    (test (< ?wcf 0.5))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 10))))
=>
    (assert (pending-action (move right) (priority 10)))
)

(defrule DECIDE::explore-south
    (declare (salience 10))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe unknown) (pit-cf ?pcf) (wumpus-cf ?wcf))
    (test (= ?cx ?ax))
    (test (= ?cy (- ?ay 1)))
    (test (< ?pcf 0.5))
    (test (< ?wcf 0.5))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 10))))
=>
    (assert (pending-action (move down) (priority 10)))
)

(defrule DECIDE::explore-west
    (declare (salience 10))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe unknown) (pit-cf ?pcf) (wumpus-cf ?wcf))
    (test (= ?cx (- ?ax 1)))
    (test (= ?cy ?ay))
    (test (< ?pcf 0.5))
    (test (< ?wcf 0.5))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 10))))
=>
    (assert (pending-action (move left) (priority 10)))
)

;;; Priorita' 5: fallback coraggioso (cella unknown o parzialmente rischiosa)
(defrule DECIDE::bold-north
    (declare (salience 5))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe ?s))
    (test (= ?cx ?ax))
    (test (= ?cy (+ ?ay 1)))
    (test (neq ?s no))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 5))))
=>
    (assert (pending-action (move up) (priority 5)))
)

(defrule DECIDE::bold-east
    (declare (salience 5))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe ?s))
    (test (= ?cx (+ ?ax 1)))
    (test (= ?cy ?ay))
    (test (neq ?s no))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 5))))
=>
    (assert (pending-action (move right) (priority 5)))
)

(defrule DECIDE::bold-south
    (declare (salience 5))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe ?s))
    (test (= ?cx ?ax))
    (test (= ?cy (- ?ay 1)))
    (test (neq ?s no))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 5))))
=>
    (assert (pending-action (move down) (priority 5)))
)

(defrule DECIDE::bold-west
    (declare (salience 5))
    (agent-state (x ?ax) (y ?ay))
    (cell (x ?cx) (y ?cy) (visited no) (safe ?s))
    (test (= ?cx (- ?ax 1)))
    (test (= ?cy ?ay))
    (test (neq ?s no))
    (not (action))
    (not (pending-action (priority ?p&:(>= ?p 5))))
=>
    (assert (pending-action (move left) (priority 5)))
)

;;; Fallback finale: esci se completamente bloccato
(defrule DECIDE::fallback-quit
    (declare (salience 1))
    (not (action))
    (not (pending-action))
=>
    (assert (pending-action (move quit) (priority 0)))
)

;;; Rimuovi azioni con priorita' inferiore
(defrule DECIDE::cleanup-lower
    (declare (salience 0))
    ?pa <- (pending-action (priority ?p1))
    (pending-action (priority ?p2))
    (test (> ?p2 ?p1))
=>
    (retract ?pa)
)

;;; Emetti l'azione con priorita' massima (una sola volta)
(defrule DECIDE::emit-action
    (declare (salience -1))
    (not (action))
    ?pa <- (pending-action (move ?m) (priority ?p))
    (not (pending-action (priority ?p2&:(> ?p2 ?p))))
=>
    (assert (action (move ?m)))
    (retract ?pa)
)
