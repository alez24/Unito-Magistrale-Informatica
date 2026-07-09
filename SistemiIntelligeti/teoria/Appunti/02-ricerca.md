# Modulo 2 — Risoluzione di problemi mediante ricerca (non informata e informata)

Questo modulo affronta il primo dei tre grandi approcci alla risoluzione automatica di problemi in IA:

1. **ricerca nello spazio degli stati** (oggetto di questo modulo),
2. ricerca in spazi con avversario (giochi ad informazione completa),
3. risoluzione di problemi mediante soddisfacimento di vincoli (CSP).

L'idea di fondo è che moltissimi problemi si possano modellare come un insieme di **stati** collegati da **azioni**, e che risolvere il problema equivalga a trovare un **percorso** (sequenza di azioni) che porti da uno stato iniziale a uno stato che soddisfa un obiettivo.

## Stati, azioni e astrazione

Alla base di tutto c'è l'idea di astrarre la realtà in un insieme discreto di **stati**, che transitano l'uno nell'altro tramite l'esecuzione di **azioni** (operazioni). Esempio minimale: stato `{dentro, fuori}`, azione `{attraversa_soglia}` — rappresentabile come un grafo di transizione di stato.

Caratteristiche tipiche di questa astrazione:

- **stati discreti**: anche se nel mondo fisico un fenomeno è continuo (es. il passaggio graduale attraverso una soglia), lo si discretizza in un numero finito di valori (idea analoga alla discretizzazione di una funzione continua in un istogramma);
- **effetto deterministico delle azioni** (nel caso base — esistono varianti non deterministiche, es. l'azione "passo" che dallo stato "dentro" può portare a due esiti diversi a seconda della posizione non rappresentata nella stanza, oppure azioni a valori continui come "passo(spinta)");
- **dominio statico**: il mondo non cambia se non per effetto delle azioni dell'agente.

Il principio guida dell'astrazione è **rappresentare solo l'informazione rilevante al problema**: per uno stato conta la posizione ma non il panorama; per un'azione conta l'esito raggiunto ma non, ad esempio, l'inquinamento prodotto.

### Obiettivi e ricerca

Un **obiettivo** è un risultato verso cui sono diretti gli sforzi, definito da:

1. una **situazione** (es. "essere in un luogo"),
2. eventualmente una **prestazione** associata (es. "...entro un certo tempo").

L'insieme di tutti gli stati che soddisfano la condizione obiettivo è detto **insieme degli stati obiettivo** (o stati *goal*/*target*).

Un algoritmo di ricerca determina una soluzione che, partendo dallo stato iniziale, raggiunge uno stato obiettivo, utilizzando:

1. una descrizione del problema;
2. un metodo di ricerca nello spazio degli stati.

***Una soluzione è un percorso nello spazio degli stati.***

## Definizione formale di problema di ricerca

Un problema di ricerca è definito formalmente come una **tupla di 4 elementi**:

| Elemento | Significato |
|---|---|
| **1. Stato iniziale** | cattura la situazione da cui si parte per calcolare la soluzione |
| **2. Funzione successore** (o funzione azioni + modello di transizione) | dato uno stato e un'azione legale in esso, calcola lo stato risultante dall'esecuzione di quell'azione |
| **3. Test obiettivo** | determina se uno stato è quello goal: verifica una proprietà o l'appartenenza all'insieme degli stati target |
| **4. Funzione di costo del cammino** | assegna un costo numerico a un percorso possibile |

L'insieme di tutti gli stati possibili (**spazio degli stati**) è spesso definito in modo implicito/generativo (tramite stato iniziale + funzione successore) piuttosto che enumerato esplicitamente.

### Esempio guida: problema di navigazione

- **Stato iniziale**: `in(Alessandria)`.
- **Funzione successore**: applicando l'azione `go(Ovada)` allo stato `in(Alessandria)` si ottiene lo stato `in(Ovada)` (transizione possibile solo se Ovada è raggiungibile direttamente da Alessandria).
- **Test obiettivo**: se la destinazione è Genova, verifica se lo stato corrisponde a `in(Genova)`.
- **Funzione di costo del cammino**: ad esempio il numero di km percorsi, oppure una misura più complessa che combina km e pedaggi.

### Esempio: il mondo dell'aspirapolvere

Due stanze (sinistra S, destra D), ciascuna sporca o pulita; un aspirapolvere che si trova in una delle due stanze e può muoversi o aspirare.

- Ogni stanza può assumere 4 configurazioni: `<pulita, vuota>`, `<pulita, con aspirapolvere>`, `<sporca, vuota>`, `<sporca, con aspirapolvere>`.
- **Azioni**: applicabili a tutti gli stati (muoviti a sinistra/destra, aspira).
- **Stato iniziale**: qualunque stato può esserlo (dipende da dove si trova l'aspirapolvere e dallo sporco presente).
- **Funzione successore**: restituisce lo stato prodotto applicando l'azione scelta allo stato corrente.
- **Test obiettivo**: entrambe le stanze pulite.
- **Costo del cammino**: ogni azione costa 1, quindi il costo è il numero di azioni eseguite.

### Esempio: il gioco dell'8 (8-puzzle)

- **Stato**: posizione di ciascuna delle 8 tessere numerate e dello spazio vuoto in una griglia 3x3. Esistono **181.440 = 9!/2** stati raggiungibili (metà delle 9! permutazioni, perché solo metà sono raggiungibili da una configurazione data — l'altra metà richiederebbe "sollevare" le tessere).
- **Stato iniziale**: qualunque configurazione può esserlo.
- **Funzione successore**: sposta nello spazio vuoto una delle tessere ad esso adiacenti.
- **Test obiettivo**: la disposizione dei numeri corrisponde alla configurazione obiettivo prefissata.
- **Costo del cammino**: ogni mossa costa 1; il costo del cammino è il numero di mosse.

### Toy problem vs Real-world problem

- **Toy problem**: problema artificiale, con formulazione precisa e univoca, usato per illustrare o confrontare metodi di risoluzione (8-puzzle, 8 regine, mondo dell'aspirapolvere, attraversamento del fiume...).
- **Real-world problem**: problema concreto (configurazione VLSI, itinerari stradali, navigazione robotica...), spesso privo di una formulazione unica e standard.

> ❓ **Domanda d'esame:** Formulare il problema delle 8 regine (stati, stato iniziale, funzione successore, test obiettivo, costo).
> **Risposta ragionata:** occorre posizionare 8 regine su una scacchiera 8x8 in modo che nessuna ne attacchi un'altra (stessa riga, colonna o diagonale vietate). Una formulazione efficiente (*incrementale*) è: **stati** = configurazioni con 0-8 regine sulla scacchiera, una per colonna, nessuna in conflitto; **stato iniziale** = scacchiera vuota; **funzione successore** = aggiungi una regina in una qualsiasi casella libera della colonna successiva che non sia attaccata dalle regine già posizionate; **test obiettivo** = 8 regine sulla scacchiera senza conflitti; **costo del cammino** = 1 per ogni regina piazzata (irrilevante, interessa solo raggiungere lo stato goal). Questa formulazione riduce enormemente lo spazio di ricerca rispetto a generare tutte le disposizioni di 8 regine su 64 caselle e poi filtrare.

## Spazio degli stati vs albero/grafo di ricerca

È fondamentale distinguere due livelli:

- **Spazio degli stati**: l'insieme (astratto, spesso implicito) di tutti gli stati raggiungibili e le transizioni fra essi, definito dal problema stesso (stato iniziale + funzione successore). Esiste indipendentemente dal fatto che venga esplorato.
- **Albero (o grafo) di ricerca**: struttura dati *costruita dall'algoritmo* durante l'esplorazione per trovare una soluzione. Ogni **nodo** dell'albero corrisponde a uno stato, ma un nodo contiene anche altra informazione (riferimento al nodo genitore, azione che lo ha generato, profondità, costo del cammino accumulato). I **nodi figli** sono generati applicando la funzione successore. L'albero diventa **grafo** quando lo stesso stato può essere raggiunto da più percorsi diversi (nodi diversi che corrispondono allo stesso stato, o — se si marcano gli stati visitati — un unico nodo con più genitori).

Formalmente, un grafo di ricerca è una coppia `G = ({ni}, {eij})`: un insieme di nodi e un insieme di archi, dove l'arco `eij` rappresenta che `nj` è successore di `ni`, con un costo `cij` associato. L'esistenza di `eij` non implica quella di `eji` (i grafi sono orientati); se esiste `eji` in generale `cji ≠ cij`. Attenzione: nella struttura dati, ogni nodo ha un puntatore al proprio **genitore** (arco figlio→genitore, opposto rispetto al verso di espansione).

Durante la ricerca ogni nodo si trova in uno di questi stati:

- **frontiera**: nodi generati ma non ancora espansi (detti anche nodi APERTI);
- **espanso/chiuso**: nodo di cui sono già stati generati tutti i successori;
- non ancora generato.

Il criterio con cui si sceglie **quale nodo della frontiera espandere per primo** è ciò che distingue le diverse strategie di ricerca.

## Criteri di valutazione delle strategie di ricerca

Per confrontare le strategie si usano quattro criteri:

1. **Completezza**: garanzia di trovare una soluzione, se esiste.
2. **Ottimalità**: garanzia di trovare la soluzione di costo minimo.
3. **Complessità temporale**: quanto tempo (= quanti nodi generati/espansi) serve per trovare una soluzione.
4. **Complessità spaziale**: quanta memoria (= quanti nodi mantenuti) serve.

Poiché gli algoritmi sono entità astratte (indipendenti dal calcolatore su cui girano), tempo e spazio si misurano in modo **parametrico**, non in secondi/byte: si conta il numero di nodi generati o visitati, usando la **notazione O-grande**. `T(n)` è `O(f(n))` se esiste `n₀` e una costante `c > 0` tali che per ogni `n > n₀` si abbia `T(n) ≤ c·f(n)`.

I parametri standard usati per gli algoritmi di ricerca sono:

- **b** = fattore di ramificazione (branching factor): numero massimo di figli di un nodo;
- **d** = profondità della soluzione più superficiale (meno costosa in numero di passi);
- **m** = profondità massima dello spazio degli stati (può essere infinita).

Gli algoritmi si dividono in:

- **approcci blind (non informati)**: usano solo la struttura del problema (stato iniziale, successori, test obiettivo);
- **approcci informati**: usano anche conoscenza aggiuntiva (euristiche) per guidare la ricerca — monoagente (questo modulo), multiagente/giochi, CSP (moduli successivi).

---

## Parte 1 — Ricerca non informata (blind search)

Lista delle strategie trattate: ricerca in ampiezza, ricerca a costo uniforme, ricerca in profondità (con variante a profondità limitata), iterative deepening, ricerca bidirezionale.

### 1. Ricerca in ampiezza (Breadth-First Search, BFS)

**Idea**: si espande prima il nodo radice, poi tutti i suoi successori (livello 1), poi tutti i discendenti di livello 2, e così via — si esplora un livello di profondità alla volta.

**Struttura dati**: la frontiera è gestita come una **coda FIFO** (First In First Out): i nodi generati per primi vengono espansi per primi.

**Nota sulla memoria**: tutti i nodi della frontiera *e tutti i loro antenati* devono restare in memoria, per poter ricostruire il percorso soluzione quando si trova il nodo obiettivo (grazie ai puntatori al genitore).

#### Valutazione BFS

- **Completezza**: sì, se il fattore di ramificazione b è finito e la soluzione si trova a profondità finita d.
- **Ottimalità**: sì, **solo se il costo del cammino è funzione monotona non decrescente della profondità** (in particolare se tutte le azioni hanno lo stesso costo — in tal caso ottimalità = trovare la soluzione con meno passi).
- **Complessità temporale**: `O(b^(d+1))`. Deriva dal fatto che nel caso peggiore si generano tutti i `b^i` nodi di ogni livello `i` fino al livello `d`, più i nodi di livello `d+1` necessari a verificare il test obiettivo sull'ultimo nodo del livello `d` (in totale `b^(d+1) - b` nodi al livello d+1 nel caso peggiore).
- **Complessità spaziale**: `O(b^(d+1))`, perché occorre mantenere in memoria tutta la frontiera e tutti gli antenati.

La complessità spaziale è il vero tallone d'Achille della BFS: con b=10, generando 10.000 nodi/sec e un nodo che occupa 1000 byte, a profondità 12 servirebbero circa **10 petabyte** di memoria e 35 anni di tempo — la memoria esaurisce le risorse ben prima del tempo.

### 2. Ricerca a costo uniforme (Uniform-Cost Search)

**Idea**: quando i costi dei passi non sono tutti uguali, non basta contare i livelli: occorre espandere sempre il nodo il cui **cammino dalla radice ha costo minimo**.

**Struttura dati**: la frontiera è una **coda con priorità** ordinata per costo del cammino accumulato `g(n)`. Ad ogni iterazione si espande il nodo di costo minimo.

Punti di attenzione:

- **costo ≠ numero di passi**: non conta quante azioni sono state eseguite, ma la somma dei loro costi;
- quando si genera per la prima volta un nodo obiettivo **l'algoritmo non si ferma subito**: prima verifica che non vi siano altri cammini aperti di costo ancora inferiore da espandere (perché quello trovato potrebbe non essere il più economico).
- quando tutti i costi sono uguali, la ricerca a costo uniforme **coincide** con la BFS.

#### Valutazione ricerca a costo uniforme

- **Completezza**: garantita solo se tutti i passi hanno **costo > 0** (costo minimo delle operazioni positivo, altrimenti si rischiano loop infiniti a costo zero che non fanno mai terminare la ricerca — es. un'azione "noOp" a costo 0).
- **Ottimalità**: garantita, sempre a patto che i costi siano tutti `> 0`. Il motivo è che i costi dei cammini aumentano monotonamente con l'aggiunta di passi e l'algoritmo espande sempre il cammino di costo minimo attualmente aperto: non può "saltare" per errore un percorso più economico non ancora scoperto.
- **Complessità** (temporale e spaziale): non dipende direttamente da b e d, ma dal **costo della soluzione ottima C\*** e dal costo minimo delle azioni ε: `O(b^(1+⌊C*/ε⌋))`. Intuitivamente, equivale al branching factor elevato al numero di passi necessari a raggiungere il costo C* se tutti i passi costassero ε. Quando i costi sono tutti uguali, ricade nel caso della BFS.

### 3. Ricerca in profondità (Depth-First Search, DFS) senza backtracking

**Idea**: si espande sempre uno dei nodi **più profondi** (più lontani dalla radice) della frontiera. L'espansione genera **tutti** i successori di un nodo. Quando si cerca di espandere un nodo privo di successori, il nodo viene scartato e si torna indietro (backtrack) per esplorare altre alternative rimaste in frontiera.

**Struttura dati**: la frontiera è gestita come una **coda LIFO** (Last In First Out), cioè uno **stack**.

#### Valutazione DFS

- **Completezza**: garantita solo se **tutti i cammini sono finiti** (altrimenti la ricerca può incamminarsi lungo un ramo infinito senza mai tornare indietro a esplorare la soluzione).
- **Ottimalità**: **non garantita in generale**, anche a parità di costo dei passi: la DFS può restituire una soluzione più lunga/costosa semplicemente perché l'ha incontrata per prima esplorando in profondità un ramo "sbagliato", mentre una soluzione più corta si trovava in un altro ramo della frontiera non ancora visitato.
- **Complessità temporale**: `O(b^m)` nel caso peggiore (m = profondità massima dell'albero), perché nel caso peggiore si visitano tutti i nodi dell'albero.
- **Complessità spaziale**:
  - versione che genera **tutti** i successori di un nodo espanso: `O(b·m)` — occorre mantenere il cammino corrente più tutti i "fratelli" generati lungo il percorso (`b·m + 1` nodi nel caso peggiore);
  - variante **con backtracking classico**, in cui si genera un solo successore alla volta (si torna al genitore per generarne un altro solo se il ramo corrente fallisce): la complessità spaziale scende a **`O(m)`**.

Il vantaggio della DFS rispetto alla BFS è enormemente in termini di spazio: con lo stesso esempio (b=10, d=12) la DFS richiederebbe solo ~118 KB contro i 10 petabyte della BFS.

#### Variante: ricerca a profondità limitata

Per evitare che la DFS si perda in cammini infiniti (o semplicemente troppo lunghi) che non portano alla soluzione, si introduce un **limite artificiale l**: un nodo viene espanso solo se la sua profondità `p ≤ l`; oltre quel limite viene trattato come se non avesse successori (si taglia il ramo).

- Tutti i cammini esplorati avranno lunghezza al più `l`.
- **Problema 1**: si perde completezza se la profondità reale dell'obiettivo d supera l (l'obiettivo non verrà mai trovato).
- **Problema 2**: se invece `l > d`, si perde efficienza esplorando inutilmente rami oltre la profondità della soluzione.

Il problema pratico è che **d non è quasi mai noto a priori**, quindi scegliere un buon valore di l è difficile — da qui l'idea dell'iterative deepening.

### 4. Iterative Deepening Depth-First Search (IDDFS)

**Idea**: esegue ripetutamente una ricerca a **profondità limitata**, aumentando progressivamente il limite l (0, 1, 2, 3, ...) fino a trovare la soluzione. Ad ogni iterazione l'albero di ricerca viene **ricostruito da zero**. Se una ricerca fallisce per raggiungimento del limite, si dice che è avvenuto un "taglio".

In pratica è come esplorare in sequenza tanti alberi diversi (con l = 0, poi l = 1, poi l = 2, ...), ciascuno tramite una normale DFS a profondità limitata.

#### Perché non è così costoso ripartire da zero?

Sembra controintuitivo che ricostruire l'albero ad ogni iterazione sia efficiente, ma la maggior parte dei nodi si trova **vicino alla frontiera** (ai livelli più profondi), quindi i nodi vicini alla radice vengono rigenerati più volte ma sono relativamente pochi rispetto a quelli generati una sola volta al livello più profondo.

Il numero totale di nodi generati dall'iterative deepening è:

```
Nid = d·b + (d-1)·b² + ... + (d-i)·b^(i+1) + ... + 1·b^d  =  Σ_{i=1}^{d} (d-i)·b^i
```

che risulta **minore** del numero di nodi generati dalla BFS nel caso peggiore:

```
Namp = b + b² + ... + b^i + ... + b^d + (b^(d+1) - b)
```

perché la BFS, a differenza dell'IDDFS, genera anche (quasi tutti) i nodi del livello `d+1`.

**Esempio numerico** (b=10, d=5): `Nid ≈ 123.456` nodi contro `Namp ≈ 1.111.100` nodi — la BFS genera quasi 9 volte più nodi, principalmente a causa del costoso livello d+1.

#### Valutazione IDDFS

Combina i pregi di BFS e DFS:

- **Completezza**: sì, se b è finito (come la BFS).
- **Ottimalità**: sì, se il costo è funzione non decrescente della profondità (come la BFS).
- **Complessità spaziale**: **O(b·d)**, modesta come la DFS.
- **Complessità temporale**: **O(b^d)**, simile (nell'ordine di grandezza) alla BFS.

È la strategia ***preferita quando lo spazio di ricerca è ampio e la profondità della soluzione non è nota a priori*** — combina la garanzia di trovare la soluzione più superficiale (come BFS) con requisiti di memoria contenuti (come DFS).

### 5. Ricerca bidirezionale

**Idea**: eseguire simultaneamente **due ricerche**: una **forward** dallo stato iniziale, una **backward** dallo stato obiettivo. La ricerca termina quando le due frontiere si intersecano (un nodo compare in entrambe).

Per determinare la ricerca all'indietro occorre saper calcolare i **predecessori** di uno stato — operazione non sempre semplice o efficiente quanto calcolare i successori. Se gli operatori hanno forma `IF antecedente THEN conseguente`, la ricerca forward verifica quali antecedenti sono soddisfatti dallo stato corrente, mentre la ricerca backward verifica quali conseguenti sono soddisfatti (usando la conoscenza degli antecedenti per risalire ai possibili predecessori).

Problema aggiuntivo: se lo stato obiettivo non è unico, da dove far partire la ricerca backward? Soluzione: introdurre uno **stato "di comodo"** raggiungibile in un passo da tutti gli stati obiettivo reali, e farla partire da lì.

Le due ricerche possono procedere:

- **a fronte d'onda** (esplorando tutte le operazioni possibili, quando non c'è conoscenza aggiuntiva), oppure
- **a cono** (esplorando solo una parte delle operazioni, se si dispone di conoscenza aggiuntiva/euristica) — in questo secondo caso è importante che i due coni si incontrino "a metà strada", altrimenti si rischia di raddoppiare il lavoro.

#### Valutazione ricerca bidirezionale

- **Complessità temporale e spaziale**: `O(b^(d/2))` (più precisamente `2·O(b^(d/2))`), un netto vantaggio rispetto a `O(b^d)`: esempio con b=2, d=6, si passa da `b^d = 64` a `b^(d/2) = 8`.
- **Completezza**: garantita se b è finito e si usa la BFS in entrambe le direzioni.
- **Ottimalità**: garantita se i costi dei passi sono identici e si usa la BFS in entrambe le direzioni.

### Grafi di ricerca e nodi già esplorati

In molti problemi lo stesso stato è raggiungibile tramite percorsi diversi: questo causa **ripetizione di lavoro** (si riespande più volte la stessa porzione di spazio degli stati). Marcare i nodi già visitati e controllare, prima di espandere un nodo, se lo stato corrispondente è già stato visitato, rende la ricerca molto più efficiente (si passa da una visita ad albero a una visita a grafo).

#### Esempi classici di problemi di attraversamento

- **Capra (pecora), cavolo e lupo**: un uomo deve traghettare pecora, cavolo e lupo con una barca che ne trasporta uno alla volta, senza mai lasciare incustodite sulla stessa riva pecora+cavolo o lupo+pecora. Stati rappresentati con variabili `<U,C,P,L>` a valori `a`/`b` (le due rive); stato iniziale `<a,a,a,a>`, stato goal `<b,b,b,b>`.
- **Missionari e cannibali**: 3 missionari e 3 cannibali devono attraversare un fiume con una barca da 1-2 posti, senza che in nessuna riva i cannibali siano mai in maggioranza rispetto ai missionari. Rappresentazioni possibili: `<Ma,Ca,Mb,Cb,B>` oppure più compattamente `<Ma,Ba,B>`.
- **Torre di Hanoi**: spostare una torre di dischi dal primo al terzo piolo (usando il secondo come appoggio), potendo sovrapporre solo dischi più piccoli su dischi più grandi.

Questi problemi sono tipici esercizi per esercitarsi nella formulazione formale (stato iniziale, azioni, test obiettivo) e nel disegno esplicito dello spazio degli stati/albero di ricerca.

### Tabella riassuntiva — confronto strategie di ricerca non informata

| Strategia | Struttura dati frontiera | Completezza | Ottimalità | Complessità temporale | Complessità spaziale |
|---|---|---|---|---|---|
| **Ampiezza (BFS)** | coda FIFO | Sì (se b finito) | Sì, se costo non decrescente con la profondità (es. costi uniformi) | O(b^(d+1)) | O(b^(d+1)) |
| **Costo uniforme** | coda a priorità (su g(n)) | Sì (se costi passi > 0) | Sì (se costi passi > 0) | O(b^(1+⌊C*/ε⌋)) | O(b^(1+⌊C*/ε⌋)) |
| **Profondità (DFS)** | coda LIFO / stack | No, solo se cammini finiti | No | O(b^m) | O(b·m) [O(m) con backtracking] |
| **Profondità limitata** | stack, con limite l | No, solo se l ≥ d | No | O(b^l) | O(b·l) |
| **Iterative deepening (IDDFS)** | stack ricostruito ad ogni iterazione | Sì (se b finito) | Sì, se costo non decrescente con la profondità | O(b^d) | O(b·d) |
| **Bidirezionale** | due frontiere (FIFO se BFS in entrambi i sensi) | Sì (se b finito, BFS in entrambe le direzioni) | Sì (se costi uniformi, BFS in entrambe le direzioni) | O(b^(d/2)) | O(b^(d/2)) |

*(b = fattore di ramificazione; d = profondità della soluzione più superficiale; m = profondità massima dello spazio degli stati; l = limite di profondità; C\* = costo della soluzione ottima; ε = costo minimo di un'azione)*

---

## Parte 2 — Ricerca informata (heuristic search)

### Perché serve conoscenza aggiuntiva

> ❓ **Domanda d'esame:** Le strategie di ricerca blind non sono efficienti. È possibile rendere la ricerca più efficiente utilizzando conoscenza sul problema? La conoscenza permette di focalizzare la ricerca verso le direzioni più promettenti?
> **Risposta ragionata:** sì. Le strategie non informate esplorano lo spazio degli stati "alla cieca", basandosi solo sulla struttura del problema (chi sono i successori, qual è il costo dei passi). Se disponiamo di conoscenza aggiuntiva sul problema — tipicamente una **stima** di quanto uno stato sia vicino all'obiettivo — possiamo usarla per **ordinare la frontiera** e dare priorità agli stati più promettenti, riducendo drasticamente il numero di nodi generati/espansi rispetto a BFS, DFS o costo uniforme. Questa stima si chiama **funzione euristica** h(n). Esempio classico: nell'8-puzzle si può usare il numero di tessere fuori posto come euristica.

### Funzioni di valutazione e best-first search

Una strategia di ricerca informata ordina la frontiera in base a una **funzione di valutazione f(n)** applicata a ciascun nodo. A seconda di come si definisce f(n) si ottengono strategie diverse; questa famiglia di strategie è detta **best-first search**, perché espande per primo il nodo ritenuto "più promettente" secondo f. Vi appartengono la ricerca greedy, A* e RBFS.

Spesso `f(n)` include una componente `h(n)`, detta **euristica**, che stima il costo minimo del cammino residuo dallo stato corrispondente a `n` fino a uno stato obiettivo.

### 1. Ricerca greedy (avida)

`f(n) = h(n)`: si sceglie sempre il nodo che l'euristica stima più vicino all'obiettivo, ignorando completamente il costo già speso per arrivarci.

**Esempio**: se gli stati sono località di cui si conoscono le coordinate, si può usare la distanza in linea d'aria verso l'obiettivo come stima della "vicinanza" reale (su strada).

**Problemi della ricerca greedy**:

- L'euristica può ingannare: la distanza in linea d'aria non riflette necessariamente la distanza reale su strada. Esempio: se in linea d'aria `dist(B,G) < dist(C,G)` ma su strada `dist(B,G) > dist(C,G)`, la greedy sceglie B illudendosi che sia il ramo migliore, quando in realtà C conduce prima all'obiettivo.
- Rischio di **vicoli ciechi** e loop: la greedy eredita i difetti della DFS, perché segue "avidamente" la direzione che sembra più promettente senza tener conto del cammino già percorso, rischiando di doversi lunghi tratti all'indietro se imbocca una strada senza uscita (es. Balme→Noasca: 18 km in linea d'aria ma 91 km su strada reale, con un vicolo cieco che costringe a tornare indietro).
- **Non è né completa né ottima** in generale (proprio come la DFS, di cui condivide la logica di avanzamento "in profondità" verso il nodo apparentemente migliore).

### 2. A* (A-star)

**Idea**: combinare i punti di forza della ricerca a costo uniforme e della ricerca greedy:

- il **costo uniforme** guarda al **passato**: espande per primi i nodi il cui cammino dalla radice costa meno;
- la **greedy** guarda al **futuro**: espande per primi i nodi che promettono di raggiungere l'obiettivo al costo minore.

`f(n) = g(n) + h(n)`, dove:

- `g(n)` = costo minimo (fra tutti i cammini finora visti) per raggiungere il nodo n dallo stato iniziale (guarda indietro, è un valore esatto sui cammini già esplorati);
- `h(n)` = stima del costo minimo del proseguimento del cammino da n a un obiettivo (guarda avanti, è una stima);
- `f(n)` = stima del costo minimo totale di un cammino risolutivo che passa per n.

Confronto con i valori "veri" (ideali, calcolabili solo con conoscenza totale, non disponibili all'algoritmo):

- `g*(n)` = costo minimo reale per raggiungere n da s;
- `h*(n)` = costo minimo reale del proseguimento da n a un obiettivo;
- `f*(n) = g*(n) + h*(n) = C*` per i nodi sul cammino ottimo.

#### Nozione di obiettivo preferito

A* lavora su grafi con un insieme T di nodi obiettivo. Per un nodo n, un obiettivo `t ∈ T` è detto **preferito** se il costo del cammino ottimo `h(n,t)` è minore o uguale al costo per raggiungere qualunque altro nodo di T da n. Si pone `h(n) = min_{t∈T} h(n,t)`: cioè h(n) rappresenta il costo per raggiungere l'obiettivo più economico da n.

#### Pseudocodice di A*

```
Sia s il nodo iniziale, T l'insieme dei nodi obiettivo (target)
segna s come APERTO e calcola f(s)
ripeti:
    seleziona il nodo APERTO n con f(n) minima
        (i pari merito si risolvono a vantaggio di eventuali n ∈ T)
    se n ∈ T:
        marca n CHIUSO e termina (soluzione trovata)
    altrimenti:
        marca n CHIUSO
        applica la funzione successore a n:
            calcola f per tutti i successori n'
            marca APERTI i successori n' non ancora CHIUSI
            per i successori n' già CHIUSI ma raggiunti ora con un f
              più basso di quello calcolato in precedenza (cammino
              migliore trovato), rimarcali come APERTI
```

**Struttura dati**: coda a priorità ordinata su `f(n) = g(n) + h(n)` (generalizza la coda a priorità della ricerca a costo uniforme, ma con priorità che include anche la stima euristica).

#### Euristiche ammissibili

Una funzione euristica h è **ammissibile** se, per ogni nodo n, `h(n) ≤ h*(n)`, dove h*(n) è il costo minimo reale per raggiungere un nodo obiettivo da n. Intuitivamente: ***un'euristica ammissibile non sovrastima mai*** — è sempre ottimistica (o al più esatta). Esempio: la distanza in linea d'aria è ammissibile rispetto alla distanza reale su strada, perché la linea retta è sempre il cammino più corto possibile fra due punti.

#### Ottimalità di A*

**Teorema**: se (1) l'euristica h è ammissibile e (2) tutti i passi hanno costo maggiore di una costante positiva piccola a piacere (ε > 0), allora ***A* termina e trova sempre una soluzione ottima***: A* è completo e ottimo.

##### Dimostrazione (caso albero di ricerca)

In un albero ogni nodo ha un solo cammino dalla radice (nessuna molteplicità di percorsi). Supponiamo per assurdo che A* scelga un obiettivo subottimo G2 al posto di un nodo n che si trova su un cammino ottimo verso il vero obiettivo G, con `f*(G) = g*(G) + h*(G) = C*` (costo della soluzione ottima).

1. **G2 è un nodo obiettivo**, quindi `h(G2) = 0` per definizione di h (l'euristica al goal vale 0, essendo la distanza residua nulla).
2. Quindi `f(G2) = g(G2) + h(G2) = g(G2)`.
3. Poiché G2 è per ipotesi subottimo, `f(G2) = g(G2) > C*`.
4. Sia n un nodo qualunque sul cammino ottimo: in un albero, `g*(n) = g(n)` (unico percorso possibile fino a n, quindi il costo osservato coincide col costo reale minimo).
5. Poiché h è ammissibile, `h(n) ≤ h*(n)`.
6. Quindi `f(n) = g(n) + h(n) ≤ g*(n) + h*(n) = f*(n) = C*`.
7. Combinando (3) e (6): `f(n) ≤ C* < f(G2)`.
8. Ma A* sceglie sempre il nodo APERTO con f minima: **fra n e G2, A* sceglierà sempre n**, mai G2 — contraddizione con l'assunzione iniziale. Quindi A* non può fermarsi su un obiettivo subottimo se esiste ancora un nodo n aperto su un cammino ottimo. ∎

##### Caso grafo di ricerca: serve la consistenza (monotonicità)

Nei grafi esiste **molteplicità di cammini**: il primo cammino trovato verso uno stato non è necessariamente quello di costo minimo (per questo, nell'esempio della Romania, A* non si ferma la prima volta che incontra Bucharest come nodo generato, ma solo quando lo estrae come nodo da espandere con f minima). Questo invalida la dimostrazione precedente, che sfruttava l'unicità del cammino nell'albero.

Per i grafi occorre l'ipotesi più forte di ***euristica consistente (o monotona)***: per ogni nodo n e ogni suo successore n' generato tramite un'azione a,

```
h(n) ≤ c(n, a, n') + h(n')
```

Questa è una **disuguaglianza triangolare**: la stima diretta da n al goal non può superare il costo di un passo verso n' più la stima residua da n'.

**Dimostrazione che con h consistente i valori f(n) sono non decrescenti lungo un cammino**:

1. Per definizione, `g(n') = g(n) + c(n,a,n')`.
2. Per definizione, `f(n') = g(n') + h(n')`.
3. Sostituendo: `f(n') = g(n) + c(n,a,n') + h(n')`.
4. Per la disuguaglianza triangolare, `c(n,a,n') + h(n') ≥ h(n)`, quindi `f(n') ≥ g(n) + h(n) = f(n)`.
5. Dunque `f(n') ≥ f(n)`. ∎

Poiché A* espande i nodi in ordine non decrescente di f, se uno stato già CHIUSO viene re-incontrato lungo un altro cammino, il nuovo valore f sarà maggiore o uguale a quello con cui è stato chiuso la prima volta; di conseguenza **il primo incontro con un nodo obiettivo durante l'espansione (non la sola generazione) corrisponde già alla soluzione ottima**.

#### Monotonicità vs ammissibilità

La monotonicità (consistenza) è una proprietà **più forte** dell'ammissibilità: si dimostra che ogni euristica monotona è anche ammissibile, ma non vale il viceversa in generale (anche se in pratica capita spesso). Graficamente: l'insieme delle euristiche monotone è un sottoinsieme di quello delle euristiche ammissibili.

La distanza in linea d'aria nel problema della Romania è sia ammissibile sia monotona: per ogni città `luogo` e un suo successore diretto `luogo1`, vale `h(luogo) < c(luogo, vai, luogo1) + h(luogo1)` — la distanza in linea d'aria da luogo a Bucharest è sempre minore della distanza su strada fino a luogo1 sommata alla distanza in linea d'aria residua.

#### Ammissibile non vuol dire informativo

`h(n) = 0` è banalmente sempre ammissibile (non sovrastima mai, essendo il minimo possibile), ma è totalmente **priva di informazione utile**: degrada A* a una ricerca "cieca" basata solo su g(n). In particolare, se in aggiunta tutti i passi hanno costo uniforme pari a 1, **A* con h=0 diventa equivalente alla ricerca in ampiezza**.

#### Ottimalità in senso forte di A*

A* è **ottimamente efficiente** per qualunque euristica data: non esiste alcun altro algoritmo ottimo (che usi la stessa euristica ed espanda nodi in modo coerente con essa) in grado di garantire l'espansione di un numero di nodi inferiore a quello espanso da A*. Il difetto pratico è che il numero di nodi espansi cresce **esponenzialmente** con la profondità della soluzione ottima, e A* mantiene in memoria **tutti** i nodi generati (comportandosi, sotto questo aspetto, come una ricerca in ampiezza): questo lo rende spesso impraticabile per problemi di grandi dimensioni per limiti di memoria prima ancora che di tempo.

### Ridurre i requisiti di memoria: IDA* e RBFS

- **IDA\*** (Iterative Deepening A*): unisce l'idea di A* con quella dell'iterative deepening, usando come limite di taglio ad ogni iterazione non la profondità ma il valore di f(n) (non approfondito nel dettaglio nelle slide del corso).

- **RBFS** (Recursive Best-First Search): funziona come una DFS ricorsiva, ma mantiene un **upper bound dinamico** che rappresenta la stima di costo della migliore alternativa attualmente nota, permettendo di abbandonare un ramo non appena esso smette di essere il più promettente, invece di proseguire indefinitamente lungo lo stesso cammino.

#### RBFS in dettaglio (Korf, 1993)

Ogni chiamata ricorsiva ha tre argomenti: un nodo N, un valore F(N) e un upper bound B.

- `f(n)`: la funzione di valutazione statica (f(n) = g(n)+h(n) come in A*, non cambia nel tempo).
- `F(n)`: valore **dinamico** associato al nodo, che dipende dai discendenti: `F(N) = f(N)` se N è esplorato per la prima volta, altrimenti `F(N) = min(F(figli di N))` — cioè F "eredita" la miglior stima trovata nel sottoalbero.
- `B`: upper bound, calcolato in base ai valori F dei nodi fratelli — memorizza il costo stimato della **migliore alternativa** rispetto al ramo attualmente in esplorazione (in pratica il secondo migliore fra i fratelli).

Chiamata iniziale: `RBFS(radice_r, f(r), ∞)`.

```
RBFS(N, F(N), B):
    se f(N) > B: ritorna f(N)                    // upper bound superato, cambia percorso
    se N è un goal: termina con successo
    se N non ha figli: ritorna infinito           // vicolo cieco, cambia percorso
    per ogni figlio Ni di N:                      // inizializza F dei successori
        se f(N) < F(N): F[i] := max(F(N), f(Ni))
        altrimenti:     F[i] := f(Ni)
    ordina i figli Ni per F[i] crescente           // F[1] = figlio più promettente
    se un solo figlio: F[2] := infinito
    finché (F[1] ≤ B e F[1] < infinito):           // scendo solo se rispetto l'upper bound
        F[1] := RBFS(N1, F[1], min(B, F[2]))
        reinserisci N1 e F[1] in ordine
    ritorna F[1]
```

**Intuizione**: RBFS lavora come A* finché il ramo che sta costruendo rimane il migliore possibile secondo l'upper bound corrente. Non appena la stima di quel ramo peggiora oltre B, la ricerca lungo quel cammino viene **sospesa e "dimenticata"** (i nodi vengono cancellati dalla memoria), mantenendo solo, sul nodo radice del ramo abbandonato, il valore F aggiornato che riassume quanto costava proseguire di là. Se in seguito quel ramo torna ad essere il più conveniente, viene ri-esplorato da capo (con conseguente **ripetizione di lavoro**, difetto tipico di RBFS).

#### Valutazione RBFS

- **Ottimalità**: sì, se l'euristica è ammissibile.
- **Complessità spaziale**: **lineare, O(b·d)** — enorme vantaggio su A*, perché mantiene in memoria solo i nodi del cammino corrente e i loro fratelli diretti (esattamente come la DFS/IDDFS), non tutti i nodi generati.
- **Complessità temporale**: difficile da definire in generale, perché dipende fortemente dall'accuratezza dell'euristica usata.
- **Difetti**: non tiene traccia dei cammini ripetuti (non riconosce se uno stato è già stato visitato per un'altra via) e, essendo vincolata a un consumo di memoria O(b·d), **non riesce a sfruttare memoria aggiuntiva disponibile** per migliorare l'efficienza, a differenza di A* che potrebbe beneficiarne mantenendo più informazione.

### Funzioni euristiche: il caso di studio dell'8-puzzle

L'8-puzzle è uno dei primi problemi su cui si è sperimentata la ricerca informata. Generando casualmente lo stato iniziale, in media servono **22 mosse** per risolverlo, con un **branching factor medio pari a 3** (dipende dalla posizione della casella vuota: 4 mosse possibili se è al centro, 2 se è in un angolo, 3 se è sul bordo).

- L'**albero esaustivo** di ricerca conterrebbe circa `3^22` nodi, oltre 30 miliardi di nodi.
- Il **grafo esaustivo** (evitando i duplicati, cioè non riesplorando stati già visitati) contiene "solo" circa **180.000 stati** (coerente con i 181.440 = 9!/2 calcolati nella definizione formale del problema).
- Passando al **15-puzzle** (griglia 4x4), lo spazio esplode fino a circa **10^13 stati**: la crescita è drammatica nonostante il problema sembri solo "un po' più grande".

#### Due euristiche ammissibili classiche

- **h1 = numero di tessere fuori posto.** È ammissibile perché ogni tessera fuori posto dovrà essere spostata almeno una volta per arrivare alla configurazione obiettivo, quindi h1 non può mai sovrastimare il numero di mosse residue.
- **h2 = distanza di Manhattan (block distance).** Somma, su tutte le tessere, della distanza fra la posizione corrente e quella desiderata, contata come numero di celle attraversate in orizzontale più numero di celle attraversate in verticale. È ammissibile perché ogni mossa può avvicinare una tessera al proprio posto di **al più una posizione** per volta.

**Esempio di calcolo**: per un dato stato s, se tutte le 8 tessere sono fuori posto, `h1(s) = 8`. Sommando le distanze di Manhattan individuali di ciascuna tessera (es. 3+1+2+...) si può ottenere ad esempio `h2(s) = 18`.

#### Confronto sperimentale fra euristiche

Per stabilire quale euristica sia "migliore" non basta guardare un singolo caso: istanze diverse dello stesso problema (stati iniziali/goal diversi), anche a parità di profondità della soluzione d, generano numeri di nodi espansi differenti. Il metodo corretto è **sperimentale**:

1. generare un numero significativo di istanze del problema;
2. applicare lo stesso algoritmo di ricerca (tipicamente A*) a ogni istanza, una volta per ciascuna euristica da confrontare;
3. raccogliere i dati (nodi generati, profondità della soluzione, ecc.);
4. calcolare le medie sui casi omogenei (es. stessa profondità di soluzione);
5. confrontare le prestazioni medie.

#### Effective branching factor (fattore di ramificazione effettivo) b*

È la misura standard per quantificare la "qualità" di un'euristica a posteriori. Dato un problema risolto con A*, siano:

- **N** = numero di nodi generati a partire dal nodo iniziale;
- **d** = profondità della soluzione trovata.

**b\*** è definito come il branching factor che avrebbe un **albero uniforme di profondità d** che contenga esattamente `N+1` nodi:

```
N + 1 = 1 + b* + (b*)² + ... + (b*)^d
```

da cui si ricava (approssimativamente, per b* grande) `N ≈ (b*)^d`, cioè `b* ≈ ᵈ√N`.

**Interpretazione**: quanto più `b*` è vicino a 1, tanto migliore (più informativa) è l'euristica, perché significa che A* con quell'euristica si comporta quasi come se seguisse un unico cammino diretto verso l'obiettivo, con pochissima esplorazione "sprecata" su rami alternativi. Poiché per una data euristica i valori di b* misurati su istanze diverse tendono ad essere **abbastanza consistenti fra loro**, bastano poche misure su un piccolo campione di problemi per stimare affidabilmente la qualità di un'euristica.

**Esperimento citato**: 1200 problemi del 15-puzzle generati casualmente, con profondità di soluzione fra 2 e 24, risolti sia con iterative deepening sia con A* usando prima h1 poi h2; per ciascuna profondità sono stati calcolati nodi generati e b* medi. Il risultato tipico (coerente con la teoria sotto) è che **h2 (Manhattan) produce sistematicamente meno nodi e un b* più basso di h1** (tessere fuori posto), risultando quindi euristica migliore.

#### Valutazione teorica: euristiche dominanti

Oltre alla valutazione sperimentale, esiste un criterio **a priori**: siano h1 e h2 due euristiche **ammissibili** tali che per ogni nodo n, `h2(n) ≥ h1(n)` (h2 "approssima meglio" h* di quanto non faccia h1). Si dice che **h2 domina h1** (o che h2 è più informata di h1).

**Perché la dominanza implica efficienza**: si dimostra (teorema, non dimostrato nelle slide) che A* espande tutti e soli i nodi con `f(n) < C*` (C* = costo della soluzione ottima, costante che non dipende dall'euristica usata ma solo dal costo reale delle azioni). Poiché `f(n) = g(n) + h(n)`, ciò equivale a dire che vengono espansi tutti i nodi con `h(n) < C* - g(n)`. Se `h2(n) ≥ h1(n)` per ogni n, allora l'insieme dei nodi che soddisfano la condizione con h1 è un **soprainsieme** di quello con h2: usando h1, A* espanderà sicuramente **almeno tutti** i nodi che espande usando h2 (e in genere di più). Di qui: ***un'euristica più informata (dominante) porta A* a espandere un numero di nodi minore o uguale***, quindi è preferibile.

Nel caso dell'8/15-puzzle, sia h1 sia h2 sono ammissibili e per costruzione `h2(n) ≥ h1(n)` per ogni n (la distanza di Manhattan somma "quante celle" deve percorrere ciascuna tessera fuori posto, quindi è sempre almeno pari al numero di tessere fuori posto): questo conferma teoricamente perché h2 è preferibile a h1.

#### Costruzione sistematica di euristiche ammissibili: problemi rilassati

Un **problema rilassato** si ottiene rimuovendo (parte del)i vincoli del problema originale. Il grafo degli stati del problema rilassato è un **supergrafo** di quello originario (meno vincoli ⇒ più transizioni permesse ⇒ più archi). Poiché il supergrafo contiene comunque tutte le soluzioni ottime del problema originale (oltre ad altre in più), **il costo della soluzione ottima nel problema rilassato è un'euristica ammissibile per il problema originale** — non può mai costare di più risolvere una versione del problema con meno vincoli.

**Esempio — 8-puzzle**: il vincolo originale è "una tessera può spostarsi da A a B se (1) A e B sono adiacenti e (2) B è vuota". Tre possibili rilassamenti (rimozione di uno o più vincoli):

1. **Rimuovi solo il vincolo (2)**: una tessera può muoversi da A a B se A e B sono adiacenti (anche se B è occupata, "scambiando" le tessere) — la soluzione ottima di questo problema rilassato dà origine a un'euristica ammissibile, vicina a **h2 (distanza di Manhattan)**.
2. **Rimuovi solo il vincolo (1)**: una tessera può muoversi ovunque, purché la destinazione B sia vuota (non serve adiacenza).
3. **Rimuovi entrambi i vincoli**: una tessera può spostarsi ovunque, sempre — questo dà origine a **h1 (tessere fuori posto)**, perché nel problema completamente rilassato basta un solo movimento per ogni tessera fuori posto.

Il programma **Absolver II** (Prieditis, 1993) è un esempio storico di sistema in grado di generare automaticamente euristiche ammissibili per astrazione (rilassamento sistematico dei vincoli): ha scoperto la prima euristica ammissibile nota per il Cubo di Rubik e un'euristica per l'8-puzzle migliore di quelle proposte in precedenza. La ricerca su generazione automatica di euristiche continua tuttora, soprattutto nell'ambito del *planning* (costruzione automatica di piani).

#### Combinare euristiche non comparabili

Se si dispone di più euristiche ammissibili `h1, ..., hk` nessuna delle quali domina le altre (per alcuni nodi è migliore l'una, per altri nodi è migliore un'altra), si può costruire un'euristica composta:

```
h(n) = max{h1(n), h2(n), ..., hk(n)}
```

Questa euristica composta è **ammissibile** (perché lo sono tutte le componenti: prendere il massimo fra valori tutti ≤ h* dà ancora un valore ≤ h*) ed è **dominante per costruzione** su ciascuna delle euristiche che la compongono, perché per ogni nodo restituisce sempre la stima più accurata (più alta, quindi più vicina a h*) fra quelle disponibili.

#### Alternativa: apprendere le euristiche induttivamente

Un approccio alternativo alla progettazione manuale è usare tecniche di **apprendimento automatico**: si arricchisce ogni stato con un insieme di *feature* (es. numero di celle fuori posto, numero di vicini errati...), si generano casualmente molti problemi, li si risolve raccogliendo i dati (stato, feature, costo reale per raggiungere la soluzione), e si applica un metodo di apprendimento induttivo per estrarre automaticamente una funzione euristica dai dati raccolti.

---

## Riepilogo e punti chiave

- Un **problema di ricerca** è formalizzato da 4 elementi: **stato iniziale, funzione successore (azioni + modello di transizione), test obiettivo, funzione di costo del cammino**. Lo **spazio degli stati** (l'insieme astratto di stati/transizioni definito dal problema) va tenuto concettualmente distinto dall'**albero/grafo di ricerca** (la struttura dati che l'algoritmo costruisce esplorando quello spazio, dove ogni nodo aggiunge informazione di struttura — genitore, costo accumulato — allo stato che rappresenta).
- Le strategie **non informate** usano solo la struttura del problema e si distinguono essenzialmente per **come gestiscono la frontiera**: FIFO (ampiezza), coda a priorità su g(n) (costo uniforme), LIFO/stack (profondità), stack con limite (profondità limitata), stack ricostruito iterativamente (iterative deepening), doppia frontiera (bidirezionale).
- Nessuna strategia non informata è "sempre migliore delle altre": BFS e costo uniforme sono complete/ottime ma costano tantissima memoria (O(b^(d+1))); DFS è economica in spazio ma non completa né ottima in generale; **iterative deepening è generalmente la scelta di compromesso migliore** quando d non è nota, unendo completezza/ottimalità di BFS a un costo spaziale O(b·d) come la DFS.
- Le strategie **informate** sfruttano una funzione euristica h(n), stima del costo residuo per raggiungere l'obiettivo. La **ricerca greedy** (f=h) è veloce ma non completa né ottima, perché ignora il costo già speso (eredita i difetti della DFS). **A\*** (f = g+h) combina il "guardare indietro" del costo uniforme con il "guardare avanti" della greedy.
- **A\* con euristica ammissibile (h ≤ h\*) è ottimo su alberi di ricerca**; sui **grafi** serve la proprietà più forte di **consistenza/monotonicità** (`h(n) ≤ c(n,a,n') + h(n')`), che garantisce f non decrescente lungo ogni cammino e quindi che il primo nodo obiettivo espanso sia già quello ottimo. Ogni euristica monotona è ammissibile, ma non vale il viceversa in generale.
- A* è **ottimamente efficiente**: nessun altro algoritmo ottimo espande meno nodi a parità di euristica; il prezzo è la memoria (mantiene tutti i nodi generati, come una BFS). **IDA\*** e **RBFS** riducono la complessità spaziale a scapito, in genere, di lavoro ripetuto: RBFS usa un upper bound dinamico per abbandonare rami non più promettenti, raggiungendo complessità spaziale lineare O(b·d) ma senza sfruttare memoria extra disponibile.
- La qualità di un'euristica si misura con l'**effective branching factor b\*** (`N+1 = 1+b*+...+(b*)^d`): più b* è vicino a 1, più l'euristica è informativa. Un criterio teorico complementare è la **dominanza**: se h2(n) ≥ h1(n) per ogni n (entrambe ammissibili), h2 domina h1 e garantisce che A* espanda un sottoinsieme dei nodi espansi con h1.
- Le euristiche ammissibili si costruiscono sistematicamente tramite **problemi rilassati** (rimozione di vincoli): il costo della soluzione ottima nel problema rilassato è sempre un'euristica ammissibile per il problema originale, perché il grafo rilassato è un supergrafo che contiene anche le soluzioni ottime originali. Nell'8-puzzle, h1 (tessere fuori posto) e h2 (distanza di Manhattan) nascono da due rilassamenti diversi dei vincoli di adiacenza/cella-vuota, e h2 domina h1.
- Quando più euristiche ammissibili non sono confrontabili, `h(n) = max(h1(n),...,hk(n))` è sempre ammissibile ed è dominante su tutte le componenti.
