# ATTIVITÀ 1 — TO-DO COMPLETO: IDA* e A* in Prolog

---

## FASE 0 — Prerequisiti teorici da studiare prima di scrivere codice

- Capire cos'è uno spazio degli stati: stato iniziale, operatori, stato goal
- Ripassare la ricerca informata: differenza tra BFS, DFS, e ricerca euristica
- Studiare A*: come funziona f = g + h, perché è ottimale con euristica ammissibile, cosa sono la frontiera e la lista chiusa
- Studiare IDA*: cos'è il threshold, come cresce ad ogni iterazione, perché usa meno memoria di A*
- Capire cosa significa euristica ammissibile (non sovrastima mai il costo reale) e consistente (h(n) <= c(n,n') + h(n'))
- Capire la distanza Manhattan e perché è ammissibile per entrambi i domini

---

## FASE 1 — Capire i due domini a fondo

### Labirinto
- Disegnare a mano la griglia 5×5 con i muri e le due uscite
- Capire cosa rappresenta uno stato: la posizione corrente pos(Riga, Colonna)
- Capire quali mosse sono possibili da ogni cella (su, giù, sinistra, destra)
- Capire quando una mossa è invalida: fuori dai bordi oppure cella è un muro
- Capire cos'è il goal: raggiungere una qualsiasi delle uscite
- Calcolare a mano la distanza Manhattan da pos(1,1) verso ciascuna uscita
- Verificare che sia ammissibile: il percorso reale non può essere più corto della Manhattan

### Puzzle dell'8
- Disegnare la configurazione iniziale e quella goal dell'immagine
- Capire come rappresentare lo stato come lista: [7,3,1,5,0,6,8,2,4]
- Capire come funziona lo zero: si "sposta" lo zero scambiandolo con un vicino
- Mappare gli indici 0-8 sulla griglia 3×3 (indice // 3 = riga, indice mod 3 = colonna)
- Capire quali scambi sono invalidi: lo zero non può uscire dalla griglia né spostarsi diagonalmente
- Calcolare a mano l'euristica Manhattan per lo stato iniziale: somma delle distanze di ogni tessera dalla sua posizione goal
- Verificare che sia ammissibile

---

## FASE 2 — Imparare Prolog abbastanza da procedere

- Capire la sintassi base: fatti, regole, query
- Capire la unificazione e il backtracking
- Capire come funzionano le liste in Prolog: testa/coda, member, append, nth0, reverse, length
- Capire findall/3: raccoglie tutte le soluzioni di un goal in una lista
- Capire assertz/retractall: aggiungere e rimuovere fatti dinamicamente
- Capire il cut (!) e quando usarlo
- Capire is/2 per i calcoli aritmetici
- Capire \/+/1 per la negazione per fallimento
- Esercitarsi con predicati ricorsivi semplici su liste prima di passare alla ricerca

---

## FASE 3 — Progettare la struttura del codice

- Decidere come rappresentare uno stato per ogni dominio
- Decidere come rappresentare un nodo nella frontiera di A*: serve f, g, stato corrente, percorso fatto finora
- Progettare un predicato generico move(Dominio, StatoCorrente, StatoSuccessore, Costo)
- Progettare un predicato generico heuristic(Dominio, Stato, Valore)
- Progettare un predicato generico goal(Dominio, Stato)
- Questa interfaccia permette di scrivere A* e IDA* una volta sola e usarli su entrambi i domini

---

## FASE 4 — Implementare le mosse

### Labirinto
- Scrivere `maze_move/3` che genera i quattro vicini di una cella
- Aggiungere il controllo che la nuova cella sia dentro la griglia
- Aggiungere il controllo che la nuova cella non sia un muro
- Testare a mano: da pos(1,1) quali mosse sono possibili? Solo giù e destra

### Puzzle
- Scrivere `blank_pos/2` che trova l'indice dello zero nella lista
- Scrivere `puzzle_move/3` che calcola il nuovo indice dopo lo scambio
- Gestire i quattro casi: su (indice-3), giù (indice+3), sinistra (indice-1), destra (indice+1)
- Aggiungere i controlli bordo per sinistra e destra (mod 3)
- Scrivere `swap_elements/4` che produce la nuova lista con i due elementi scambiati
- Testare: da [7,3,1,5,0,6,8,2,4] quali stati successori esistono?

---

## FASE 5 — Implementare le euristiche

### Labirinto
- Scrivere `maze_heuristic/2` che calcola la Manhattan verso tutte le uscite con findall
- Prendere il minimo della lista risultante con min_list
- Testare a mano su qualche cella

### Puzzle
- Scrivere `puzzle_heuristic/2` che per ogni tessera (escluso lo zero) calcola la Manhattan tra posizione attuale e posizione nel goal
- Sommare tutte le distanze con sumlist
- Testare a mano: lo stato iniziale [7,3,1,5,0,6,8,2,4] deve dare un valore specifico calcolabile a mano

---

## FASE 6 — Implementare A*

- Struttura della frontiera: lista di nodi ordinata per f crescente
- Scrivere `insert_sorted/3` che inserisce un nodo nella posizione giusta
- Scrivere `insert_all/3` che inserisce una lista di nodi nella frontiera
- Scrivere `astar_loop/7`: estrae il nodo con f minimo, controlla se è goal, altrimenti espande
- Gestire la lista chiusa: non reinserire stati già visitati
- Testare prima sul labirinto (spazio piccolo, facile da seguire a mano)
- Poi testare sul puzzle

---

## FASE 7 — Implementare IDA*

- Scrivere `idastar/5` che inizializza il threshold con h(start)
- Scrivere `idastar_loop/7` che ad ogni iterazione lancia la DFS e aggiorna il threshold
- Scrivere `idastar_search/8`: la DFS ricorsiva con cutoff — se f > threshold ritorna il valore f come next bound
- Scrivere `search_successors/9` che itera sui successori raccogliendo il minimo next bound tra tutti i fallimenti
- Gestire la terminazione: se next bound è infinito non esiste soluzione
- Usare il percorso come lista chiusa per evitare cicli (niente lista chiusa globale)
- Testare prima sul labirinto poi sul puzzle

---

## FASE 8 — Verificare la correttezza

- Controllare che A* e IDA* trovino lo stesso costo ottimo sugli stessi input
- Verificare il percorso del labirinto disegnandolo sulla griglia a mano
- Verificare il percorso del puzzle applicando le mosse una per una sulla configurazione iniziale e controllando di arrivare al goal
- Provare stati goal già raggiunti: il costo deve essere 0
- Provare labirinti irrisolvibili: il programma deve terminare senza soluzione e non andare in loop

---

## FASE 9 — Confrontare le prestazioni

- Usare `statistics(walltime, ...)` per misurare il tempo
- Contare i nodi espansi in A* e le iterazioni in IDA*
- Eseguire entrambi gli algoritmi sugli stessi casi di test
- Testare almeno: labirinto piccolo, labirinto grande, puzzle dell'8 con la configurazione dell'immagine
- Raccogliere i dati in una tabella: dominio, algoritmo, costo, nodi/iterazioni, tempo
- Commentare i risultati: quando vince A* (spazio denso, percorso lungo), quando vince IDA* (spazio ampio, euristica precisa, poca memoria)

---

## FASE 10 — Scrivere la relazione

- Descrivere brevemente i due domini e come sono stati modellati
- Spiegare le euristiche scelte e perché sono ammissibili
- Presentare i risultati con la tabella di confronto
- Commentare le differenze osservate e collegarle alle proprietà teoriche degli algoritmi
- Non serve essere lunghi: è una valutazione breve, bastano chiarezza e precisione
