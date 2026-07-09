# Modulo 1 — Introduzione all'IA e Agenti Intelligenti

## Cos'è l'IA

Esempi di apertura (DeepSeek/ChatGPT che "allucinano" su un personaggio inesistente, Napoleone VII di Baviera): sistemi fluenti e convincenti ma **non implica comprensione né conoscenza verificata**. L'IA reale diffusa è quasi sempre **specializzata e invisibile** (raccomandazioni, riconoscimento immagini, assistenti, mutui, logistica), non il robot antropomorfo dell'immaginario comune.

**Intelligenza artificiale** = intelligenza **non naturale**, ottenuta con procedimenti tecnici/informatici (non biologici).

**Breve storia**: 1936 Macchina di Turing; 1940 ENIAC; 1950 Turing propone il Test di Turing; 1956 **Dartmouth Summer Research Project** (John McCarthy conia "Artificial Intelligence"; parteciparono Solomonoff, Minsky, McCarthy, Shannon, Newell, Simon ecc.; né Turing né von Neumann). **Automazione ≠ intelligenza**: una calcolatrice esegue istruzioni automaticamente ma non è intelligente — serve **adattarsi**, scegliere di fronte a situazioni non previste, eventualmente **imparare**.

**Test di Turing** (1950, "Computing Machinery and Intelligence", *Imitation Game*): un intervistatore comunica per iscritto con un umano e una macchina nascosti; se non li distingue in modo affidabile, la macchina supera il test. Valuta solo il **comportamento osservabile** (I/O). Critica (esempio Valeria/Rossella sul quiz di geografia): stesso output (risposta corretta) può nascondere comprensione reale oppure un caso fortuito — **stesso output non implica stessa comprensione**, quindi il test è necessario ma probabilmente non sufficiente per l'intelligenza "vera".

**Stanza Cinese** (Searle, 1980, *Minds, brains, and programs*): una persona che non conosce il cinese, seguendo un manuale di regole puramente sintattiche, produce risposte in cinese sensate senza capirle. Tesi di Searle: eseguire un programma (manipolare simboli sintatticamente) non è mai condizione sufficiente per l'intenzionalità/comprensione.

**CAPTCHA**: test di Turing "inverso" — un computer distingue umano da bot (1997, AltaVista).

**Strong AI** (riprodurre realmente il pensiero umano, scienze cognitive) vs **Weak AI** (task-oriented: basta risolvere problemi che richiederebbero intelligenza se svolti da un umano, comportamento *razionale*). Il corso adotta l'approccio Weak AI / "agire razionalmente" (Poole, Nilsson, R&N).

**Le quattro scuole di definizione dell'IA** (R&N, due assi: pensiero/comportamento × umano/razionale):

| | Pensiero | Comportamento |
|---|---|---|
| **come l'uomo** | pensare come umani (Haugeland, Bellman) | agire come umani (Kurzweil, Rich&Knight — Test di Turing) |
| **razionale** | pensare razionalmente (Charniak&McDermott, Winston) | agire razionalmente (Poole, Nilsson — approccio del corso) |

**Quando serve l'IA**: non quando esistono già modelli matematici/algoritmi precisi; utile/necessaria con problemi non deterministici, molteplici soluzioni possibili, preferenze, dati simbolici, conoscenza ampia/incompleta, interazione con ambiente/umani.

**Discipline fondanti**: Filosofia, Matematica, Economia, Neuroscienze, Psicologia, Informatica, Teoria del controllo, Linguistica. Esempi: **Aristotele** (Etica Nicomachea) — si delibera sui *mezzi*, non sui fini, procedendo a ritroso dai mezzi a una causa prima: primo esempio storico di ricerca **backward** (⟶ General Problem Solver di Newell&Simon, ~2300 anni dopo). **Pavlov** — riflesso condizionato (stimolo neutro + stimolo incondizionato ⟶ stimolo condizionato): comportamento modificabile dall'esperienza, base dell'apprendimento automatico.

## Agenti e ambienti

**Agente** = astrazione che percepisce l'ambiente (sensori) e agisce su di esso (attuatori); agente+ambiente = binomio inscindibile. Il simbolo "?" nel diagramma = funzione deliberativa (cosa distingue i vari tipi di agente).

**Sequenza percettiva** = storia completa delle percezioni ricevute fino a un istante. Il modo più generale (oneroso) per il modulo deliberativo è una tabella percepito→azione. Esempio mondo dell'aspirapolvere: due tabelle diverse per lo stesso ambiente = due agenti diversi con comportamenti diversi → serve un criterio oggettivo per confrontarli (misura di prestazione).

**Razionalità**: agente razionale = "fa la cosa giusta", massimizza la **misura di prestazione (performance measure)** attesa. Dipende da 4 fattori: azioni disponibili, misura di prestazione, conoscenza dell'ambiente, sequenza percettiva. **Razionalità ≠ onniscienza/chiaroveggenza**: ottimizza il risultato *atteso* (dato ciò che si sa), non quello *reale* (esempio torta di compleanno: comprare la torta migliore nota resta razionale anche se la nonna ne porta una identica — informazione non posseduta). Un agente razionale migliora **imparando dall'esperienza**: ripetere lo stesso errore ignorando ciò che si è imparato non è più razionale. La **percezione non è un atto passivo**: un agente razionale può scegliere di percepire di più prima di agire (es. guardare prima di attraversare).

**Task environment e PEAS**: Performance measure, Environment, Actuators, Sensors — primo passo sistematico nella progettazione di un agente.

**Proprietà dell'ambiente** (7 assi indipendenti, determinano quali tecniche servono):

| Asse | Valore "facile" | Valore "difficile" |
|---|---|---|
| Osservabilità | completa | parziale |
| Determinismo | deterministico | stocastico (strategico se dipende solo da altri agenti) |
| Episodicità | episodico (percezione→azione indipendenti) | sequenziale |
| Dinamicità | statico (non cambia mentre l'agente decide) | dinamico |
| Discretezza | discreto | continuo |
| N. agenti | singolo | multiagente |

Parziale osservabilità spesso **appare** come stocasticità (es. batteria con carica continua percepita solo come bassa/media/alta). Criterio per modellare un'entità come agente: il suo comportamento cerca di massimizzare una **propria** misura di prestazione dipendente dal comportamento altrui (interazione strategica); altrimenti è ambiente. Caso più difficile: parzialmente osservabile, stocastico, sequenziale, dinamico, continuo, multiagente (es. guidare un taxi vs. parole crociate, il caso più facile).

Esempi guida: **termostato** (percepisce temperatura, decide, accende/spegne — comportamento predefinito: non fare nulla) e **Roomba** (percepisce ostacoli/batteria — comportamento predefinito: torna a ricaricarsi).

**Agente = architettura + programma**. **Funzione agente** (astrazione ideale: intera sequenza percettiva → azione) vs **programma agente** (implementazione reale: percezione corrente + eventuale stato interno → azione).

**Tipologie di agente** (sofisticazione crescente):

| Tipo | Usa per decidere | Limiti |
|---|---|---|
| **Reattivo semplice** | solo percezione corrente + regole condizione-azione | solo se completamente osservabile; rischio loop infiniti (serve randomizzazione) |
| **Reattivo con modello** | percezione + stato interno + modello di come evolve il mondo | gestisce osservabilità parziale, prevede gli effetti delle azioni |
| **Basato su obiettivi** | percezione + modello + goal esplicito (ragionamento ipotetico/pianificazione) | flessibile (basta cambiare goal), ma non distingue fra soluzioni diverse |
| **Basato sull'utilità** | come sopra + funzione di utilità (bilancia costo/tempo/rischio...) | sceglie la *migliore* fra più soluzioni, ma serve saper definire l'utilità |
| **Che apprende** | tutto sopra + Critico + Modulo di apprendimento + Generatore di problemi (azioni esplorative) | si adatta nel tempo, ma più complesso, serve un buon segnale di feedback |

## Dall'automazione alla dichiaratività

**Paradigma imperativo/a oggetti** (non-AI): sequenza esplicita di passi che dicono **come** ottenere il risultato (risolve un singolo compito specifico). **Paradigma dichiarativo** (AI): separa **cosa** si vuole/si sa (Knowledge Base) da un **programma generale** (motore di inferenza/ricerca) applicabile a descrizioni diverse senza riscriverlo.

**Mondo dei blocchi** (esempio guida): l'agente percepisce lo stato iniziale (di per sé non genera azione), riceve un **goal**, e deve **costruire autonomamente** — tramite ricerca nello spazio degli stati — la sequenza di azioni (Prendi, Impila, Metti) che porta dallo stato iniziale al goal: "il programma dell'agente costruisce un programma".

**Dal toy problem al mondo reale**: identificare un passaggio pedonale da un'immagine reale richiede elaborare pixel grezzi fino a trasformarli in informazione (visione artificiale) — enorme distanza rispetto a dati simbolici già puliti come nel mondo dei blocchi.

---

# Modulo 2 — Ricerca nello spazio degli stati

## Formulazione del problema

Astrazione: **stati discreti**, effetto (di solito) **deterministico** delle azioni, **dominio statico**. Un **obiettivo** = situazione (+ eventuale prestazione) da raggiungere; **insieme degli stati obiettivo** = tutti gli stati che lo soddisfano. Una **soluzione è un percorso** nello spazio degli stati.

**Problema di ricerca** = 4-tupla: (1) stato iniziale, (2) funzione successore (azioni + modello di transizione), (3) test obiettivo, (4) funzione di costo del cammino. Lo **spazio degli stati** è spesso implicito/generativo. Esempi: navigazione stradale, aspirapolvere (4 configurazioni per stanza), **8-puzzle** (181.440 = 9!/2 stati raggiungibili — solo metà delle permutazioni è raggiungibile senza "sollevare" le tessere). **Toy problem** (formulazione precisa, es. 8 regine, torre di Hanoi) vs **real-world problem** (VLSI, itinerari, spesso senza formulazione univoca). Esempio 8 regine: formulazione **incrementale** (stati = configurazioni parziali senza conflitti, una regina per colonna) riduce enormemente lo spazio rispetto a generare tutte le disposizioni su 64 caselle.

**Spazio degli stati** (astratto, definito dal problema) ≠ **albero/grafo di ricerca** (struttura dati costruita dall'algoritmo: nodo = stato + genitore + azione + profondità + costo accumulato). Diventa **grafo** quando lo stesso stato è raggiungibile da più percorsi. Nodi: **frontiera** (generati non ancora espansi), **espanso/chiuso**, non ancora generato.

**Criteri di valutazione**: completezza (trova sempre soluzione se esiste), ottimalità (trova quella a costo minimo), complessità temporale/spaziale (in nodi generati/mantenuti, notazione O-grande). Parametri: **b** (branching factor), **d** (profondità soluzione più superficiale), **m** (profondità massima, anche infinita). Approcci **blind/non informati** (solo struttura del problema) vs **informati** (usano euristiche).

## Ricerca non informata

| Strategia | Frontiera | Completa | Ottima | Tempo | Spazio |
|---|---|---|---|---|---|
| Ampiezza (BFS) | coda FIFO | Sì (b finito) | Sì (costo non decrescente con profondità, es. costi uniformi) | O(b^(d+1)) | O(b^(d+1)) |
| Costo uniforme | coda priorità su g(n) | Sì (costi>0) | Sì (costi>0) | O(b^(1+⌊C*/ε⌋)) | idem |
| Profondità (DFS) | coda LIFO/stack | No (solo se cammini finiti) | No | O(b^m) | O(bm) [O(m) con backtracking a un successore alla volta] |
| Profondità limitata (l) | stack + limite l | No se l<d | No | O(b^l) | O(bl) |
| Iterative deepening (IDDFS) | stack ricostruito ogni iterazione | Sì (b finito) | Sì (come BFS) | O(b^d) | O(bd) |
| Bidirezionale | doppia frontiera | Sì (b finito, BFS entrambe le direzioni) | Sì (costi uniformi, BFS) | O(b^(d/2)) | O(b^(d/2)) |

Note: la BFS ha complessità spaziale proibitiva in pratica (es. b=10,d=12 → ~10 petabyte). La ricerca a costo uniforme non si ferma al primo goal trovato, verifica che non ci siano cammini aperti più economici; coincide con BFS se costi uniformi. **IDDFS genera meno nodi della BFS** (evita quasi tutto il costoso livello d+1) — è generalmente la scelta migliore quando d non è nota: unisce completezza/ottimalità di BFS a spazio O(bd) come DFS. **Ricerca bidirezionale**: richiede saper calcolare i predecessori (non sempre facile); se il goal non è unico si introduce uno stato "di comodo" raggiungibile da tutti i goal in un passo. Marcare i nodi già visitati (albero→grafo) evita di riesplorare gli stessi stati.

Esempi classici di esercizio: capra/lupo/cavolo, missionari e cannibali, torre di Hanoi.

## Ricerca informata (euristica)

`f(n)` = funzione di valutazione per ordinare la frontiera (famiglia **best-first search**); `h(n)` = euristica, stima il costo minimo residuo a un goal.

- **Greedy**: f(n)=h(n). Guarda solo avanti, ignora il costo già speso. Può essere ingannata (l'euristica non riflette il costo reale) e cadere in vicoli ciechi/loop (eredita i difetti della DFS): **non completa né ottima** in generale.
- **A\***: f(n)=g(n)+h(n) — g(n) guarda indietro (costo minimo osservato per arrivare a n), h(n) guarda avanti (stima al goal). **Euristica ammissibile**: h(n)≤h*(n) (mai sovrastima). **Teorema**: se h ammissibile e costi >ε>0, A* è completo e ottimo (dimostrazione su albero: un nodo n sul cammino ottimo ha sempre f(n)≤C*<f(G2) per qualunque goal subottimo G2, quindi A* lo preferisce sempre). Su **grafi** (molteplicità di cammini) serve la proprietà più forte di **consistenza/monotonicità**: h(n)≤c(n,a,n')+h(n') (disuguaglianza triangolare) ⟹ f(n) non decrescente lungo ogni cammino ⟹ il primo goal *espanso* (non solo generato) è già ottimo. Ogni euristica monotona è ammissibile, non vale il viceversa. h(n)=0 è banalmente ammissibile ma non informativa (A* degenera in costo uniforme/BFS). A* è **ottimamente efficiente**: nessun altro algoritmo ottimo con la stessa euristica espande meno nodi — ma mantiene **tutti** i nodi in memoria (come BFS), spesso impraticabile per limiti di memoria.
- **IDA\*** (iterative deepening A*): come A* ma il limite di taglio è su f(n), non sulla profondità.
- **RBFS** (Recursive Best-First Search, Korf 1993): DFS ricorsiva con un **upper bound dinamico** B (miglior alternativa fra i fratelli); abbandona un ramo quando smette di essere il più promettente, "dimenticandolo" (poi eventualmente ri-esplorato, con lavoro ripetuto). Spazio **O(bd)** lineare (enorme vantaggio su A*), ottimo se h ammissibile; non riconosce cammini ripetuti e non sfrutta memoria extra disponibile.

**Caso di studio 8-puzzle**: in media 22 mosse, branching medio 3 (2 in un angolo, 3 sul bordo, 4 al centro). Albero esaustivo ~3^22 nodi; grafo esaustivo (senza duplicati) ~180.000 stati; 15-puzzle ~10^13 stati.

Due euristiche ammissibili classiche: **h1 = tessere fuori posto** (ogni tessera fuori posto va mossa almeno una volta), **h2 = distanza di Manhattan** (ogni mossa avvicina una tessera al più di 1 posizione). Confronto **sperimentale**: si generano molte istanze, si applica A* con ciascuna euristica, si confrontano nodi espansi medi a parità di profondità soluzione. **Effective branching factor b\***: N+1 = 1+b*+...+(b*)^d (N=nodi generati, d=profondità soluzione) — più b* è vicino a 1, più l'euristica è informativa. Sperimentalmente h2 (Manhattan) produce sistematicamente meno nodi/b* più basso di h1.

**Dominanza** (criterio teorico a priori): se h2(n)≥h1(n) ∀n (entrambe ammissibili), h2 **domina** h1 ⟹ A* con h1 espande un sovrainsieme dei nodi espansi con h2 (perché A* espande tutti i nodi con f(n)<C*, cioè h(n)<C*-g(n)). Nell'8-puzzle h2 domina h1.

**Problemi rilassati**: rimuovendo vincoli si ottiene un supergrafo che contiene anche le soluzioni ottime originali ⟹ il costo della soluzione ottima nel problema rilassato è **sempre** un'euristica ammissibile per l'originale. Nell'8-puzzle: rilassare solo "B deve essere vuota" (tessera si muove verso adiacente anche occupata) ≈ h2; rilassare entrambi i vincoli (adiacenza + cella vuota) ⟹ h1. **Absolver II** (Prieditis 1993): sistema storico che genera automaticamente euristiche ammissibili per rilassamento sistematico (scoprì la prima euristica nota per il Cubo di Rubik).

Più euristiche ammissibili non comparabili: `h(n)=max(h1(n),...,hk(n))` è ammissibile e dominante su tutte le componenti. Alternativa: **apprendere le euristiche induttivamente** da feature + dati raccolti risolvendo molti problemi casuali.

---

# Modulo 3 — Ricerca con avversario (giochi)

Minsky (1968): i giochi danno "la massima complessità con le minime strutture iniziali" — banco di prova ideale per l'IA (interseca matematica, CS, economia, psicologia).

**Ambiente competitivo**: obiettivi degli agenti **conflittuali**. Tassonomia (2 assi): **informazione perfetta** (scacchi, dama, Otello, Forza4, tris) vs **imperfetta** (Mastermind, Scarabeo, Bridge, Poker); **deterministici** vs **stocastici** (dadi: Backgammon, Monopoli, Risiko). Il modulo tratta giochi **deterministici, informazione completa, 2 giocatori, somma zero**.

**Somma zero**: u(A)=-u(B) per ogni stato terminale — basta un solo valore per nodo. Il **tris** mostra fenomeni chiave: branching a ogni turno, ambiente **multi-agente** (solo parzialmente controllabile), una vittoria "lontana" è più rischiosa di una immediata (l'avversario può reagire), in svantaggio conviene prolungare la partita (più occasioni di errore avversario).

**Differenze dalla ricerca classica**: si cerca una **strategia** (funzione stato→mossa), non un cammino; niente g(x) (costo azioni uniforme, si guarda solo vittoria/sconfitta/pareggio); anche l'avversario muove, non controllabile.

**Formalismo**: MAX muove per primo, MIN è l'avversario. Osservabilità totale (turni) o parziale (mosse simultanee). **Ipotesi di pessimismo**: l'avversario è infallibile, gioca sempre la mossa a lui più favorevole. **Ply** = mezzo turno (turno completo = 2 ply). **Albero di gioco**: radice=stato iniziale, nodi MAX/MIN alternati, foglie=stati terminali con utilità.

**Minimax**: `Minimax(n) = Utilità(n)` se terminale, `max succ` se nodo MAX, `min succ` se nodo MIN — calcolato bottom-up. È visita DFS ricorsiva (MAX-VALUE/MIN-VALUE alternati). **Complessità**: tempo O(b^m), spazio O(bm) (lineare, tipico della DFS). **Completo** (alberi finiti), **ottimo** solo se entrambi giocano in modo ottimale (altrimenti resta comunque *sicuro*, garantisce almeno quel valore). Estensione a n giocatori: vettore di utilità ⟨u1,...,uk⟩ per nodo (possibili alleanze). Con 2 giocatori a somma zero basta un solo valore perché u2=-u1; con ≥3 non vale più questa relazione.

**Teoria delle decisioni** (esiti non controllabili, es. tabella payoff investimenti): **maximax** (ottimistico: massimo dei massimi, rischia ma può cogliere l'occasione migliore), **maximin** (pessimistico/conservativo: massimo dei minimi, minimizza la perdita peggiore — logica identica a Minimax), **minimax regret** (minimizza il rimpianto massimo, regret = best payoff scenario − payoff scelta fatta — bilancia le altre due visioni). Nei giochi, la "dinamica non controllabile" sono le mosse dell'avversario: Minimax = maximin applicato ricorsivamente lungo l'albero.

**Potatura alfa-beta**: mantiene α (massimo lower bound per MAX lungo il cammino, inizial. -∞, aggiornato nei nodi MAX) e β (minimo upper bound per MIN, inizial. +∞, aggiornato nei nodi MIN). Si continua a esplorare solo se il valore è in [α,β]. **Si pota quando β≤α** (test non stretto `≤`, non `<`): **beta-pruning** in un nodo MIN quando trova v≤α; **alfa-pruning** in un nodo MAX quando trova v≥β. Trova **sempre la stessa mossa e lo stesso valore** di Minimax, ma nel **caso migliore O(b^(m/2))** (dimezza l'esponente: con b=2,m=8 si passa da 256 a 16 nodi). **Dipende criticamente dall'ordinamento delle mosse**: se il killer move è esaminato per ultimo, il guadagno crolla; ordinamento ottimale → O(b^(m/2)) (branching effettivo ≈ √b, es. scacchi b=35→~6); ordine casuale (caso medio) → O(b^(3m/4)); ordine pessimo → degenera in Minimax puro O(b^m). Come trovare killer moves: apprendimento da esperienze passate, combinazione con iterative deepening (info dai livelli superficiali per ordinare quelli profondi), **tabelle di trasposizione** (hash table per riconoscere stati raggiunti da ordini di mosse diversi ed evitare di riesplorarli — politiche LRU se la memoria non basta).

**Real-time e cutoff**: alfa-beta deve comunque arrivare ai terminali — troppo lento con vincoli di tempo. Si introduce un **test di taglio** (profondità massima predefinita, o iterative deepening con tempo limitato) che restituisce `eval(stato)` invece di aspettare il terminale. **Funzione di valutazione euristica**: combinazione **lineare** pesata di feature, `eval(s)=Σwi·fi(s)` (es. scacchi: numero di pedoni/alfieri/torri...). **Problema dell'orizzonte**: la valutazione può essere instabile proprio nel punto di taglio, rischiando di non "vedere" un ribaltamento imminente. **Quiescenza** (Berliner 1973): tagliare solo dove la valutazione è **stabile/quiescente**; nodi non quiescenti richiedono ulteriore esplorazione.

Cenno ai **giochi stocastici** (expectiminimax): nodi di caso (chance) il cui valore è il valore atteso (media pesata sulle probabilità) dei successori, non max/min — non approfondito nelle slide del corso.

**Programmi storici**: Checkers (Samuel, Chinook), Othello (Logistello), Backgammon (TD-gammon), Go (AlphaGo), Bridge (Bridge Baron, GIB), Scacchi (DeepBlue). **DeepBlue**: primo a battere un campione del mondo in carica (Kasparov, 10 feb 1996), 200M posizioni/sec, iterative deepening + alfa-beta + tabelle di trasposizione, profondità tipica 14 (fino a 40), eval con >8000 feature, 700.000 partite di gran maestri nel database. **AlphaGo** (Google, 2015): primo a battere un maestro umano a Go senza handicap; deep learning + ricerca ad albero, addestrato su 30M mosse umane + self-play; versione a cluster (1202 CPU+176 GPU) batteva la versione single-computer nel 77% delle partite.

Parallelo memoria umana: Legge di Miller (1956, 7±2 elementi in memoria a breve termine), revisione di Cowan (2001, 4±1).

---

# Modulo 4 — Constraint Satisfaction Problems (CSP)

Rispetto alla ricerca "scatola nera", nei CSP **lo stato ha struttura interna esplicita** (variabili+valori) e i vincoli sono dichiarativi: permette algoritmi generali e potatura molto più efficace.

**CSP** = variabili X1..Xn, domini D1..Dn, vincoli C1..Cm, opzionale funzione obiettivo. **Assegnamento** {Xi=vi,...}: **completo** (tutte le variabili), **consistente** (nessun vincolo violato), **soluzione** = completo+consistente. Esempio guida: colorazione mappa Australia (7 territori, 3 colori, vincoli binari sui confini) — qualunque permutazione dei colori di una soluzione è ancora soluzione (simmetria).

**Domini**: finiti (vincoli enumerabili, es. booleani → CSP NP-completo tipo 3-SAT), infiniti discreti (linguaggi di specifica, es. Lavoro1+5<Lavoro2), continui (con vincoli lineari → programmazione lineare, polinomiale).

**Arità vincoli**: unari (una variabile, es. T≠G), binari (grafo di vincoli), n-ari (ipergrafo, es. `diverse(WA,NT,SA)`, criptoaritmetica SEND+MORE=MONEY con vincolo alldifferent + equazione aritmetica globale non scomponibile). Vincoli rigidi (obbligatori) vs **criteri di preferenza/soft** (violabili, servono a ordinare le soluzioni ammissibili).

**CSP come ricerca**: stato iniziale={}, successore=assegna valore a variabile non assegnata, goal=assegnamento completo, costo=costante (profondità max = n). **Commutatività**: l'ordine di assegnamento non conta (stesso stato finale) ⟹ si fissa sempre prima la variabile poi il valore, riducendo il branching da n·d (foglie n!·d^n) a **d** per livello (foglie d^n — es. Australia: da 11.022.480 a 2.187 foglie).

**Generate-and-test**: genera assegnamento completo, testa consistenza — esplosione combinatoria (8 regine: 64^8≈2,8×10^14 con rappresentazione ingenua, 8^8≈16,7M con "una regina per colonna"; 16 regine ≈1200 anni). **Backtracking** (DFS + potatura sui vincoli appena si genera un conflitto): soffre di **thrashing** (ripete lo stesso errore in punti diversi dell'albero, non "ricorda" il perché del fallimento).

**Pseudocodice backtracking**: `BACKTRACK(assegnamento,csp)`: se completo→restituisci; scegli variabile non assegnata, per ogni valore consistente prova ad assegnare, propaga inferenze, ricorri; se tutti i valori falliscono→fallimento (backtrack al chiamante).

**Euristiche variabile**: **MRV** (Minimum Remaining Values / fail-first: scegli la variabile con meno valori legali residui, per scoprire subito i vicoli ciechi); **degree heuristic** (tie-breaker o per la prima variabile: scegli quella coinvolta nel maggior numero di vincoli con variabili non assegnate). **Euristica valore**: **LCV** (Least Constraining Value: scegli il valore che lascia più opzioni residue ai vicini, per massimizzare la probabilità di successo del ramo). Non è contraddittorio usare "più vincolata" per la variabile e "meno vincolante" per il valore: si sceglie *dove* rischiare di fallire subito, poi *come* minimizzare il rischio lì.

**Propagazione/inferenza** (consistenza locale, crescente forza/costo):
- **Forward checking**: quando si assegna una variabile, elimina subito dai domini dei vicini diretti i valori incompatibili (si integra naturalmente con MRV). **Limite**: non rileva inconsistenze fra due vicini non ancora assegnati (es. NT e SA entrambi ridotti allo stesso unico valore, pur essendo confinanti — se ne accorge solo più avanti).
- **Node consistency**: rispetto dei vincoli unari (preprocessing sui domini iniziali).
- **Arc consistency (AC-3, Mackworth 1977)**: un arco X→Y è consistente se per ogni valore di X esiste ≥1 valore compatibile in Y. Coda di archi; se si elimina un valore da Xi, si rimettono in coda tutti gli archi entranti in Xi. Costo O(n²d³) (n²=archi max, d=dominio max). **Incompleta**: arc-consistent non implica soluzione (esempio: triangolo a 3 nodi, 2 colori, tutti "diversi" — arc consistent ma insolubile). Usata come preprocessing o intrecciata col backtracking (**MAC**, Maintaining Arc Consistency).
- **Path consistency (PC-2)**: più forte, ragiona su triplette di variabili — rileva insolubilità dove arc consistency fallisce (es. Australia a 2 colori: coppia {WA,SA} + NT).
- **k-consistency**: generalizza (1=node, 2=arc, 3=path); un CSP **fortemente n-consistent** si risolve **senza backtracking** in O(nd), ma verificare il grado di consistenza è esso stesso esponenziale (risultato più teorico che pratico).

**Vincoli globali**: **Alldifferent** (se <n valori disponibili per n variabili → fallimento immediato, pigeonhole); **Atmost(N,A1..Ak)** (vincolo di risorse, propagazione su somme di minimi/massimi o su intervalli per domini grandi).

**Backtracking cronologico vs backjumping**: il cronologico torna sempre alla variabile immediatamente precedente, anche se non è la causa del conflitto (spreco). **Backjumping**: usa il **conflict set** (assegnamenti che hanno causato il conflitto) per saltare direttamente alla variabile realmente responsabile. Se combinato con forward checking arricchito (che già costruisce i conflict set), il backjumping "puro" diventa **ridondante**. **NOGOOD**: assegnamento parziale non estendibile a soluzione, scoperto solo esplorando. **Conflict-directed backjumping**: aggiorna dinamicamente i conflict set (`conf(Xi) ← conf(Xi)∪conf(Xj)−{Xi}`), scoprendo relazioni implicite fra variabili anche non direttamente confinanti — è, di fatto, una forma di apprendimento (simile al clause learning dei SAT solver).

**Applicazioni**: Sudoku (tutto Alldifferent su righe/colonne/riquadri), N-regine su larga scala (local search/min-conflicts arriva a N=6.000.000), location of facilities, job scheduling, car sequencing, cutting stock, vehicle routing, timetabling, crew scheduling (es. equipaggi treni FS con ECLiPSe, 1998). Software: ECLiPSe, CHR, SAT solver (DPLL + backjumping + apprendimento clausole, es. MiniSat), GECODE, Answer Set Programming.

---

# Modulo 5 — Rappresentazione della conoscenza e Logica proposizionale

**Ragionare** = rendere esplicita conoscenza implicita, lavorando **sulla forma** delle affermazioni (schemi astratti), non sul contenuto — è ciò che rende il ragionamento automatizzabile: (1) un linguaggio, (2) regole di ragionamento, (3) un algoritmo che le applica.

**Agente basato sulla conoscenza**: **KB** (base di conoscenza, evolve nel tempo) + **tell/assert** (aggiungi formule) + **ask/query** (interroga). Vincolo: ogni risposta ad ask deve essere **conseguenza logica** delle tell + background knowledge. Schema KB-Agent: ad ogni ciclo, tell(percezione) → azione=ask(query) → tell(azione) → tempo++. Variante con `modify` (aggiunge *e rimuove* fatti, non solo accumula — il mondo cambia).

**Dato** (grezzo, senza significato) → **informazione** (cosa rappresenta) → **conoscenza** (relazioni fra informazioni). Esempio **bug algorithm**: agente con conoscenza locale, avanza in retta e fa wall-following agli ostacoli — mostra come la KB cresce ciclo dopo ciclo.

**Programmazione dichiarativa**: si specifica la KB (cosa è vero/cosa fare) in forma dichiarativa, con meccanismi generali ask/tell validi per qualunque KB (vs procedurale, tutto codificato ad hoc). Esempi: XML, SQL, regex. Esempio **mondo dei blocchi**: azioni con precondizioni ed effetti (`add`/`delete`), es. `pick(x,y)`: precondizioni `on(x,y)∧clear(x)∧handempty`, effetti `add(clear(y)),add(holding(x)),delete(on(x,y)),delete(clear(x)),delete(handempty)`.

## Concetti fondamentali della logica

**Modello** m: mondo possibile che fissa il valore di verità delle formule; **M(α)** = insieme dei modelli di α. **Conseguenza logica** A⊨B: B vera in *tutti* i modelli in cui A è vera ⟺ M(A)⊆M(B) (attenzione: A⊭B significa solo che *esiste* un controesempio, non che B sia sempre falsa). **Equivalenza** A≡B ⟺ M(A)=M(B). **Validità/tautologia** (vera in ogni modello, es. Q∨¬Q), **insoddisfacibilità/contraddizione** (falsa in ogni modello, es. Q∧¬Q; P valida ⟺ ¬P insoddisfacibile), **soddisfacibilità** (vera in ≥1 modello — nei CSP si cerca proprio un modello che soddisfi i vincoli).

**Inferenza**: processo **sintattico** (lavora sulla struttura, non sul significato). **Modus Ponens** (da A⇒B e A, deriva B), **eliminazione della congiunzione** (da A∧B deriva B). `KB⊢ᵢA`: A derivabile da KB con l'algoritmo i. **Correttezza (soundness)**: KB⊢ᵢA⟹KB⊨A (mai conclusioni sbagliate — **sempre richiesta**). **Completezza**: KB⊨A⟹KB⊢ᵢA (non perde conclusioni valide — non sempre garantita). **Grounding**: legame fra rappresentazione simbolica e ambiente reale (deriva dalla percezione).

## Logica proposizionale

Simboli proposizionali (no variabili), True/False. Formule complesse: negazione ¬ (letterale=atomica eventualmente negata), congiunzione ∧ (congiunti), disgiunzione ∨ (disgiunti), implicazione ⇒ (premessa/conclusione), biimplicazione ⇔. Precedenza: ¬,∧,∨,⇒,⇔.

**Semantica** (ricorsiva): con N simboli, **2^N modelli**. `¬Q` vera sse Q falsa; `Q∧P` sse entrambe vere; `Q∨P` sse almeno una vera; `Q⇒P` sempre vera tranne Q vera e P falsa; `Q⇔P` sse stesso valore. **P⇒Q ≡ ¬P∨Q**: se P falsa, vera "vacuamente" indipendentemente da Q; **non è una relazione causale** (es. "Torino è in Lombardia⇒Cesare governò Roma" è VERA perché l'antecedente è falso — l'implicazione dipende solo dai valori di verità, non dal significato/causa).

**Verificare KB⊨P**: (1) **model checking** (enumera 2^N modelli, costoso) o (2) **theorem proving**. **Teorema di deduzione**: (R⊨Q) sse (R⇒Q) è valida. **Dimostrazione per refutazione**: (R⊨Q) sse (R∧¬Q) è insoddisfacibile — si nega il goal, si cerca una contraddizione (`False`), analogo a una ricerca nello spazio degli stati. Vale per **logiche monotone**: KB⊨P ⟹ KB∧Q⊨P (aggiungere info non invalida conclusioni già derivate).

**Equivalenze logiche** (regole di inferenza derivate): commutatività/associatività di ∧/∨, doppia negazione, contrapposizione (α⇒β ≡ ¬β⇒¬α), eliminazione implicazione (α⇒β≡¬α∨β), **De Morgan** (¬(α∧β)≡¬α∨¬β; ¬(α∨β)≡¬α∧¬β), distributività, eliminazione bicondizionale. Un sottoinsieme incompleto di regole può perdere completezza (es. senza doppia negazione non si deriva P⊢¬¬P).

**Risoluzione**: regola singola che, con un algoritmo di ricerca completo, dà un procedimento **corretto e completo**. Si applica a **clausole** (disgiunzioni di letterali): da due clausole con letterali complementari, il **resolvent** contiene tutti i letterali tranne la coppia complementare (fattorizzato se ripetuti). **Modus ponens è un caso particolare** di risoluzione.

**CNF** (congiunzione di clausole): (1) elimina ⇔ (α⇔β → (α⇒β)∧(β⇒α)), (2) elimina ⇒ (α⇒β → ¬α∨β), (3) porta la negazione dentro (De Morgan, doppia negazione), (4) distribuisci ∨ su ∧.

**Algoritmo CP-RISOLUZIONE(KB,A)**: CNF di (KB∧¬A); risolvi iterativamente tutte le coppie di clausole; se si genera la **clausola vuota** → true (KB⊨A); se non si generano più nuove clausole senza averla trovata → false. Esempio applicativo pioggia/atmosfera/strada: negando il goal e risolvendo a catena (5 passi) si arriva alla clausola vuota, confermando l'entailment.

**Clausole di Horn**: al più un letterale positivo (esattamente uno = clausola definita); catturano implicazioni con antecedente congiuntivo (`¬A∨¬B∨C ≡ A∧B⇒C`), base della programmazione logica (Prolog). Permettono inferenza in **tempo lineare** (molto più efficiente della risoluzione generale).

**Forward chaining**: parte dai fatti noti, applica modus ponens iterativamente (rappresentabile con grafo AND-OR), aggiunge alla KB ogni conseguente le cui premesse sono tutte vere, fino a derivare la query. **Data-driven**, completo, **lineare**, ma può fare inferenze irrilevanti (adatto a riconoscimento di pattern/oggetti).

**Backward chaining**: parte dal goal; se non è già un fatto, cerca clausole che lo concludono e dimostra ricorsivamente le premesse (i valori si propagano dal basso verso l'alto). **Goal-driven**, generalmente più efficiente (focalizzato), usato in theorem proving e Prolog. Attenzione a evitare loop e a non ridimostrare sottogoal già dimostrati.

---

# Modulo 6 — Logica del primo ordine (FOL)

**Pregi della proposizionale da conservare**: dichiarativa, composizionale (verità delle parti → verità del tutto), non ambigua. **Limiti**: non compatta (una regola per ogni individuo, es. `ascoltaMusica(mia)⇐felice(mia)` ripetuta per ognuno), non esprime relazioni fra oggetti (`padre(x,y)`). Cenno ad altre logiche specializzate: temporale, epistemica, deontica, fuzzy — FOL scelta perché mantiene dichiaratività/composizionalità/non-ambiguità aggiungendo espressività.

**FOL**: il mondo è fatto di **oggetti** in **relazione**. Sintassi: costanti (oggetti specifici), predicati (proprietà/relazioni → vero/falso), funzioni (→ un oggetto, non lo costruiscono, lo *riferiscono* — es. `GambaSinistra(John)`), variabili, connettivi, uguaglianza =, quantificatori ∀∃.

**Modello FOL** M=(D,I): D=dominio (≥1 oggetti+relazioni), I=interpretazione (costanti→oggetti, predicati→relazioni, funzioni→relazioni funzionali). **Il valore di verità dipende sempre dal modello scelto** — cambiare i nomi mantenendo la struttura non cambia la verità; cambiare l'interpretazione (anche solo dei predicati) sì. **Termine ground** = senza variabili. In FOL, con dominio illimitato, i **modelli possono essere infiniti** (per ogni cardinalità del dominio, ogni interpretazione possibile...) → l'enumerazione dei modelli, praticabile in proposizionale (2^N), **non è più praticabile**.

**Formula atomica**: predicato(termini) o termine=termine. **Quantificatori**:
- `∀x F`: vera se F vera per ogni interpretazione di x. **Regola pratica: ∀ va con ⇒** (per restringere a una sottoclasse: `∀x Partecipa(x,C)⇒Intelligente(x)` — con ∧ si affermerebbe che *tutti gli oggetti del dominio* partecipano E sono intelligenti, sbagliato).
- `∃x F`: vera se F vera per almeno un x. **Regola pratica: ∃ va con ∧** (`∃x Partecipa(x,C)∧Intelligente(x)` — con ⇒ basterebbe un solo oggetto qualsiasi che *non* partecipa per rendere vera la formula, indipendentemente da chi sia intelligente: errore insidioso).
- **Quantificatori diversi non commutano**: `∀x∃y Ama(x,y)` (ognuno ama qualcuno, anche diverso) ≠ `∃y∀x Ama(x,y)` (esiste un unico y amato da tutti — implica la prima, non viceversa). Stesso tipo invece commuta liberamente (`∃x∃y≡∃y∃x`, `∀x∀y≡∀y∀x`).
- De Morgan generalizzato: `∀x¬F≡¬∃xF`, `∃x¬F≡¬∀xF`, `∀xF≡¬∃x¬F`, `∃xF≡¬∀x¬F`.

**Uguaglianza**: riguarda solo termini. "John ha almeno due fratelli" richiede esplicitamente `∃y,z Fratello(John,y)∧Fratello(John,z)∧¬(y=z)` (senza `¬(y=z)` sarebbe soddisfatta anche se y,z fossero lo stesso oggetto). **Problema dell'unicità dei nomi**: `Fratello(John,Richard)∧Fratello(John,Ramon)` non esclude che Richard e Ramon siano la stessa persona nella semantica standard FOL. **Database semantics** (Prolog): Unique Names Assumption + Closed-World Assumption + Domain Closure — molto più intuitiva, riduce i modelli possibili (spesso finiti), ma va tenuta distinta dalla semantica standard di R&N.

**Inferenza in FOL**: (1) **proposizionalizzazione** + algoritmo proposizionale, o (2) **lifting** delle regole (più efficiente).

**UI** (istanziazione universale): da `∀xα` deriva `SUBST({x/g},α)` per **qualsiasi** termine ground g — KB equivalente. **EI** (istanziazione esistenziale): da `∃xα` deriva `SUBST({x/k},α)` con k **costante nuova** (skolemizzazione), applicata **una sola volta**; KB solo equivalente *inferenzialmente*, non logicamente. Con funzioni annidabili, i termini ground possono essere infiniti. **Teorema di Herbrand**: se una formula è conseguenza logica, esiste una dimostrazione **finita** costruendo i termini in ampiezza. Conseguenza: **FOL è semidecidibile** (si conferma sempre il "sì", ma se la conseguenza non vale la ricerca può non terminare mai — non esiste un algoritmo generale che dimostri il "no"). La proposizionalizzazione è comunque **inefficiente** (genera istanze inutili per ogni costante del vocabolario).

**Modus Ponens Generalizzato (MPG)**: da p'1,...,p'n e (p1∧...∧pn⇒q), se esiste θ con p'iθ=piθ ∀i, si conclude qθ. Richiede l'antecedente = congiunzione di letterali positivi; è il **lifting** del modus ponens (variabili + unificazione, arbitrario numero di premesse).

**Unificazione**: UNIFY(F1,F2)=θ tale che F1θ=F2θ; se ne esistono più, si preferisce il **Most General Unifier (MGU)**. Può fallire per conflitto di variabile (es. `UNIFY(Conosce(John,x),Conosce(x,Richard))` fallisce) — si risolve con la **standardizzazione separata** (rinomina le variabili di formule diverse prima di unificare).

**Clausole di Horn FOL**: fatti (`Avido(x)` o `Avido(John)`) + implicazioni con antecedente congiuntivo positivo. **DATALOG** = Horn + niente funzioni. Esempio guida "Sotto Casa" (vendita alcolici a minorenne): formalizzazione con costanti/predicati, skolemizzazione di `∃x Possiede(Marco,x)∧Birra(x)` in una costante di Skolem B, forward chaining via MPG fino a `Reo(SottoCasa)`.

**Forward chaining FOL**: un fatto è **rinomina** di un altro se identico a meno dei nomi delle variabili — si aggiunge alla KB solo se non è rinomina di uno già presente. Propaga sia verità sia **sostituzioni** lungo il grafo AND-OR. Corretto sempre; **completo e termina su DATALOG**; con funzioni può non terminare (Herbrand).

**Backward chaining FOL**: goal in uno stack; si estrae, si cercano clausole la cui testa unifica col goal (se unifica con un fatto, si rimuove/risolve; altrimenti si inseriscono ricorsivamente le premesse nello stack con le sostituzioni). Successo quando lo stack è vuoto. **Composizione delle sostituzioni**: `SUBST(COMPOSE(θ1,θ2),F)=SUBST(θ2,SUBST(θ1,F))`. Corretto, **incompleto** (depth-first, rischio loop infiniti), generalmente più efficiente del forward chaining.

**Risoluzione in FOL** (lifting + refutazione): KB tradotta in **CNF** (variabili implicitamente universali). 6 passi: elimina ⇔/⇒ → sposta negazioni dentro → standardizza variabili (occorrenze diverse di ∃y in scope diversi sono indipendenti) → **skolemizza** → elimina ∀ residui → distribuisci ∨ su ∧.

**Skolemizzazione**: ogni `∃y` (nello scope di `∀x1,x2,...`) diventa una **funzione di Skolem** `S(x1,x2,...)` con argomenti = tutte le variabili universali nel cui scope ricade; se non ricade in alcun ∀, degenera in una **costante di Skolem** (=EI). Errore classico: sostituire un `∃y` sotto un `∀x` con una singola costante fissa afferma erroneamente che *tutti gli x* condividono lo stesso y (es. "ogni persona abita in un luogo" → skolemizzare con costante fissa direbbe che tutti abitano nello stesso posto; serve `luogo(x)`, funzione di Skolem). Gli argomenti di una funzione di Skolem dipendono esattamente dallo **scope** (l'ordine di annidamento, non l'ordine di scrittura): se `∃z` è il quantificatore più esterno (`∃z∀x,y F`), z è un'unica costante (non dipende da x,y).

**Binary resolution liftata**: da `l1∨...∨lk` e `m1∨...∨mn`, se θ unifica li con ¬mj, il resolvent è `SUBST(θ, ...)` (tutti i letterali tranne quella coppia). Le clausole non devono condividere variabili (standardizzazione separata); la **fattorizzazione liftata** riduce letterali *unificabili* (non solo sintatticamente uguali). Binary resolution + fattorizzazione = **completa**. Esempio classico "Curiosity ha ucciso il gatto?": formalizzazione FOL di 6 premesse + negazione del goal, CNF con skolemizzazione (funzioni di Skolem F(x), G(x)), catena di risoluzioni fino alla clausola vuota.

**Refutation-completeness**: la risoluzione non enumera *tutte* le conseguenze, ma è **refutation-complete** — se KB è insoddisfacibile, deriva sempre in tempo finito la clausola vuota; quindi può sempre confermare KB⊨Q verificando che KB∧¬Q sia insoddisfacibile.

**Ingegneria della conoscenza**: (1) identificare l'uso della KB, (2) raccogliere conoscenza informale, (3) definire vocabolario, (4) formalizzare in FOL; poi per interrogare: descrivere l'istanza specifica + query.

---

# Modulo 7 — Tassonomie/Ontologie e Pianificazione automatica

## Tassonomie e ontologie

**Tassonomia** = organizzazione gerarchica (albero) di concetti tramite relazione **Is-a** (sottoclasse): tutte le istanze di una sottoclasse sono anche istanze della superclasse. Le istanze **ereditano** le proprietà delle sovraclassi (es. `Member(X,Pallone)⇒Sferico(X)` vale per ereditarietà anche per `PalloneCalcio`) — evita ridondanza, permette inferenza automatica.

**Decomposizioni**: su un insieme S={X1,...,Xn} di sottocategorie di C, si può rendere esplicito: **Disjoint(S)** (nessuna istanza in comune), **ExhaustiveDec(S,C)** (ogni istanza di C appartiene ad almeno una Xi), **Partition(S,C)** = Disjoint∧Exhaustive.

**Relazioni strutturali**: **Part-of** (transitiva: Part-of(X,Y)∧Part-of(Y,Z)⇒Part-of(X,Z)) descrive di cosa è fatta una cosa; **Bunch-of** (mucchio) per aggregati senza relazioni interne specificate fra le parti (`Bunch-of(s)=s`).

**T-box** (schema/definizioni generali, intensionale) vs **A-box** (fatti su istanze specifiche, estensionale, coerenti con la T-box) — come lo schema di un DB rispetto ai suoi record.

**Problematiche**: **eccezioni al default** (proprietà che valgono "di solito" ma con eccezioni: uccelli volano tranne struzzi/pinguini/kiwi — una sotto-sottoclasse può cancellare una proprietà ereditata); **polisemia** (stessa parola, concetti/alberi tassonomici diversi, es. "cane" animale/costellazione/persona vile/dente meccanico — il motore inferenziale non deve mischiare le tassonomie; problema di identificazione univoca dei concetti).

**Ontologia** generalizza la tassonomia: da **albero** (solo Is-a) a **grafo** (Is-a + Part-of + relazioni di dominio arbitrarie, es. `haMoglie`). Ogni tassonomia è un'ontologia, non viceversa. Interrogazioni tipiche: istanza∈categoria?, istanza ha proprietà?, differenza fra categorie?, identificazione di istanze. Esempio applicativo: **PROV** (W3C, provenienza dei dati: Agente/Attività/Entità, `wasGeneratedBy`, `used`, `wasDerivedFrom`).

**Semantic Web** (Tim Berners-Lee, standard W3C): **RDF** (triple soggetto-predicato-oggetto; soggetto/predicato/oggetto sono **IRI**, identificatori univoci globali — risolve il problema della polisemia; grafo RDF; serializzato in XML/Turtle/N3), **RDFS** (tassonomie su RDF), **SPARQL** (query, come SQL per RDF), **OWL 2** (linguaggio dichiarativo per ontologie: Entità/Assiomi/Espressioni; costrutti `ClassAssertion`, `SubClassOf`, `EquivalentClasses`, `DisjointClasses`, `ObjectPropertyAssertion`, `ObjectSomeValuesFrom`/`ObjectAllValuesFrom`; **open world assumption** — a differenza dei DB, un fatto assente è *sconosciuto* non falso; ammette definizioni multiple distribuite), **FOAF** (ontologia sociale: Agent/Person/Group, name/knows/age).

**Costruire un'ontologia**: identificare concetti (sostantivi, sottoclassi) → identificare proprietà (verbi) → riuso di ontologie esistenti → scrittura formale (T-box) → annotazione dati (A-box) → validazione → sistema di interrogazione. Strumenti: Protégé, reasoner (FaCT++, HermiT, Pellet, RacerPro), Apache Jena, AllegroGraph.

**Relazioni fra ontologie**: Identical (stessa ontologia), Equivalent (stesso vocabolario/assiomatizzazione, linguaggio diverso, es. SKOS vs RDF), Extension (una estende l'altra, non viceversa), Weakly-Translatable (traduzione con perdita di informazione), Strongly-Translatable (fedele: vocabolario totalmente mappabile, assiomatizzazione preservata, senza perdita né inconsistenze), Approx-Translatable (weak + possibili inconsistenze, concetti solo affini, es. coriandolo=prezzemolo o pepe a seconda della tradizione). L'**ontology alignment/matching** è in generale imperfetto. FIPA prevede un *ontology agent* dedicato per discovery/traduzione fra ontologie di agenti diversi.

Is-a e Part-of sono relazioni **statiche**: non catturano **azione** e **cambiamento nel tempo** → serve un formalismo dedicato (ponte verso la pianificazione).

## Pianificazione automatica

**Pianificare** = costruire una sequenza di azioni che, da uno stato iniziale, soddisfa un goal. **PDDL** = standard per descrivere problemi di pianificazione. Stato = congiunzione di **atomi ground**. Le azioni sono **schematiche/parametriche**, con impatto limitato, una sola eseguita per volta; se eseguita nel mondo reale **potrebbe non essere possibile fare backtracking**.

Differenze dalla ricerca classica: rappresentazione **logica strutturata** di stati/azioni (predicati, precondizioni, effetti) invece che atomica; goal tipicamente **scomposto in sottoobiettivi**; attenzione esplicita a rappresentare gli **effetti** delle azioni (frame problem).

**Situation Calculus** (fondamento in FOL): **Azione** = funzione (non predicato, oggetto "intangibile", es. `Move(R,L1,L2)`); **Situazione** = stato risultante da una sequenza di azioni; **Fluente** = proprietà che cambia con le azioni, sempre parametrizzata sulla situazione (es. `Holds(At(R,Loc),s)`); predicati/funzioni **atemporali** non dipendono dalle azioni. `Do(Azioni,S)`: `Do([],s)=s`; `Do([a|resto],s)=Do(resto,Risultato(a,s))`. Due situazioni sono identiche solo se stessa storia: `Do(Az1,S1)=Do(Az2,S2) ⇔ Az1=Az2 ∧ S1=S2`. Permette **proiezione**: verificare vincoli lungo un piano o pianificare per un goal finale.

- **Assioma di applicabilità**: `Applicable(Action(params),s) ⇔ Precond(params,s)`.
- **Assioma di effetto**: `Applicable(Action(params),s) ⇒ Effects(params,Result(Action(params),s))`.

Esempio guida mondo dei blocchi `Move(x,y,z)`: applicabilità `Clear(x,s)∧Clear(z,s)∧On(x,y,s)∧x≠z∧y≠z∧x≠Table`; effetto `On(x,z,...)∧Clear(y,...)`.

**Frame problem**: come rappresentare ciò che un'azione **NON** modifica (non derivabile dai soli assiomi di applicabilità/effetto)? Soluzioni: (1) **enumerare esplicitamente** un assioma di frame per ogni coppia azione×fluente non toccato (esplode combinatoriamente al crescere delle proprietà); (2) **assioma di stato successore** unico per fluente: "azione applicabile ⇒ (fluente vero dopo ⇔ l'azione lo rende vero ∨ (era vero ∧ l'azione non l'ha reso falso))" — compatta tutto in uno schema, evitando l'enumerazione. Completato da assiomi di **unique action names** (azioni con nomi diversi sono oggetti diversi; stesso nome+argomenti uguali ⇒ stessa azione).

**Scomposizione in sottogoal**: approccio base — risolvere i sottoobiettivi (in principio) uno alla volta. **Anomalia di Sussman**: stato iniziale A su B, C isolato; goal = pila A-B-C. I sottogoal "A su B" e "B su C" **interagiscono**: perseguendo prima l'uno si disfano i progressi dell'altro (e viceversa). **Soluzione: interleaving** dei passi dei due sottopiani (es. sposta C, sposta A da B, sposta B su C, sposta A su B) invece di eseguirli a blocchi separati e sequenziali. Dimostra che i sottoobiettivi non sono sempre indipendenti e un planner efficace deve intrecciare i passi.

Il Situation Calculus è stato storicamente fondamentale (fonda la pianificazione su FOL) ma **poco usato in pratica**: mancano euristiche efficienti per lo spazio (enorme) delle sequenze di azioni. I planner moderni usano PDDL con algoritmi/euristiche dedicate (planning graph ecc.) — approfondito nel corso magistrale "IA e Laboratorio".

---

# Modulo 8 — Machine Learning: Classificazione, Alberi di Decisione, Reti Neurali

## Classificazione

**Le classi non esistono in natura**: sono definite dal progettista in base allo scopo del classificatore; il sistema **non ha altra conoscenza oltre ai dati** e impara esattamente ciò che c'è nei dati come etichettati.

Dati: **esempi/istanze** (oggetti) + **categorie/classi** (etichette). Obiettivo: costruire un **modello** che associ nuove istanze alla classe corretta. **Apprendimento supervisionato**: gli esempi hanno già la classe associata. Tre sottoproblemi: rappresentazione dei dati, analisi/costruzione del modello, uso della conoscenza.

Schema: **training set** → (**induzione**) → **modello** (classe=f(descrizione)) → (**deduzione**) → classe di nuove istanze; **test set** per la **valutazione** (dati non usati in training, confrontando predetto vs reale). Istanza = tupla (x,y): x=attributi descrittivi, y=classe.

**Modello predittivo** (predice la classe di istanze ignote) vs **modello descrittivo** (spiega quali caratteristiche distinguono le categorie, es. "i mammiferi hanno sangue caldo").

**Matrice di confusione** (2 classi): **Accuratezza**=(f11+f22)/tot, **Error rate**=(f12+f21)/tot. **Matrice dei costi**: pesa diversamente i tipi di errore (es. falso negativo su malattia più grave del falso positivo; costo totale = Σ costo_ij×frequenza_ij). **Attenzione**: un'accuratezza altissima (es. 99.9%) su un dataset **sbilanciato** non implica un buon modello — un classificatore banale "sempre classe maggioritaria" ottiene comunque quell'accuratezza senza aver imparato alcun pattern discriminante: bisogna guardare la matrice di confusione completa e la composizione del dataset.

**Insidie pratiche**: dati difficili da reperire → dataset non rappresentativi; bias mentale di chi raccoglie i dati (es. solo foto di mele per "riconoscere la frutta" → il modello impara solo mele); un algoritmo non ha la conoscenza di base di un umano (non sa che un frutto nasce dall'impollinazione). Applicazioni ad alto rischio: riconoscimento facciale, mutui, assicurazioni sanitarie, uso militare, guida autonoma (variante del *trolley problem*, **problem of the many hands**: responsabilità distribuita fra progettisti/produttori/chi addestra/chi usa).

**Rote learning** (apprendimento meccanico, un "non-modello"): memorizza tutte le istanze, non generalizza; su nuova istanza cerca un match identico o (se assente) istanze **simili** (misura di distanza); se le classi trovate differiscono, **votazione a maggioranza** o **pesata** (peso ∝ 1/distanza, pesi non persistenti — a differenza dei pesi di una rete neurale). Introduce il concetto di **generalizzazione**: modelli diversi (alberi, regole if-then, reti neurali=matrici di pesi, apprendimento per rinforzo=distribuzioni di probabilità) hanno rappresentazioni diverse.

## Alberi di decisione

Nodi interni = **test su attributo**; foglie = **decisione/classe**. Esempio dataset Iris (setosa/versicolor/virginica, attributi continui petal/sepal width/length).

**Algoritmo di Hunt** (ricorsivo, alla base di ID3/C4.5/CART): per ogni nodo t con dati Dt — (1) **caso base**: se tutte le istanze sono della stessa classe, t diventa foglia; (2) **passo ricorsivo**: altrimenti scegli un attributo di split, un figlio per ogni valore possibile, ricorri su ciascuno. Note: se una combinazione di valori non è rappresentata nel training set, si assegna una **classe di default**; se istanze **identiche** hanno classi diverse (non-determinismo), il nodo diventa foglia con la classe di **maggioranza**; restano da definire i **criteri di arresto** e **come scegliere l'attributo di split**.

Strategia **greedy** (nessun backtracking): 3 problemi aperti — tipo di condizione di test per attributo, come determinare lo split migliore, quando fermarsi.

**Tipi di split**: binari (2 figli), nominali (multivalore: un figlio per valore; o binario: un sottoinsieme vs resto, `2^(k-1)-1` raggruppamenti possibili), ordinali (raggruppamento deve **rispettare l'ordinamento**, es. {small,medium} vs {large,extralarge} ok, {small,large} vs {medium,extralarge} no), continui (soglia binaria A≤v, o discretizzazione multi-soglia).

**Misure di impurità** (basate su p(i|t)=probabilità di classe i nel nodo t): **Entropia** = `-Σp(i|t)log2 p(i|t)` (0 se nodo puro, massima=1 per 2 classi equidistribuite (0.5,0.5)); **Gini** = `1-Σp(i|t)²`; **errore di classificazione**. **Rasoio di Occam**: a parità di prestazioni, preferire alberi più compatti.

**Guadagno** = I(parent) − Σ(N(vj)/N)·I(vj) (impurità padre meno media pesata impurità figli); con entropia si chiama **information gain**. **Attenzione**: information gain (e Gini) **favoriscono attributi con molti valori** — un identificatore univoco (es. matricola) dà information gain massimo (ogni figlio puro con 1 istanza) ma è **overfitting totale**, zero generalizzazione. Mitigabile restringendosi a split binari.

## Reti neurali

Ispirate (non fedelmente) ai neuroni biologici. Primi modelli: **Perceptron** (Rosenblatt), B-machine (Turing).

**Perceptron**: `net=Σwi·Xi`, `Y=f(net)`. Attivazione: **gradino** (Rosenblatt originale, valori discreti 0/1, non derivabile) o **sigmoide** `Y=1/(1+e^(-α(net-θ)))` (θ=soglia/bias, α=pendenza; derivabile, necessaria per apprendimento a gradiente; per α crescente tende al gradino).

Geometricamente il perceptron codifica un **iperpiano** nello spazio N-dimensionale degli input (`w1x1+w2x2+...=0`): sopra l'iperpiano si attiva (classe 1), sotto no (classe 0). I pesi **caratterizzano il neurone** e sono **persistenti** (a differenza dei pesi "usa e getta" della votazione pesata nel rote learning). Risolve solo problemi **linearmente separabili**; apprendimento supervisionato da esempi; "imparare"=trovare la posizione corretta dell'iperpiano.

**Apprendimento**: `wj(k+1) = wj(k) + η·(d-o)·xj` (d=desiderato, o=ottenuto, η=learning rate). **Teorema di Novikoff**: converge se il problema è linearmente separabile, altrimenti non converge. **Epoca** = elaborazione (forward+backward+update) di tutte le istanze del training set; servono tipicamente molte epoche. η evita che l'apprendimento "insegua" solo l'ultimo esempio.

**Limite: XOR**. Le 4 combinazioni (0,0)→0, (1,0)→1, (0,1)→1, (1,1)→0 **non sono linearmente separabili** da nessuna retta — un solo perceptron non impara lo XOR. Soluzione: più iperpiani combinati → reti **multi-strato**.

**Rete neurale**: approssimatore universale di funzioni, neuroni collegati secondo una **topologia** (a strati/layered, o a vicinato).

**MLP (Multi-Layer Perceptron)**: topologia a strati, **feed-forward** (flusso in una sola direzione). Input=funzione identità; hidden=perceptron veri (sigmoide, uno o più livelli); output=combina i risultati hidden. Tipicamente **fully connected**. Codifica classi in output: **1 neurone** per 1-2 classi; per ≥3 classi, **codifica one-hot** (un neurone per classe, preferita alla codifica binaria compatta `⌈log2(classi)⌉` perché più robusta a piccoli errori e più interpretabile — ogni neurone ha un target 0/1 chiaro).

Con più hidden layer: gerarchia di astrazione (1° layer traccia confini/separazioni lineari, 2° combina confini in forme, 3° combina forme in forme complesse). **MLP a 3 livelli con sigmoide** = **approssimatore universale di funzioni** (con neuroni hidden a sufficienza). Conoscenza = **matrice dei pesi**.

**Backpropagation** (apprendimento supervisionato): per ogni istanza, **passata forward** (calcola output) + **passata backward** (propaga l'errore, aggiorna i pesi dai neuroni di output verso gli strati precedenti). Epoca = intero learning set elaborato.

**Discesa del gradiente**: `Δwji = -η·∂E/∂wji` (greedy, minimo non necessariamente globale). Errore globale `E = ½Σ(ti-yi)²` (p=neuroni output, t=target, y=output). Il **problema del credit assignment** (come distribuire l'errore agli hidden, dove non si conosce un target diretto) è risolto dalla backpropagation:
- Delta rule **output**: `Δwji=η·δj·xji`, `δj=yj(1-yj)(tj-yj)` (il termine yj(1-yj) deriva dalla derivata della sigmoide).
- Delta rule **hidden**: `Δwki=η·δk·xki`, `δk=yk(1-yk)·Σj∈Ik δj·wkj` — il δ di un hidden si ottiene propagando all'indietro (da cui "backpropagation") i δ dei neuroni successivi, pesati sulle rispettive connessioni.

**Regressione**: una rete neurale (non solo MLP) può approssimare una funzione continua `y=f(x)` non nota, non solo classificare (un neurone di output per ciascun valore prodotto, se a più valori). Errore valutato con **MSE** = `Σ(yo-yd)²/n` (non più matrice di confusione/accuratezza, dato che non ci sono classi discrete).
