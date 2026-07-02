# Modulo 4: Constraint Satisfaction Problems (CSP)

I problemi visti nei moduli precedenti (ricerca cieca ed euristica) trattano gli stati come "scatole nere": l'unica cosa che l'algoritmo di ricerca può fare è generare successori, testare l'obiettivo, eventualmente stimare una distanza tramite euristica. Nei CSP si apre la scatola: **lo stato ha una struttura interna esplicita** (un insieme di variabili con valori), e i vincoli fra le variabili sono rappresentati in modo dichiarativo. Questo permette di costruire algoritmi generali di risoluzione (non specifici per un singolo problema) e tecniche di potatura molto più efficaci della ricerca cieca.

Esempi di ambiti in cui i vincoli sono centrali: design di oggetti (vincoli funzionali/fisici), allocazione di risorse (quantità, priorità, tempi), progettazione di circuiti, pianificazione di percorsi robotici (es. manovre di parcheggio).

## Definizione formale di CSP

Un **constraint satisfaction problem (CSP)** è definito da:

- un insieme di **variabili** X1, …, Xn;
- un insieme di **domini** D1, …, Dn (uno per variabile, con i valori ammissibili);
- un insieme di **vincoli** C1, …, Cm che restringono le combinazioni di valori ammissibili;
- opzionalmente, una **funzione obiettivo** da massimizzare/minimizzare (nel caso più semplice di CSP "puro" non è richiesta: basta trovare un assegnamento che soddisfi tutti i vincoli).

### Stati e assegnamenti

- Gli **stati** di un CSP corrispondono a tutti i possibili **assegnamenti** di valori alle variabili.
- Un **assegnamento** {Xi1 = vi1, Xi2 = vi2, …} attribuisce valori a un sottoinsieme (anche vuoto o totale) delle variabili.
- Un assegnamento è detto:
  - **completo** se assegna un valore a tutte le variabili;
  - **consistente** se non viola alcun vincolo;
  - **soluzione** se è completo e consistente.
- Quando esiste una soluzione si dice anche che esiste un "mondo possibile" che soddisfa i vincoli.

### Esempio guida: colorazione della mappa dell'Australia

Colorare i 7 territori dell'Australia (WA, NT, SA, Q, NSW, V, T) con i colori {R, G, B} in modo che due territori confinanti non abbiano lo stesso colore.

- **Variabili**: WA, NT, SA, Q, NSW, V, T (una per territorio).
- **Domini**: uguali per tutte, D = {R, G, B}.
- **Vincoli** (binari, uno per ogni coppia di territori confinanti):
  WA≠NT, WA≠SA, NT≠SA, NT≠Q, SA≠Q, SA≠NSW, SA≠V, Q≠NSW, NSW≠V.
  (la Tasmania T è un'isola: non confina con nessuno, quindi non ha vincoli binari con le altre variabili).

Un possibile assegnamento parziale, es. {WA=R, NT=R, SA=G, …}, non è consistente (WA e NT confinano e hanno lo stesso colore). Un assegnamento consistente è {WA=R, NT=G, SA=B, …}. Una soluzione completa è {WA=R, NT=G, SA=B, Q=R, NSW=G, V=R, T=B}: da notare che **qualunque permutazione dei tre colori applicata a una soluzione è ancora una soluzione** (simmetria del problema).

I vincoli binari si rappresentano naturalmente come archi di un **grafo di vincoli**, i cui nodi sono le variabili: questa rappresentazione è centrale per gli algoritmi di propagazione (arc consistency, AC-3) che vedremo più avanti.

## Tipi di domini e di variabili

- **Domini finiti**: è possibile enumerare esplicitamente i vincoli mettendo in relazione i valori (es. Australia). Il caso particolare in cui il dominio è {vero, falso} dà luogo a CSP **booleani**, la cui decisione è NP-completa (es. 3-SAT).
- **Domini infiniti (discreti)**: non si possono enumerare i vincoli; si usano linguaggi di specifica. Esempio: per dire che "Lavoro2 deve iniziare almeno 5 giorni dopo Lavoro1" si scrive Lavoro1 + 5 < Lavoro2.
- **Domini continui**: tipici dei problemi di scheduling con tempi di inizio/fine reali. Se i vincoli sono disuguaglianze lineari che definiscono una regione convessa, il CSP si risolve con la **programmazione lineare** in tempo polinomiale.

## Arità dei vincoli

- **Vincoli unari**: coinvolgono una sola variabile (e un valore). Esempio: T ≠ G (la Tasmania non può essere verde).
- **Vincoli binari**: coinvolgono due variabili; sono gli archi del grafo di vincoli. Esempio: WA ≠ NT.
- **Vincoli a tre o più variabili (n-ari)**: coinvolgono un numero qualsiasi di variabili; si rappresentano con **ipergrafi** (archi che connettono più di due nodi). Esempio: diverse(WA, NT, SA). Spesso possono essere riscritti come insieme equivalente di vincoli binari.

### Esempio classico di vincolo n-ario: criptoaritmetica

```
   SEND
 + MORE
 -------
  MONEY
```

Ogni lettera rappresenta una cifra diversa (S, E, N, D, M, O, R, Y). Dominio di S e M: {1,…,9} (non possono essere zero, essendo cifre iniziali); dominio delle altre lettere: {0,…,9}. Vincoli: "a lettere diverse corrispondono valori diversi" (alldifferent) più il vincolo aritmetico globale, che coinvolge **tutte** le variabili e non è scomponibile in vincoli binari:

(1000·S + 100·E + 10·N + D + 1000·M + 100·O + 10·R + E) = (10000·M + 1000·O + 100·N + 10·E + Y)

### Vincoli vs. criteri di preferenza

I vincoli possono essere più o meno rigidi:

- una **soluzione** deve soddisfare **tutti** i vincoli veri e propri;
- una soluzione **può violare** uno o più **criteri di preferenza** (soft constraints);
- il soddisfacimento dei criteri di preferenza permette di **ordinare** le soluzioni ammissibili, distinguendo quelle preferibili da quelle meno preferibili.

Esempio: nella costruzione di un orario un docente preferisce le lezioni del mattino; questo "vincolo" è in realtà un criterio di preferenza da comporre con quelli di altri docenti. Il risultato finale potrebbe non soddisfare la preferenza (il docente finisce sempre al pomeriggio), ma può comunque essere la soluzione migliore fra quelle disponibili — non ottimale rispetto alla preferenza, ma ottima rispetto ai vincoli rigidi più il criterio complessivo.

## CSP come problema di ricerca nello spazio degli stati

I CSP si possono formulare come problemi di ricerca:

- **stato iniziale** = assegnamento vuoto { };
- **funzione successore** = assegna un valore a una delle variabili non ancora assegnate, scartando le scelte che generano conflitti immediati;
- **test obiettivo** = l'assegnamento corrente è completo (tutte le variabili hanno un valore);
- **costo di cammino** = costante per ogni passo (es. 1), perché conta solo raggiungere un assegnamento completo consistente, non "quanto costa" arrivarci.

Poiché ogni passo valorizza esattamente una variabile precedentemente non assegnata, **la profondità massima dell'albero di ricerca è n** (il numero di variabili).

### Perché l'ordine di assegnamento non conta: commutatività

Un aspetto fondamentale, specifico dei CSP rispetto alla ricerca generica: **uno stato è un assegnamento di valori** {X1=v1, …, Xn=vn}, e l'ordine (il cammino) con cui i valori sono stati assegnati alle variabili è **irrilevante ai fini del risultato**. Assegnare prima X1=v1 e poi X2=v2, oppure prima X2=v2 e poi X1=v1, porta allo stesso stato finale {X1=v1, X2=v2}. Si dice che **i CSP sono commutativi**.

Questa proprietà è cruciale dal punto di vista pratico: **gli algoritmi possono sempre scegliere prima una variabile e poi un valore per essa**, senza bisogno di considerare tutti gli ordini possibili delle variabili come rami distinti dell'albero di ricerca. Questo riduce drasticamente il fattore di ramificazione effettivo, come mostrato di seguito.

## Rappresentare gli stati: generate-and-test vs. ricerca con backtracking

### Approccio a forza bruta: generate-and-test

Usa **solo informazioni di stato**, ignorando i vincoli durante la generazione:

```
finché non hai una soluzione e ci sono alternative:
    1) genera un assegnamento completo
    2) controlla se è consistente
    3) se sì: è una soluzione, esci dal ciclo
    4) se no: torna al passo 1
se hai una soluzione: restituiscila
altrimenti: fallimento
```

Può richiedere di esplorare **l'intero spazio degli assegnamenti completi**, la maggior parte dei quali inconsistente: è enormemente dispendioso.

**Esempio, 8 regine**: posizionare 8 regine su una scacchiera 8×8 senza che nessuna sia sotto attacco (esistono 92 soluzioni, 12 a meno di simmetrie).

- *Rappresentazione 1*: variabili Q1..Q8 = posizione (1..64) della regina i-esima → d^n = 64^8 ≈ 2,81 × 10^14 assegnamenti possibili.
- *Rappresentazione 2* (migliore, sfrutta la conoscenza che ogni regina occupa una colonna diversa): variabili Q1..Q8 = numero di riga della regina nella colonna i, dominio {1..8} → 8^8 = 16.777.216 assegnamenti, molti meno ma ancora troppi.
- Con 16 regine si arriverebbe a 16^16 ≈ 1,8 × 10^19 configurazioni, stimate in ~1200 anni di computazione con generate-and-test.

La lezione è che **come rappresentiamo il problema conta moltissimo**, e che introdurre i vincoli esplicitamente (invece di generare e poi testare) è la strada per rendere trattabile la ricerca.

### Ricerca in profondità con backtracking

Si esplora lo spazio degli assegnamenti con una **depth-first search**, ma si usano i vincoli per **potare** (pruning) i cammini appena si genera un conflitto, invece di aspettare l'assegnamento completo. È una ricerca non informata + vincoli. La limitatezza della profondità dei cammini (= n) rende ragionevole la profondità, anche se il fattore di ramificazione può essere alto.

Analisi del branching factor: con n variabili e d valori medi per variabile, se **non** si sfrutta la commutatività, al primo livello il fattore di ramificazione è n·d (si può scegliere una qualsiasi fra n variabili e uno qualsiasi fra d valori), al secondo livello (n-1)·d, ecc. L'albero avrebbe **n! · d^n foglie** (nell'esempio Australia: 7 variabili, 3 valori → 7!·3^7 = 11.022.480 foglie).

Sfruttando la commutatività (si fissa **prima la variabile**, poi si sceglie il valore), il fattore di ramificazione si riduce a **d per livello**, e le foglie scendono a **d^n** (nell'esempio Australia: 3^7 = 2.187, un risparmio enorme rispetto a 11.022.480).

### Pseudocodice del backtracking

```
funzione BACKTRACKING-SEARCH(csp) restituisce soluzione o fallimento
    restituisci BACKTRACK({}, csp)

funzione BACKTRACK(assegnamento, csp) restituisce soluzione o fallimento
    se assegnamento è completo allora restituisci assegnamento
    var ← SELECT-UNASSIGNED-VARIABLE(csp)
    per ogni valore in ORDER-DOMAIN-VALUES(var, assegnamento, csp) fai
        se valore è consistente con assegnamento (rispetto ai vincoli) allora
            aggiungi {var = valore} ad assegnamento
            inferenze ← INFERENCE(csp, var, valore)
            se inferenze ≠ fallimento allora
                aggiungi inferenze ad assegnamento
                risultato ← BACKTRACK(assegnamento, csp)
                se risultato ≠ fallimento allora restituisci risultato
            rimuovi {var = valore} e le inferenze da assegnamento
    restituisci fallimento
```

Punti chiave: si fissa **una variabile per volta** (SELECT-UNASSIGNED-VARIABLE), si cerca un **valore consistente** con l'assegnamento parziale corrente secondo i vincoli, e si procede ricorsivamente; quando **tutti** i valori per la variabile corrente sono stati provati senza successo, si arriva a "fallimento" e si fa **backtracking** verso la chiamata precedente per esplorare un'altra alternativa.

### Limiti del backtracking semplice: il thrashing

Il backtracking di base è una ricerca in profondità **non informata**: non è particolarmente efficiente, ed è soggetta a **thrashing**: lo stesso errore (lo stesso assegnamento incompatibile fra due variabili) può ripetersi identico in più punti diversi dell'albero di ricerca, perché l'algoritmo non "ricorda" perché ha fallito.

Esempio: se il valore vi assegnato a Xi rende impossibile ogni valore per Xj (variabile scelta successivamente), il sottoalbero fallisce. Se in un altro ramo dell'albero si arriva di nuovo a scegliere prima Xi=vi e poi Xj, si ripete esattamente lo stesso fallimento, sprecando lavoro.

Per migliorare servono risposte a tre domande:

1. L'assegnamento della variabile corrente ha un impatto sulle variabili non ancora assegnate? → **inferenza/propagazione dei vincoli** (forward checking, arc consistency…).
2. L'ordinamento dei valori da provare influisce sul risultato? → **euristica del valore** (least constraining value).
3. Quando un cammino fallisce, è possibile fare tesoro dell'esperienza per evitare fallimenti simili? → **backjumping**, conflict set, apprendimento di NOGOOD.

## Euristiche per la scelta della variabile

A ogni passo del backtracking va scelta una variabile non assegnata su cui procedere. Farlo a caso è sub-ottimale.

### Minimum Remaining Values (MRV, o euristica "fail-first")

Sceglie la variabile con **il minor numero di valori legali rimasti** (consistenti con l'assegnamento corrente). L'idea è "fallire il prima possibile", così da scoprire subito i vicoli ciechi invece di scoprirli tardi dopo aver investito lavoro su altre variabili.

Esempio (Australia): assegnati WA=R e NT=B, restano 5 variabili. SA ha un solo valore possibile (deve essere diversa da rosso e da blu → verde): è la scelta più vincolata, quindi MRV sceglie SA.

### Degree heuristic (euristica di grado)

MRV non aiuta sempre: ad esempio nella scelta della **prima** variabile da assegnare (nessun vincolo è ancora stato attivato, tutte le variabili hanno lo stesso numero di valori residui) o in caso di **pareggio** fra più variabili con lo stesso MRV. In questi casi si usa l'**euristica di grado**: si sceglie la variabile **coinvolta nel maggior numero di vincoli** con le altre variabili non ancora assegnate.

Esempio: se l'unico assegnamento fatto finora è NT=B, WA, SA e Q sono in parimerito per MRV (ciascuna con 2 valori consistenti); l'euristica di grado sceglie **SA**, che è coinvolta in 5 vincoli (confina con WA, NT, Q, NSW, V), più di ogni altra variabile.

Le due euristiche si usano in combinazione: MRV come criterio principale, degree heuristic come tie-breaker.

## Euristica per la scelta del valore: Least Constraining Value (LCV)

Una volta scelta la variabile, in che ordine provare i suoi valori possibili? L'euristica del **valore meno vincolante** predilige il valore che **lascia più libertà** (più opzioni residue) alle variabili adiacenti nel grafo dei vincoli.

Esempio: assegnati WA=R e NT=G, si deve assegnare Q, che può valere B o R. I vicini di Q sono SA (dominio residuo {B}) e NSW (dominio residuo {R,G,B}):

- se Q=B: SA non ha più valori possibili (dominio vuoto!) e NSW si riduce a 2 valori;
- se Q=R: SA non viene per nulla ristretto, e NSW resterà con {G,B}.

Quindi **Q=R è la scelta meno vincolante**: una scelta più restrittiva fatta in anticipo rischia di tagliare fuori soluzioni raggiungibili, causando fallimenti evitabili più avanti nella ricerca.

Da notare la logica opposta rispetto a MRV: per la **variabile** si vuole la più vincolata (fail-first, per potare presto rami sbagliati), per il **valore** si vuole il meno vincolante (per non eliminare a priori soluzioni buone). MRV serve a decidere *cosa* assegnare, LCV serve a decidere *come* provare ad assegnarlo.

> ❓ **Domanda d'esame:** perché per la scelta della variabile si usa "la più vincolata" (MRV) mentre per la scelta del valore si usa "il meno vincolante" (LCV)? Non è contraddittorio?
> Non è contraddittorio perché i due criteri rispondono a obiettivi diversi. Scegliere la variabile più vincolata (con meno valori residui) serve a **individuare il prima possibile i vicoli ciechi**: se una variabile ha pochissime opzioni è più probabile che porti presto a un fallimento, ed è meglio scoprirlo subito piuttosto che dopo aver costruito un assegnamento parziale grande e costoso da disfare (principio del "fail-first"). Scegliere invece, per quella variabile, il valore meno vincolante per le altre serve a **massimizzare la probabilità di successo** del ramo che si sta esplorando, lasciando il maggior numero possibile di opzioni aperte alle variabili adiacenti non ancora assegnate. In sintesi: si sceglie "dove rischiare di fallire subito" (variabile) e poi, una volta lì, "come minimizzare il rischio di fallire" (valore).

## Rendere informata la ricerca: propagazione dei vincoli (inferenza)

Le euristiche di ordinamento migliorano *come* si esplora l'albero, ma non riducono di per sé lo spazio di ricerca. Il passo successivo è alternare fasi di **esplorazione** (assegnare una variabile) a fasi di **inferenza**: dopo ogni assegnamento si propagano le conseguenze sui domini delle altre variabili, eliminando valori che non potranno mai portare a una soluzione consistente con la scelta appena fatta. Questo è il principio della **consistenza locale**: ci si concentra su una proprietà di consistenza relativa a una parte del CSP (un sottoproblema) e si propaga l'informazione a tutto il grafo, cercando di costruire (o scartare) la soluzione.

Le proprietà/tecniche di consistenza locale principali, in ordine crescente di forza (e di costo):

1. **Forward checking** (più un approccio pratico che una proprietà formale)
2. **Node consistency** (riguarda singole variabili / vincoli unari)
3. **Arc consistency** (riguarda coppie di variabili / vincoli binari)
4. **Path consistency** (riguarda triplette di variabili)

### Forward checking

Idea: quando si assegna un valore a una variabile, si **guardano subito in avanti** i vicini diretti sul grafo dei vincoli e si eliminano dai loro domini i valori che sarebbero ormai incompatibili, invece di scoprirlo solo quando si arriverà ad assegnare quei vicini.

Esempio: se WA=R, i vincoli impongono che i vicini diretti NT e SA non potranno più essere R: si rimuove R dai loro domini residui **subito**, prima ancora di doverli assegnare. Il forward checking si accompagna naturalmente a MRV, perché aggiorna in tempo reale il numero di valori residui di ogni variabile (l'informazione di cui MRV ha bisogno).

**Esempio numerico (Australia)**: la tabella seguente mostra come si riducono i domini man mano che si effettuano gli assegnamenti WA=R, poi Q=G, poi V=B:

```
              WA    NT    Q    NSW   V     SA    T
INIZIO        RGB   RGB   RGB  RGB   RGB   RGB   RGB
WA=R  →        R    GB   RGB  RGB   RGB   GB    RGB
Q=G   →        R    B    G    RB    RGB   B     RGB
V=B   →        R    B    G    R     B     ø     RGB
```
Quando SA arriva a dominio vuoto (perché confina con WA, NT, Q e V, tutti già fissati su colori diversi), si ha fallimento immediato e si fa backtracking, senza dover neppure provare ad assegnare SA esplicitamente.

### Limiti del forward checking

Il forward checking **non cattura tutte le inconsistenze**, perché propaga solo dal nodo appena assegnato verso i suoi vicini diretti, senza controllare le conseguenze fra coppie di vicini fra loro. Esempio: dopo WA=R e Q=G, i domini residui di NT e SA restano entrambi {B} (entrambi ridotti a un solo valore, lo stesso): questo forza un'inconsistenza, perché NT e SA sono confinanti e sarebbero costretti ad avere **lo stesso** colore B, violando il vincolo NT≠SA. Il forward checking, però, non se ne accorge, perché non confronta i domini residui di NT e SA fra loro: se ne accorgerà solo più avanti nella ricerca, quando tenterà di assegnarli esplicitamente.

### Node consistency

Un grafo di vincoli è **node consistent** quando lo sono tutte le sue variabili; una variabile è node consistent quando **rispetta tutti i vincoli unari** che la riguardano. Esempio: il vincolo "età compresa fra 18 e 35 anni" si esprime con due vincoli unari, età > 18 e età < 35; l'algoritmo di node consistency filtra dal dominio della variabile "età" tutti i valori che non li rispettano. È la forma più semplice di consistenza locale, e si applica una tantum come preprocessing sui domini iniziali (rende i vincoli unari "impliciti" nel dominio, così gli algoritmi successivi possono ignorarli).

### Arc consistency

Un grafo di vincoli è **arc consistent** quando rispetta tutti i vincoli binari. È una proprietà importante perché **ogni vincolo a tre o più variabili può sempre essere trasformato in un insieme equivalente di vincoli binari**, dunque tecniche pensate per l'arc consistency hanno applicabilità generale.

**Nota di confronto con forward checking**: il forward checking, di fatto, realizza un controllo di arc consistency limitato ai soli archi che collegano la variabile appena assegnata con i suoi vicini diretti; **non propaga** però il ragionamento ai vicini dei vicini. L'arc consistency, applicata sistematicamente (con un algoritmo come AC-3), fa esattamente questo: propaga a catena su tutto il grafo.

**Definizione formale**: dato un grafo di vincoli, un **arco** è un lato orientato (l'arco WA→NSW è diverso, e va trattato separatamente, dall'arco NSW→WA). Un arco X→Y è **consistente** quando: per ogni valore possibile di X (vertice sorgente) esiste **almeno un** valore di Y (vertice destinazione) ad esso consistente rispetto al vincolo.

Esempio: se il dominio di WA è {R, G} e il dominio di NSW è {R}: l'arco WA→NSW **non** è consistente, perché se WA=R allora NSW non ha alcun valore assegnabile (essendo NSW={R} e dovendo NSW≠WA); l'arco NSW→WA, invece, è consistente (per l'unico valore di NSW, R, esiste un valore consistente in WA, cioè G).

Quando un arco non è consistente, si possono **eliminare valori dal dominio della variabile sorgente** finché l'arco non diventa consistente.

### Algoritmo AC-3

Sviluppato nel 1977 da Alan Mackworth (Arc Consistency algorithm #3). Viene insegnato perché è più efficiente dei precedenti (AC-1, AC-2) e più semplice dei successivi (AC-4, ecc.). Si può usare come **preprocessing** prima della ricerca, oppure **intrecciato con il backtracking** per propagare via via le scelte fatte: quest'ultimo uso prende il nome di algoritmo **MAC** (Maintaining Arc Consistency).

**Idea generale**: si mantiene una coda (queue) di archi da verificare. Si estrae un arco (Xi → Xj), si controlla se è consistente; se si eliminano valori dal dominio di Xi per renderlo consistente, **tutti gli archi che puntano a Xi** (del tipo Xk → Xi, per ogni vicino Xk di Xi diverso da Xj) devono essere rimessi in coda, perché la riduzione del dominio di Xi potrebbe aver reso quegli archi non più consistenti.

```
funzione AC-3(csp) restituisce false se un dominio è svuotato (CSP inconsistente), true altrimenti
    queue ← insieme di tutti gli archi (Xi, Xj) del csp
    finché queue non è vuota:
        rimuovi un arco (Xi, Xj) da queue
        se REVISE(csp, Xi, Xj) allora
            se Di è vuoto allora restituisci false
            per ogni Xk vicino di Xi, Xk ≠ Xj:
                aggiungi (Xk, Xi) a queue
    restituisci true

funzione REVISE(csp, Xi, Xj) restituisce true se il dominio di Xi è stato modificato
    revised ← false
    per ogni x in Di:
        se non esiste alcun valore y in Dj tale che (x,y) soddisfa il vincolo tra Xi e Xj:
            elimina x da Di
            revised ← true
    restituisci revised
```

**Esempio guidato (Australia, con WA=R, Q=G già assegnati)**: si inizializza la coda con tutti gli archi orientati (WA→NT, NT→WA, NT→Q, Q→NT, WA→SA, SA→WA, SA→Q, Q→SA, …). Si estraggono e verificano man mano:

- WA→NT: consistente (R è compatibile con G e B, i valori residui di NT) → si rimuove semplicemente dalla coda.
- NT→WA: **non** consistente (R di NT è incompatibile con R di WA) → si rimuove R dal dominio di NT; si rimette in coda ogni arco Xk→NT (WA→NT, SA→NT, Q→NT).
- NT→Q: **non** consistente (G di NT incompatibile con G di Q) → si rimuove G da NT; si rimettono in coda gli archi verso NT (già presenti).
- Q→NT, WA→SA: consistenti.
- SA→WA: **non** consistente (R di SA incompatibile con R di WA) → si rimuove R da SA; si rimette in coda WA→SA.
- NT→WA, WA→NT: consistenti (di nuovo, coi domini aggiornati).
- SA→Q: **non** consistente (G di SA incompatibile con G di Q) → si rimuove G da SA; si rimettono in coda gli archi verso SA.
- NT→WA, WA→NT: consistenti.
- Q→SA: consistente.
- NT→SA: **non** consistente (l'unico valore rimasto in NT, B, è incompatibile con l'unico valore rimasto in SA, B) → si rimuove B da NT.
- A questo punto **NT ha dominio vuoto**: l'algoritmo segnala che l'assegnamento WA=R, Q=G **non è consistente** (nessuna estensione è possibile), senza dover esplorare esplicitamente tutte le variabili rimanenti.

Questo esempio mostra bene il valore pratico di AC-3: scopre l'inconsistenza **per propagazione**, risparmiando la ricerca esplicita.

### Costo computazionale di AC-3

- Un CSP con n variabili e vincoli binari ha al più n² archi.
- Sia d il numero massimo di valori nel dominio di una variabile.
- Il tempo nel caso peggiore è **O(n²d³)**.
- È più costoso del forward checking, ma anche più efficace (elimina più inconsistenze).
- **AC-3 è incompleto**: esistono assegnamenti globalmente inconsistenti che l'arc consistency da sola non rileva (vedi sotto).

### Incompletezza di AC-3 (arc-consistent ma senza soluzione)

Esempio: un grafo a 3 nodi (1, 2, 3) tutti collegati a due a due (triangolo), con dominio {bianco, nero} per ciascuno e vincolo "colori diversi" fra ogni coppia collegata. Il grafo **è arc consistent** (per ogni valore di ogni nodo esiste un valore compatibile nel vicino), **eppure non esiste soluzione**, perché con solo 2 colori non si può colorare un triangolo (3-clique) in modo che tutte le coppie abbiano colori diversi. Questo mostra che l'arc consistency, da sola, **non è sufficiente** a garantire (né a rilevare l'assenza di) una soluzione: serve una proprietà più forte, la **path consistency**, oppure comunque va completata con una fase di ricerca (backtracking) sopra i domini ridotti.

### Path consistency

Proprietà **più forte** dell'arc consistency: identifica vincoli impliciti dedotti da **triplette** di variabili. Una coppia di variabili {X1, X2} è path consistent rispetto a una terza variabile X3 quando: per ogni assegnamento {X1=a, X2=b} consistente con i vincoli esistenti fra X1 e X2, esiste un valore di X3 che soddisfa contemporaneamente i vincoli su {X1,X3} e {X2,X3}.

Esempio (Australia semplificata a 2 colori R/B): consideriamo la coppia {WA, SA} e la variabile NT. I casi consistenti per {WA,SA} sono {WA=R,SA=B} o {WA=B,SA=R}. In entrambi i casi NT non ha alcun valore compatibile con entrambi WA e SA contemporaneamente (NT confina con entrambi e con solo 2 colori disponibili non può differire da entrambi): quindi il CSP **non ha soluzione**, cosa che l'arc consistency da sola non avrebbe rilevato.

L'algoritmo **PC-2** (sempre di Mackworth) propaga la path consistency in modo analogo a come AC-3 propaga l'arc consistency, ma con complessità maggiore.

### Generalizzazione: k-consistency

Un CSP è **k-consistent** quando: per ogni sottoinsieme di k-1 variabili e per ogni loro assegnamento consistente, è sempre possibile trovare un assegnamento consistente per una qualunque k-esima variabile.

- 1-consistency = node consistency
- 2-consistency = arc consistency
- 3-consistency = path consistency

Un CSP è **fortemente k-consistent** quando è k-consistent, (k-1)-consistent, …, fino a 1-consistent (cioè tutti i livelli di consistenza fino a k sono soddisfatti simultaneamente). Ad esempio, un CSP fortemente 3-consistent ha: tutte le triplette di variabili legate da vincoli che soddisfano la path consistency, tutte le coppie legate da vincolo che soddisfano l'arc consistency, e tutte le variabili che soddisfano i vincoli unari.

**Risultato teorico**: un CSP fortemente k-consistent (con k pari al numero di variabili n) può essere risolto **senza mai fare backtracking**, in tempo O(n·d): intuitivamente, essendo 1-consistent si può iniziare da un valore consistente per X1; essendo 2-consistent si trova un valore consistente per le variabili direttamente legate a X1; essendo 3-consistent si trova un valore consistente per le variabili legate a coppie delle precedenti; e così via. Il problema pratico è che **decidere se un CSP è fortemente k-consistent ha esso stesso costo esponenziale**, quindi in pratica questo risultato è più di interesse teorico che applicativo diretto — motiva però l'uso di tecniche di consistenza parziale (arc consistency) come compromesso costo/beneficio.

## Vincoli speciali (globali)

Alcuni tipi di vincoli ricorrono così spesso da essere stati studiati con algoritmi dedicati più efficienti del trattamento generico:

### Alldifferent(X1, …, Xn)

Impone che tutte le variabili elencate assumano valori tutti diversi fra loro (generalizzazione del vincolo binario "diverso da" a n variabili). Se le n variabili possono assumere complessivamente **meno di n valori distinti** (m < n), il vincolo non può mai essere soddisfatto (pigeonhole principle) e si rileva subito il fallimento. Altrimenti, si assegnano per prime le variabili che hanno un solo valore possibile, si verifica che il vincolo resti soddisfatto, e si propaga la scelta riducendo via via i domini delle altre variabili coinvolte (simile in spirito al forward checking, ma specializzato per questo tipo di vincolo).

### Atmost(N, A1, …, Ak)

Vincolo di risorse: le attività A1, …, Ak possono complessivamente impegnare **al più N** risorse. Supponendo i domini di ogni Ai ordinati crescentemente, si sommano i valori minimi v11+…+vk1: se la somma supera N, il vincolo è insoddisfacibile; altrimenti si possono eliminare i valori massimi che, sommati ai minimi altrui, violerebbero il limite N. Per domini molto grandi (es. logistica, dove non è pratico enumerare esplicitamente ogni valore) i domini si rappresentano come **intervalli** [vi1, vim] e la propagazione agisce sulla ridefinizione degli estremi degli intervalli, non su enumerazioni esplicite.

## Oltre il backtracking cronologico: backjumping

### Il limite del backtracking cronologico

Quando il backtracking standard raggiunge un vicolo cieco, torna indietro **sempre e solo** alla variabile assegnata al passo immediatamente precedente (backtracking **cronologico**), indipendentemente dal fatto che quella variabile abbia o meno causato il conflitto. Questo non sfrutta l'informazione sui vincoli ed eredita i limiti delle strategie di ricerca cieche.

**Esempio**: assegnamento corrente {Q=R, NSW=G, V=B, T=R}. Si sceglie SA: tutti i valori possibili vanno in conflitto, perché Q, NSW e V (tutti confinanti con SA) coprono già l'intero spettro dei colori. La variabile scelta alla chiamata ricorsiva precedente era **T**, quindi il backtracking cronologico tornerebbe indietro su T — ma **T non ha nessun ruolo nel conflitto** (T non confina con SA)! Si sprecherebbe lavoro riprovando altri valori di T inutilmente.

### Backjumping: backtracking non cronologico

Strategia più intelligente: tornare indietro direttamente a **una variabile che potrebbe risolvere il problema** (nell'esempio: V). Per farlo, ogni variabile mantiene un **conflict set**: l'insieme degli assegnamenti (di altre variabili) che hanno contribuito a creare il conflitto. Nell'esempio, il conflict set di SA è {Q=R, NSW=G, V=B}.

**Definizione formale di conflict set**: sia A un assegnamento parziale consistente, sia X una variabile non ancora assegnata. Se A ∪ {X=vi} risulta inconsistente per **ogni** valore vi del dominio di X, allora A è un conflict set di X.

Un conflict set è **minimo** quando togliendo uno qualsiasi degli assegnamenti che lo compongono esso cessa di essere un conflict set (cioè ogni elemento del conflict set è davvero necessario a causare il conflitto). Quando si verifica un fallimento su una variabile, il **backjumping** usa il conflict set per decidere direttamente a quale variabile precedente saltare (nell'esempio: V), senza passare per le variabili intermedie estranee al conflitto (T).

### Relazione fra backjumping e forward checking

Il forward checking (FC) può essere arricchito per costruire automaticamente i conflict set: quando una variabile viene assegnata e FC propaga la scelta eliminando valori dai domini di altre variabili (es. V=B elimina B dal dominio di SA), basta registrare la relazione "chi ha causato l'eliminazione": conflict(SA) ← conflict(SA) ∪ {V=B}.

**Nota importante**: il forward checking, se arricchito così, rileva **esattamente gli stessi conflitti** che rileverebbe il backjumping puro. Quindi **usare backjumping insieme a forward checking è ridondante** — le due tecniche, combinate ingenuamente, non si sommano in efficacia perché coprono lo stesso tipo di informazione.

## Assegnamenti NOGOOD e conflict-directed backjumping

### NOGOOD

Analogia con i sistemi operativi: nel controllo del deadlock esistono stati "sicuri", "insicuri" e di "blocco" — uno stato insicuro non è ancora un blocco, ma vi conduce necessariamente. Analogamente, un **assegnamento NOGOOD** in un CSP è un **assegnamento parziale** che, pur non essendo ancora un vicolo cieco immediato, **non può mai essere esteso a una soluzione** — lo si scopre solo esplorando ulteriormente.

Esempio (Australia): {WA=R, NSW=R} è NOGOOD. Non è un vicolo cieco immediato (la ricerca può proseguire, ad esempio con T=R, senza problemi apparenti), e i conflict set di V, Q e NT conterranno separatamente o l'assegnamento di WA o quello di NSW, ma raramente entrambi assieme finché non si prova a chiudere il cerchio. Solo quando si tenta di assegnare NT, SA, Q o V (che devono essere B o G, ma essendo a loro volta confinanti fra loro esauriscono le combinazioni possibili con soli 2 colori residui) si scopre il fallimento — ma a quel punto non è ovvio "risalire" alla vera causa (la scelta iniziale WA=R, NSW=R).

### Conflict-directed backjumping

Il backjumping "semplice" basato sui soli conflict set locali non risolve completamente il problema NOGOOD, perché il conflitto dipende sia dagli assegnamenti già fatti sia dalle variabili non ancora assegnate (e dalle loro reciproche relazioni). Il **conflict-directed backjumping** aggiorna dinamicamente i conflict set mano a mano che si esplora, propagando le informazioni scoperte "a ritroso" fra variabili, così da saltare direttamente ai veri responsabili del conflitto, anche se non direttamente confinanti con la variabile fallita.

**Regola di aggiornamento**: sia Xj la variabile corrente su cui tutti i valori falliscono. Si fa backjump alla variabile Xi aggiunta più di recente a conf(Xj), aggiornando: conf(Xi) ← conf(Xi) ∪ conf(Xj) − {Xi}.

**Esempio numerico completo (Australia)**: assegnando nell'ordine WA=R, NSW=R, T=B, NT=B, Q=G, si arriva a dover assegnare SA, ma nessun valore funziona. I conflict set costruiti via FC durante il percorso sono:

```
conf(WA) = {}
conf(NSW) = {}
conf(T) = {}
conf(NT) = {WA}
conf(Q) = {NSW, NT}
conf(SA) = {WA, NSW, NT, Q}
```

- **Backjump a Q** (variabile aggiunta più di recente a conf(SA)): conf(Q) ← {NSW,NT} ∪ {WA,NSW,NT,Q} − {Q} = {WA, NSW, NT}. Da notare: **WA non confina con Q**, ma viene comunque registrato nel suo conflict set perché ha contribuito indirettamente al conflitto — si scopre così un "vincolo implicito". Si prova Q=B, Q=R: falliscono entrambi (arc consistency lo esclude), dominio di Q vuoto.
- **Backjump a NT**: conf(NT) ← {WA} ∪ {WA,NSW,NT} − {NT} = {WA, NSW}. Si prova NT=G (fallisce) e NT=B (fallisce): dominio di NT vuoto.
- **Backjump a NSW**: conf(NSW) ← {} ∪ {WA,NSW} − {NSW} = {WA}. Il metodo ha così **scoperto la relazione fra NSW e WA** (che in effetti sono confinanti). Si prova NSW=G: questa volta si riesce a costruire una soluzione completa.

**Osservazione conclusiva**: la ricerca era partita da uno stato NOGOOD, e l'ha scoperto solo esplorando; ma i vincoli hanno guidato la scoperta di relazioni implicite fra variabili. Registrare gli stati NOGOOD minimali permette all'algoritmo di evitare di ripetere in futuro gli stessi assegnamenti falliti: si tratta, a tutti gli effetti, di una **forma di apprendimento** (nearly identica nello spirito al clause learning dei moderni SAT solver).

## Applicazioni ed esempi aggiuntivi

### Sudoku come CSP

- **Variabili**: una per ogni casella xij (i = riga, j = colonna).
- **Dominio**: {1, …, 9}; alcune variabili hanno un valore prefissato dalla griglia iniziale (i valori prefissati sono **vincoli unari**).
- **Vincoli** (tutti espressi con il vincolo globale alldifferent):
  - per ogni riga i: alldifferent(xi1, …, xi9)
  - per ogni colonna j: alldifferent(x1j, …, x9j)
  - per ogni riquadro 3×3: alldifferent delle 9 celle del riquadro.

### N-regine su larga scala

Grazie a tecniche avanzate (in particolare il local search, cfr. min-conflicts, e formulazioni CSP efficienti), alcuni algoritmi moderni sono riusciti a risolvere il problema delle N regine con **N = 6.000.000**: un salto enorme rispetto ai pochi milioni di configurazioni testabili con generate-and-test già discusso per N=16.

### Applicazioni reali di tipo ricerca operativa

- **Location of facilities**: dato un elenco di magazzini e richieste dei clienti, trovare un percorso che soddisfi le richieste minimizzando i costi.
- **Job scheduling**: sequenziare operazioni di macchinari per produrre diversi prodotti minimizzando il tempo totale di produzione.
- **Car sequencing**: nell'industria automobilistica, ordinare la produzione di auto con optional diversi senza eccedere la capacità delle aree di lavoro dedicate al montaggio degli optional.
- **Cutting stock problem**: tagliare materiale in pezzi più piccoli minimizzando lo spreco.
- **Vehicle routing**: trovare il percorso di costo minimo per rifornire n clienti da un unico deposito.
- **Timetabling**: costruzione automatica di orari (didattici, tenendo conto di aule/laboratori e altri vincoli).
- **Rostering / crew scheduling**: definizione di turni ed equipaggi (es. compagnie aeree). Nel 1998 CSP realizzati in ECLiPSe sono stati usati per definire gli equipaggi dei treni delle Ferrovie dello Stato italiane.

### Software e strumenti per CSP

- **Linguaggi di programmazione a vincoli**: dichiarativi, spesso sviluppati come moduli di Prolog.
- **ECLiPSe** (eclipseclp.org): ambiente per programmazione a vincoli; usato ad esempio da Opel (premio VDA Logistics Award 2015, ottimizzazione della catena di distribuzione con Flexis AG).
- **CHR** (Constraint Handling Rules, Università di Leuven): disponibile per vari Prolog, Java, Haskell, C; applicato ad esempio alla navigazione robotica.
- **SAT solver**: risolvono CSP a variabili booleane; molti sono basati sull'algoritmo **DPLL** arricchito con risoluzione di conflitti, backjumping, propagazione, apprendimento di clausole. MiniSat, vincitore della competizione SAT 2005, è open source.
- **GECODE** (C++, con interfaccia grafica) e **GECODE/R** (binding Ruby): framework generali per la modellazione e risoluzione di CSP.
- **Answer Set Programming (ASP)**: non nasce specificamente per i CSP, ma è uno strumento (concettuale e pratico) con cui si possono programmare e risolvere CSP (es. il problema della zebra), approfondito nel corso "Intelligenza Artificiale e Laboratorio" della magistrale.

> ❓ **Domanda d'esame:** qual è la differenza pratica fra forward checking, arc consistency (AC-3) e path consistency, e quando conviene usare l'una o l'altra?
> Le tre tecniche formano una gerarchia crescente di potenza (e di costo): il **forward checking** propaga solo dalla variabile appena assegnata ai suoi vicini diretti, aggiornandone i domini residui; è economico e si integra naturalmente con MRV, ma non rileva inconsistenze fra due vicini non ancora assegnati (es. NT e SA entrambi ridotti allo stesso unico valore, pur essendo confinanti). L'**arc consistency** (realizzata dall'algoritmo AC-3) propaga sistematicamente su tutti gli archi del grafo, non solo quelli toccati dall'ultimo assegnamento: quando riduce un dominio, rimette in coda tutti gli archi entranti nel nodo modificato, così l'informazione si propaga "a catena" su tutto il grafo. Costa O(n²d³) contro il costo minore del forward checking, ma è più efficace; resta comunque **incompleta** (un grafo può essere arc consistent e non avere comunque soluzione, come nell'esempio del triangolo a 2 colori). La **path consistency** è più forte ancora, perché ragiona su triplette di variabili e può scoprire l'assenza di soluzione anche quando l'arc consistency non ce la fa, ma il suo algoritmo (PC-2) ha complessità maggiore. In pratica: il forward checking si usa sempre "in linea" durante il backtracking per il suo basso costo; l'arc consistency (via AC-3 o l'algoritmo MAC che la integra nel backtracking) si usa quando serve una potatura più efficace e ci si può permettere il costo aggiuntivo; la path consistency (e la k-consistency in generale) restano soprattutto di interesse teorico, perché il loro costo cresce rapidamente e decidere il grado di consistenza di un CSP è esso stesso costoso.

## Riepilogo e punti chiave

- Un **CSP** è definito da variabili, domini e vincoli; una soluzione è un assegnamento **completo e consistente**. I vincoli possono essere unari, binari (rappresentabili come grafo di vincoli) o n-ari (rappresentabili come ipergrafo, spesso riscrivibili in vincoli binari equivalenti); si distinguono inoltre vincoli rigidi da criteri di preferenza (soft).
- I CSP si formulano naturalmente come problema di ricerca nello spazio degli assegnamenti (stato iniziale = assegnamento vuoto, successori = estensione di una variabile, obiettivo = assegnamento completo). Grazie alla **commutatività** (l'ordine di assegnamento non influisce sul risultato) si può sempre fissare prima la variabile e poi il valore, riducendo il fattore di ramificazione da n·d a d per livello.
- Il **generate-and-test** è impraticabile su problemi anche piccoli (esplosione combinatoria: d^n). Il **backtracking** (depth-first + vincoli usati per potare) è già molto più efficiente, ma soffre di **thrashing** se non guidato da euristiche e inferenza.
- **Euristiche di scelta della variabile**: MRV (Minimum Remaining Values / fail-first) sceglie la variabile più vincolata, per scoprire prima i fallimenti; la **degree heuristic** (grado, numero di vincoli con variabili non assegnate) serve come tie-breaker, specie all'inizio della ricerca. **Euristica di scelta del valore**: Least Constraining Value (LCV) sceglie il valore che lascia più opzioni aperte ai vicini, per massimizzare la probabilità di successo del ramo.
- **Tecniche di inferenza/propagazione** (dalla più economica alla più potente): forward checking (propaga solo ai vicini diretti della variabile appena assegnata) → node consistency (vincoli unari) → arc consistency/AC-3 (vincoli binari, propagazione a catena su tutto il grafo, O(n²d³), ma incompleta) → path consistency/PC-2 (triplette di variabili, più forte ma più costosa). Generalizzazione: **k-consistency** e **forte k-consistency** (un CSP fortemente n-consistent si risolve senza backtracking, ma verificarlo è esponenziale).
- **Vincoli globali** come Alldifferent e Atmost hanno algoritmi di propagazione dedicati, più efficienti del trattamento generico, e sono la base di molte modellazioni pratiche (es. Sudoku è interamente esprimibile con vincoli Alldifferent).
- Il **backtracking cronologico** torna sempre indietro alla variabile immediatamente precedente, anche se non è la causa del conflitto. Il **backjumping** usa i **conflict set** per saltare direttamente alla variabile realmente responsabile; se combinato con forward checking arricchito con il tracciamento dei conflitti, il backjumping diventa ridondante (FC da solo rileva già gli stessi conflitti). Il **conflict-directed backjumping** affina ulteriormente il meccanismo per gestire gli **assegnamenti NOGOOD** (assegnamenti parziali non estendibili a soluzione, scoperti solo esplorando), aggiornando dinamicamente i conflict set e scoprendo relazioni implicite fra variabili non direttamente connesse: è, di fatto, una forma di apprendimento.
- I CSP hanno applicazioni pratiche pervasive (scheduling, routing, timetabling, car sequencing, crew scheduling…) e un ecosistema di software dedicato (ECLiPSe, CHR, SAT solver come MiniSat, GECODE, ASP), a conferma che si tratta di un paradigma di modellazione, non solo di un esercizio accademico.
