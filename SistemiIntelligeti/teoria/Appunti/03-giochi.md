# MODULO 3 — Ricerca con avversario (giochi)

## Introduzione: perché studiare i giochi in AI

Marvin Minsky (1968) osservava che *"i giochi non vengono scelti perché sono chiari e semplici, ma perché ci danno la massima complessità con le minime strutture iniziali"*. I giochi sono quindi un banco di prova ideale per l'AI: regole semplici e stato ben definito, ma spazio di ricerca enorme e presenza di un **avversario** che rende il problema strutturalmente diverso dalla ricerca "in solitaria" vista nei moduli precedenti.

Il tema dei giochi attraversa più discipline (pungolo scientifico):

- **Matematica**: teoria dei grafi, complessità computazionale
- **Computer Science**: AI, database, calcolo parallelo
- **Economia**: teoria dei giochi, economia cognitiva/sperimentale
- **Psicologia**: fiducia, percezione del rischio

### Ambienti competitivi

Un **ambiente multi-agente** è competitivo quando gli obiettivi degli agenti sono **conflittuali**: il conseguimento dell'obiettivo di un agente impedisce (almeno in parte) il conseguimento di quello degli altri. In questo contesto, i problemi di ricerca con avversario sono detti **giochi**. Le azioni degli altri agenti non sono più cooperative come nella pianificazione classica, ma vanno anticipate come ostili.

## Tassonomia dei giochi

I giochi si classificano lungo due assi indipendenti:

**Condizioni di scelta (informazione)**

- **Informazione perfetta/completa**: lo stato del gioco è totalmente esplicito e visibile a tutti i giocatori (es. scacchi, dama, Otello, Forza4, tris)
- **Informazione imperfetta**: lo stato è solo parzialmente noto ad ogni giocatore (es. Mastermind, Scarabeo, Bridge, Poker e in genere i giochi di carte, dove le carte avversarie sono nascoste)

**Effetti della scelta (determinismo)**

- **Deterministici**: lo stato successivo è determinato unicamente dalle azioni degli agenti
- **Stocastici**: lo stato successivo dipende anche da fattori esterni casuali (es. lancio di dadi in Backgammon e Monopoli, pescate a caso in Risiko)

| | Informazione perfetta | Informazione imperfetta |
|---|---|---|
| **Deterministici** | Scacchi, Go, Dama, Otello, Forza4, Tris | Mastermind, Scarabeo, Bridge, Poker |
| **Stocastici** | Backgammon, Monopoli | Risiko |

Il Modulo 3 si concentra sui **giochi ad informazione completa (perfetta)**, tipicamente deterministici e a due giocatori, a **somma zero**.

### Gioco a somma zero

> Un gioco a somma zero è un contesto di interazione multi-agente in cui la perdita (o il guadagno) di un agente è esattamente compensata dal guadagno (perdita) degli altri agenti.

Esempio intuitivo: la torta da dividere. Se le fette sono irregolari, la parte in più che riceve chi ha la fetta più grande è esattamente compensata dalla parte in meno ricevuta dagli altri. Nei giochi a due giocatori a somma zero, se l'utilità di uno stato terminale per il giocatore A è *u*, l'utilità dello stesso stato per B è *-u*: è sufficiente memorizzare un solo valore per conoscere automaticamente anche l'altro.

### Perché il tris è un caso interessante da studiare

Osservando lo sviluppo di una partita a tris si notano fenomeni chiave:

- Ogni giocatore, quando è il suo turno, sceglie tra più mosse possibili (branching)
- **L'ambiente è multi-agente**: l'evoluzione dello stato è solo *parzialmente controllabile* dal singolo giocatore, perché l'altro giocatore muove alternandosi
- Una mossa che apre a una vittoria "a tre passi" può essere più rischiosa di una vittoria immediata, perché nel frattempo l'avversario ha la possibilità di reagire e ribaltare la situazione
- In una posizione di svantaggio, conviene comunque "prolungare il più possibile" la partita piuttosto che perdere subito, perché ciò lascia all'avversario più occasioni di commettere un errore

Questi esempi illustrano intuitivamente l'idea centrale della ricerca competitiva: bisogna ragionare **ipoteticamente sulle mosse dell'avversario**, non solo sulle proprie.

### Differenze rispetto alla ricerca (in)formata "classica"

| Ricerca classica | Ricerca con avversario |
|---|---|
| Obiettivo: trovare un cammino a costo minimo | Obiettivo: determinare una **strategia** (funzione che associa una mossa a ogni stato raggiungibile), non una singola sequenza fissa |
| Si usa g(x), il costo del cammino | g(x) non si usa: guadagno/perdita non dipendono dal costo delle azioni (assunto uniforme) |
| I nodi terminali hanno un costo/valore | I nodi terminali sono categorizzati come **vittoria, sconfitta, parità** |
| Il nodo successore è sempre scelto dall'agente | **Anche l'avversario muove**: la scelta del nodo successivo non è sempre sotto il controllo dell'agente |

Perché serve una *strategia* e non un semplice piano: poiché non si sa in anticipo quale mossa farà l'avversario, occorre precalcolare la risposta migliore per **ogni possibile mossa avversaria**, non solo per un'unica sequenza ipotizzata.

## Caratteristiche formali del gioco (a due giocatori)

- Due giocatori, convenzionalmente chiamati **MAX** e **MIN**; MAX muove per primo
- Ciascun giocatore non conosce in anticipo la mossa che farà l'altro, ma **conosce l'insieme delle mosse possibili** e può calcolare gli stati successori che ne deriverebbero
- **Osservabilità**:
  - *totale* nei giochi a turni: ogni giocatore conosce l'esito delle mosse precedenti prima di scegliere la propria
  - *parziale* nei giochi ad azione simultanea: i giocatori non conoscono le mosse eseguite simultaneamente dall'avversario
- A partire dallo stato iniziale si costruisce un **albero di gioco**, applicando ricorsivamente le azioni disponibili e calcolando gli stati successori
- Alcuni stati sono **terminali**: quando se ne raggiunge uno, la partita finisce
- I giocatori valutano gli stati tramite una funzione di **utilità**, che tiene necessariamente conto anche del punto di vista dell'avversario
- **Ipotesi di pessimismo**: si assume che l'avversario sia "infallibile" e giochi sempre la mossa che gli porta il massimo guadagno possibile (il peggior danno per noi) — è un'ipotesi conservativa che garantisce una strategia sicura anche contro l'avversario più forte possibile
- I giochi a turno più semplici sono descritti come **2-ply**: un *ply* è un mezzo turno, cioè la mossa di un solo giocatore (un turno completo = 2 ply, uno per MAX e uno per MIN)

### Albero di gioco: definizione

L'**albero di gioco** è la struttura che rappresenta tutte le evoluzioni possibili della partita a partire dallo stato iniziale:

- la **radice** è lo stato iniziale (turno di MAX)
- ogni **nodo interno** rappresenta uno stato di gioco, etichettato come nodo MAX o nodo MIN a seconda di chi deve muovere
- gli **archi** rappresentano le mosse legali
- le **foglie** sono gli stati terminali, cui è associata un'**utilità** definita dalle regole del gioco (tipicamente: vittoria/sconfitta/pareggio per il gioco del tris, un valore numerico continuo per giochi con punteggio)

## Algoritmo Minimax

### Idea e strategia ottima

La **strategia ottima** per un agente è la sequenza di mosse (in realtà, la funzione che mappa ogni stato raggiungibile nella mossa migliore) che, assumendo un avversario perfetto, massimizza l'utilità garantita. Poiché l'agente non sa come muoverà l'altro, può solo *"immedesimarsi"* nell'avversario e ragionare ipoteticamente: costruisce mentalmente l'intero albero di gioco, assumendo che:

- nei nodi in cui muove **MAX**, verrà scelta la mossa che **massimizza** il valore per MAX
- nei nodi in cui muove **MIN** (l'avversario, infallibile), verrà scelta la mossa che **minimizza** il valore per MAX (cioè quella più svantaggiosa possibile per MAX)

### Definizione ricorsiva: valore-minimax

```
                ⎧ Utilità(n)                       se n è terminale
Minimax(n)  =   ⎨ max_{s ∈ Succ(n)} Minimax(s)      se n è un nodo MAX
                ⎩ min_{s ∈ Succ(n)} Minimax(s)      se n è un nodo MIN
```

Il valore minimax è quindi calcolato ***ricorsivamente per ogni nodo*** dell'albero, dal basso (foglie) verso l'alto (radice), e permette all'agente di scegliere la mossa da eseguire alla radice (si sceglie il figlio con il valore minimax più alto, se si è in un nodo MAX).

Da qui il nome "minimax": **ogni giocatore, minimizzando il guadagno massimo dell'altro, minimizza automaticamente la propria perdita** — grazie alla proprietà di somma zero (utilità di uno = meno utilità dell'altro), tenere traccia di un solo valore per nodo è sufficiente.

### Pseudocodice

```
funzione MINIMAX-DECISION(stato) restituisce una mossa
    return arg max_{a ∈ Azioni(stato)} MIN-VALUE(Risultato(stato, a))

funzione MAX-VALUE(stato) restituisce un valore di utilità
    if TEST-TERMINALE(stato) then return Utilità(stato)
    v ← -∞
    for each a in Azioni(stato) do
        v ← MAX(v, MIN-VALUE(Risultato(stato, a)))
    return v

funzione MIN-VALUE(stato) restituisce un valore di utilità
    if TEST-TERMINALE(stato) then return Utilità(stato)
    v ← +∞
    for each a in Azioni(stato) do
        v ← MIN(v, MAX-VALUE(Risultato(stato, a)))
    return v
```

L'algoritmo effettua una **visita ricorsiva in profondità** (DFS) dell'intero albero, con chiamate alternate tra `MAX-VALUE` e `MIN-VALUE`. Ogni nodo assume il proprio valore solo alla **chiusura** della relativa chiamata ricorsiva (cioè dopo che tutti i suoi figli sono stati valutati): i nodi terminali ricevono come valore la loro utilità diretta; i nodi interni ricevono il max o il min dei valori dei figli, a seconda del tipo.

### Esempio passo-passo

Consideriamo un piccolo albero di gioco a 4 livelli (2 turni completi, 4 ply: MAX-MIN-MAX-MIN), con branching factor 3 e 9 foglie, valori di utilità arbitrari (schema analogo a quello usato nelle slide):

```
                                   MAX (radice)
                    ┌────────────────┼────────────────┐
                  MIN(A)           MIN(B)           MIN(C)
              ┌─────┼─────┐    ┌─────┼─────┐    ┌─────┼─────┐
             3      12    8    2      4     6    14     5    2
```

Valutazione bottom-up:

1. **Foglie**: valore = utilità diretta (3, 12, 8, 2, 4, 6, 14, 5, 2)
2. **Nodo MIN(A)**, figlio della radice: MIN sceglie la mossa peggiore per MAX tra {3, 12, 8} → `min(3,12,8) = 3`
3. **Nodo MIN(B)**: `min(2,4,6) = 2`
4. **Nodo MIN(C)**: `min(14,5,2) = 2`
5. **Radice (MAX)**: MAX sceglie la mossa che massimizza il proprio guadagno tra i valori calcolati per i figli, {3, 2, 2} → `max(3,2,2) = 3` → **MAX sceglierà il ramo verso MIN(A)**

Il valore minimax della radice è **3**: è il massimo risultato che MAX può *garantirsi* contro un avversario che gioca in modo ottimale (non è detto sia il massimo assoluto raggiungibile nell'albero — qui 14 — perché per raggiungerlo MAX dovrebbe "sperare" in un errore di MIN, cosa che l'ipotesi pessimistica esclude).

Questo è esattamente lo schema mostrato nelle slide (radice MAX → 3 nodi MIN → 9 foglie): a ogni nodo MIN si applica `v ← min(...)` scegliendo la mossa meno vantaggiosa per MAX, mentre alla radice MAX si applica `v ← max(...)` scegliendo la mossa più vantaggiosa per sé.

### Complessità

- **Temporale**: O(b^m), dove *b* = fattore di ramificazione (branching factor) e *m* = profondità massima dell'albero — è una visita esaustiva in profondità dell'intero albero
- **Spaziale**: O(bm) se i successori vengono generati uno alla volta (non tutti contemporaneamente); O(b·m) è comunque **lineare** nella profondità (tipico vantaggio della DFS), a differenza della complessità temporale che resta **esponenziale**

### Proprietà

- **Completo**: sì, su alberi/grafi finiti
- **Ottimale**: sì, ma solo a condizione che **sia MAX sia MIN giochino in modo ottimale** (se l'avversario reale non gioca ottimamente, la strategia minimax resta comunque *sicura*, garantendo almeno il valore calcolato)

### Estensione a più di due giocatori

Minimax si estende a giochi con più di due giocatori sostituendo il valore scalare di ogni nodo con un **vettore di utilità** ⟨u₁, ..., uₖ⟩, dove uᵢ è l'utilità del nodo per il giocatore i. Un fenomeno tipico che emerge in questo scenario è la possibile **formazione di alleanze** tra sottoinsiemi di giocatori.

> ❓ **Domanda d'esame:** perché in un gioco a due giocatori a somma zero basta un solo valore per nodo, mentre con più giocatori serve un vettore?
> Nella somma zero a due giocatori l'utilità di un giocatore è sempre l'opposto di quella dell'altro (u₂ = -u₁), quindi un solo numero descrive completamente la situazione di entrambi. Con tre o più giocatori questa relazione di opposizione non vale più (il guadagno di uno non implica necessariamente e proporzionalmente la perdita degli altri, soprattutto se si formano alleanze), quindi occorre tracciare separatamente l'utilità di ciascun giocatore in ogni nodo.

---

## Teoria delle decisioni: maximax, maximin, minimax regret

Prima di tornare ai giochi con avversario, le slide introducono tre approcci generali di **teoria delle decisioni** per scegliere tra alternative quando l'esito dipende da fattori **non controllabili** (nei giochi, il ruolo di "fattore non controllabile" sarà giocato proprio dall'avversario).

### Scenario di esempio: tabella dei payoff

Si deve scegliere un investimento tra tre alternative, sapendo che il mercato può salire, restare stabile o scendere (andamento non controllabile, dipende da dinamiche esterne):

| alternative | sale | stabile | scende |
|---|---|---|---|
| fondo1 | 40 | 45 | 5 |
| fondo2 | 70 | 30 | -20 |
| azioni | 55 | 40 | -10 |

Le **scelte** (righe) sono sotto il controllo del decisore, se ne può fare **una sola**; i **payoff** (che possono rappresentare guadagni, perdite, o altre misure come tempo o risorse, a seconda del problema specifico) dipendono anche dall'andamento del mercato, non controllabile.

### Approccio maximax (ottimistico)

Si guarda, per ciascuna scelta, il **payoff più alto ottenibile**, e si sceglie l'alternativa che promette il massimo assoluto: il "massimo dei massimi".

Nell'esempio: fondo1→45, fondo2→**70**, azioni→55 ⇒ si sceglie **fondo2**.

È un approccio **ottimistico**: non offre alcuna garanzia che le dinamiche esterne (il mercato) evolvano effettivamente nella direzione più favorevole per la scelta fatta.

### Approccio maximin (pessimistico/conservativo)

Si guarda, per ciascuna scelta, il **payoff peggiore possibile** (la perdita maggiore), e si sceglie l'alternativa che **minimizza la perdita massima**: il "massimo dei minimi".

Nell'esempio: fondo1→5, fondo2→-20, azioni→-10 ⇒ si sceglie **fondo1** (unica opzione che non va mai in perdita).

È l'approccio **conservativo/pessimistico**: si presuppone che accada sempre lo scenario peggiore per la scelta fatta — è esattamente la stessa logica prudente su cui si basa **minimax** nei giochi con avversario (si veda oltre).

### Approccio minimax regret

Introduce il concetto di **rimpianto (regret)**: quanto si "perde" rispetto alla scelta che, col senno di poi, sarebbe stata ottimale in quello scenario.

```
Regret = Best payoff (nello scenario) − Real payoff (della scelta fatta)
```

Passo 1 — calcolo dei regret per ciascuno scenario (colonna):

- Scenario "sale": best payoff = 70 (fondo2). Regret: fondo1 = 70-40 = 30; fondo2 = 70-70 = 0; azioni = 70-55 = 15
- Analogamente si calcolano i regret per "stabile" e "scende"

Passo 2 — **regret table** risultante:

| alternative | sale | stabile | scende |
|---|---|---|---|
| fondo1 | 30 | 0 | 0 |
| fondo2 | 0 | 15 | 25 |
| azioni | 15 | 5 | 15 |

Passo 3 — per ciascuna alternativa si prende il **regret massimo** (il caso peggiore di rimpianto): fondo1→30, fondo2→25, azioni→15. Si sceglie l'alternativa con il **minimo tra i regret massimi**: **azioni**, con rimpianto massimo pari a 15.

### Quando si usa ciascun approccio

- **Maximax**: quando il decisore è disposto a rischiare pur di non perdere l'occasione migliore (visione ottimistica del futuro/dell'avversario)
- **Maximin**: quando occorre una garanzia di sicurezza, si vuole evitare lo scenario peggiore ad ogni costo (visione pessimistica/prudente) — è il criterio "difensivo" per eccellenza
- **Minimax regret**: quando si vuole evitare grandi rimpianti *a posteriori*, bilanciando le altre due visioni: non è né il più ottimista né il più prudente in assoluto, ma minimizza il massimo "errore di scelta"

### Collegamento con i giochi con avversario

Nei giochi, la "dinamica esterna non controllabile" è costituita proprio dalle **mosse dell'avversario**: non sappiamo quale sceglierà, dobbiamo basarci solo sullo stato corrente e sulle mosse disponibili. I giocatori razionali sono **pessimisti/conservativi** per definizione (ipotesi di avversario infallibile): per questo l'algoritmo Minimax è concettualmente lo stesso approccio ***maximin*** applicato ricorsivamente lungo l'albero di gioco, turno dopo turno.

---

## Potatura alfa-beta (Alpha-Beta Pruning)

### Motivazione

Minimax richiede una visita **esaustiva** dell'albero, con complessità temporale esponenziale O(b^m): in giochi reali (scacchi, Go) è del tutto improponibile. L'idea della potatura alfa-beta è che **non serve esplorare tutti i rami**: se durante la visita si scopre che un ramo non potrà mai influenzare la decisione finale alla radice (perché è già "battuto" da un'alternativa migliore trovata altrove), si può **evitare di espanderlo**, senza perdere nulla in termini di correttezza del risultato alla radice.

Esempio intuitivo dalle slide: se in un nodo MIN si è già trovato un successore di valore 2, e gli altri fratelli non ancora espansi sono foglie di un sottoalbero il cui valore minimo sarebbe comunque più alto di 2, è inutile espanderli: darebbero comunque un vantaggio a MAX che MIN (razionale) non permetterebbe mai di realizzare.

### Definizione di α e β

Durante l'esplorazione si mantengono due valori, aggiornati e propagati lungo la ricorsione:

- **α (alfa)** = il **massimo lower bound** trovato finora per MAX lungo il cammino dalla radice al nodo corrente = il valore della miglior scelta per MAX trovata finora in un qualsiasi punto di scelta lungo il cammino. Inizialmente **α = -∞**. È aggiornato dai nodi **MAX**.
- **β (beta)** = il **minimo upper bound** trovato finora per MIN lungo il cammino = il valore della miglior scelta per MIN trovata finora lungo il cammino. Inizialmente **β = +∞**. È aggiornato dai nodi **MIN**.

Ha senso continuare a esplorare un nodo **se e solo se** il suo valore stimato è compreso nell'intervallo **[α, β]**. Idealmente, [α, β] è un intervallo che si **restringe progressivamente** man mano che la ricerca procede.

### Quando si pota un ramo

Se in un certo nodo i due estremi si "invertono" (cioè si verifica **β ≤ α**), nessun valore del sottoalbero rimanente potrà mai essere contemporaneamente minore di β e maggiore di α: è quindi inutile continuare l'esplorazione di quel sottoalbero, e si può interrompere immediatamente (**potatura/pruning**).

- **Beta-pruning**: avviene in un nodo MIN quando si trova un successore con valore v ≤ α (il nodo MIN, che sta minimizzando, non potrà mai restituire alla radice/al padre MAX un valore migliore di α, quindi il ramo padre-MAX ignorerà comunque questo nodo)
- **Alfa-pruning**: avviene simmetricamente in un nodo MAX quando si trova un successore con valore v ≥ β

> Nota tecnica dalle slide: il pruning avviene correttamente solo se il test usato è `if (v ≤ α) return value` (disuguaglianza **non stretta**) e non `if (v < α)`; questo garantisce la potatura anche nei casi limite in cui il valore coincide esattamente con il bound.

### Pseudocodice

```
funzione ALFA-BETA-DECISION(stato) restituisce una mossa
    return arg max_{a ∈ Azioni(stato)} MIN-VALUE(Risultato(stato,a), -∞, +∞)

funzione MAX-VALUE(stato, α, β) restituisce un valore di utilità
    if TEST-TERMINALE(stato) then return Utilità(stato)
    v ← -∞
    for each a in Azioni(stato) do
        v ← MAX(v, MIN-VALUE(Risultato(stato,a), α, β))
        if v ≥ β then return v        # beta cutoff (poda: MIN non lascerà mai arrivare qui)
        α ← MAX(α, v)                 # MAX-VALUE aggiorna il lower bound
    return v

funzione MIN-VALUE(stato, α, β) restituisce un valore di utilità
    if TEST-TERMINALE(stato) then return Utilità(stato)
    v ← +∞
    for each a in Azioni(stato) do
        v ← MIN(v, MAX-VALUE(Risultato(stato,a), α, β))
        if v ≤ α then return v        # alfa cutoff (poda: MAX non sceglierà mai questo ramo)
        β ← MIN(β, v)                 # MIN-VALUE aggiorna l'upper bound
    return v
```

Come riassunto nelle slide: **MAX-VALUE modifica il lower bound (α)**, **MIN-VALUE modifica l'upper bound (β)**.

### Esempio passo-passo (tracciamento sull'albero delle slide)

Riprendendo lo stesso albero di gioco usato per Minimax (radice MAX, 3 figli MIN, ciascuno con 3 foglie: gruppi {3,17,2}, {12,15,25}, {0,2,14} secondo l'ordine delle slide):

1. **Radice**: α=-∞, β=+∞. Si scende nel primo figlio MIN, propagando gli stessi bound (scendendo la ricorsione i bound non cambiano fino al primo terminale)
2. Si raggiunge la prima foglia del primo nodo MIN: valore **3**. Il nodo MIN aggiorna il proprio upper bound locale: β=3 (non può garantire a MAX più di 3, avendo già questa opzione)
3. Si esamina il secondo figlio di quel nodo MIN: valore **17**. Poiché 17 > 3, per MIN (che vuole minimizzare) questo non migliora la sua scelta: β resta 3
4. Terminato il nodo MIN (valore finale 3, esaminati tutti i figli, es. anche 2 se presente non cambia il min), si retropropaga: il nodo MAX radice aggiorna **α = 3** (MAX sa di potersi garantire almeno 3 tramite questo ramo)
5. Si passa al secondo figlio MIN della radice, con **α=3, β=+∞** ereditati. Il suo primo figlio è terminale con valore **2**: il nodo MIN aggiorna β=2. Ma ora **β(2) ≤ α(3)**: gli estremi si sono "incrociati" → **beta-pruning**: il nodo MIN non può avere un valore superiore a 2, che è già peggiore (per MAX) del 3 già garantito altrove, quindi si interrompe l'esplorazione dei restanti fratelli di questo nodo MIN (non serviranno mai a MAX). Il nodo assume il valore stimato 2 (una **stima**, perché la ricerca è stata interrotta prima di esplorare tutto)
6. Retropropagando: 2 non migliora α alla radice (2 < 3), quindi α resta 3 alla radice
7. Si passa al terzo figlio MIN della radice, ereditando α=3, β=+∞. Si scende fino a un nodo MAX intermedio, il quale trova un figlio di valore **15**: aggiorna il proprio α=15 (MAX qui può garantirsi almeno 15). Ma il nodo MAX ha come vincolo dall'alto β=3 ereditato dal genitore MIN: poiché ora α(15) ≥ β(3), si verifica **alfa-pruning**: l'esplorazione si interrompe, il nodo assume il valore stimato 15
8. Il nodo MIN padre (il terzo figlio della radice) ha ora visto i valori 3 e 15 tra i suoi successori: essendo MIN, sceglie il minimo, cioè **3** (β resta 3, non modificato dal valore peggiore 15)
9. Retropropagando fino alla radice: MAX ha visto i tre rami con valori 3, 2, 3 → **max = 3**. Il valore finale della radice è **3**, identico a quello ottenuto con Minimax puro

Nell'esempio completo delle slide (20 nodi totali), alfa-beta esamina solo **11 nodi su 20**, restituendo comunque il valore corretto (3) e la stessa mossa ottima alla radice.

### Equivalenza con Minimax e guadagno in complessità

Alpha-beta pruning e Minimax sono ***equivalenti*** nel senso che:

- trovano entrambi la **stessa mossa ottima** per il nodo radice
- attribuiscono al nodo radice la **stessa valutazione**

Alfa-beta raggiunge lo stesso risultato **espandendo molti meno nodi**. Nel caso migliore, la complessità temporale passa da ***O(b^m)*** a ***O(b^(m/2))***. Esempio intuitivo dalle slide: con b=2, m=8, si passa da 2^8=256 nodi a 2^4=16 nodi espansi — un risparmio enorme che, applicato ricorsivamente, permette di raddoppiare la profondità di ricerca esplorabile nello stesso tempo rispetto a Minimax puro.

### Importanza dell'ordinamento delle mosse

L'efficacia della potatura ***dipende fortemente dall'ordine*** in cui i successori di ciascun nodo vengono considerati:

- Se il successore più promettente (**killer move**) viene esaminato **per ultimo**, non è possibile evitare di esplorare i sottoalberi dei suoi fratelli, e il guadagno di alfa-beta si riduce drasticamente
- La complessità O(b^(m/2)) si ottiene **solo** quando si riesce a espandere per primi i figli più promettenti (ordinamento ottimale dei successori): in questo caso il branching factor "effettivo" diventa circa la **radice quadrata** del branching factor originale (esempio dagli scacchi: b=35 diventa ≈6 con buon ordinamento e alfa-beta)
- Quando l'ordinamento dei successori **non è possibile** (caso medio, ordine casuale), la complessità è **O(b^(3m/4))** — una via di mezzo tra il caso migliore e quello peggiore

> ❓ **Domanda d'esame:** perché l'ordinamento delle mosse è così cruciale per alfa-beta?
> Perché la potatura si verifica solo quando i bound α e β si "incrociano" abbastanza presto durante l'esplorazione dei fratelli di un nodo. Se il valore migliore (killer move) viene trovato subito, i bound si stringono rapidamente e i fratelli successivi, meno promettenti, vengono scartati senza doverli espandere. Se invece la mossa migliore viene trovata per ultima, i bound restano larghi per tutta l'esplorazione dei fratelli precedenti, e nessuna potatura può avvenire: nel caso peggiore alfa-beta degenera esattamente nella stessa complessità di Minimax, O(b^m).

### Come trovare le killer moves

Le slide propongono tre tecniche per stimare in anticipo quali mosse esplorare per prime:

1. **Apprendimento**: il sistema "ricorda" le esperienze passate e le usa per stimare la mossa più promettente (efficace, ma richiede tempo per imparare)
2. **Combinazione con iterative deepening**: le informazioni ottenute alle iterazioni più superficiali (profondità minori) vengono usate per ordinare le mosse alle iterazioni più profonde successive
3. **Tabelle di trasposizione**: spesso usate insieme ad alfa-beta + iterative deepening

### Trasposizioni

In molti giochi, sequenze di mosse **diverse nell'ordine** possono condurre allo **stesso stato finale** (es. M1-M2-M3-M4 e M2-M3-M1-M4 producono lo stesso stato). Questi ordinamenti alternativi sono detti **trasposizioni**.

Quando lo spazio degli stati è grande, riconoscere le trasposizioni è importante per **evitare di rivisitare (ed esplorare) più volte gli stessi stati**. Si mantiene una **hash table** (tabella delle trasposizioni): ogni volta che si genera un nuovo stato, si verifica se corrisponde a uno stato già raggiunto tramite una trasposizione precedente; in caso affermativo, non lo si esplora di nuovo (si riusa il valore già calcolato). Quando lo spazio eccede le capacità di memoria disponibili, si mantengono in tabella solo le voci usate più **di frequente** o più **di recente** (politiche tipo LRU).

---

## Ricerca con profondità limitata e funzioni di valutazione euristica

### Il problema del real-time

Alfa-beta riduce lo spazio esplorato, ma **deve comunque arrivare fino agli stati terminali** per calcolare valori esatti. In giochi con alberi molto profondi (es. scacchi) questo può risultare troppo lento quando esiste un **vincolo sui tempi di risposta** (contesto *real-time*). Serve quindi introdurre dei **test di cutoff** che permettano di fermare la ricerca e produrre una decisione **prima** di raggiungere i nodi terminali.

### Funzione di valutazione euristica

Idea generale: in molti problemi è possibile **categorizzare gli stati non terminali** in base a caratteristiche osservabili, stimando la probabilità che, partendo da quello stato, si arrivi alla vittoria (rispetto a pareggio/sconfitta), sulla base di statistiche sulle classi di stati simili.

In pratica, però, il numero di classi necessarie per una stima significativa è **troppo alto** da gestire esplicitamente. La soluzione standard è usare una **funzione di valutazione lineare** che combina un insieme di caratteristiche (*features*) pesate:

```
eval(s) = Σ_{i=1..k} wᵢ · fᵢ(s)
```

dove fᵢ sono le feature dello stato (es. negli scacchi: numero di pedoni, alfieri, torri ecc. ancora posseduti da ciascun giocatore) e wᵢ i pesi associati, che ne indicano l'importanza relativa. Questa combinazione **lineare** è la forma più semplice possibile di aggregazione delle feature (le slide notano esplicitamente che questo concetto sarà ripreso parlando di reti neurali, dove le combinazioni possono diventare non lineari).

### Alfa-beta con cutoff (versione con profondità limitata)

Si modifica l'algoritmo sostituendo il test di terminalità con un **test di taglio** generico:

```
if [TEST-TAGLIO(stato, profondità)] then return eval(stato)
```

al posto di `if TEST-TERMINALE(stato) then return Utilità(stato)`.

Possibili strategie per decidere **quando tagliare**:

1. **Profondità massima predefinita**: si taglia sempre a una profondità fissata a priori
2. **Iterative deepening**: quando è il proprio turno, si usa tutto il tempo disponibile per cercare la mossa migliore con approfondimenti crescenti (si esegue la ricerca a profondità 1, poi 2, poi 3...); allo scadere del tempo disponibile si restituisce la miglior mossa trovata fino a quel momento

### Problema dell'orizzonte

I tagli artificiali introducono un rischio noto come **problema dell'orizzonte**: l'algoritmo "non vede oltre" il punto di taglio, ma in certe fasi del gioco la situazione può ribaltarsi molto rapidamente subito dopo — ovvero la funzione di valutazione risulta **instabile** in quel punto. Tagliare la ricerca in questi punti è **prematuro e rischioso**, perché l'avversario potrebbe forzare successivamente un forte cambiamento della valutazione che l'algoritmo non ha potuto "vedere".

### Quiescenza

Concetto proposto da Berliner (1973) per mitigare il problema dell'orizzonte: la decisione di terminare o continuare la ricerca in un nodo deve dipendere dalla ***quiescenza*** della funzione di valutazione in quel nodo, cioè dalla stabilità/permanenza nel tempo del segno (positivo o negativo) della valutazione.

- Nodi la cui valutazione è **quiescente** (stabile) possono essere tagliati in sicurezza
- Nodi **non quiescenti** (valutazione instabile, suscettibile di grandi variazioni imminenti) richiedono **ulteriore esplorazione** dei sottoalberi che li hanno come radice, prima di potersi fidare della stima

(Berliner realizzò anche il primo programma capace di battere un maestro umano in un gioco — nel suo caso il backgammon.)

---

## Giochi stocastici: cenni (expectiminimax)

Le slide lette non trattano esplicitamente l'algoritmo *expectiminimax* in dettaglio (non presente come sezione dedicata in questi tre file), ma introducono la distinzione tra giochi **deterministici** e **stocastici** nella tassonomia iniziale (es. Backgammon, Monopoli, Risiko), evidenziando che in questi giochi lo stato successivo dipende **anche da fattori esterni** non controllabili da nessuno dei due giocatori (tipicamente il lancio di dadi). Concettualmente, questo richiederebbe di estendere l'albero di gioco con **nodi di caso** (chance nodes), il cui valore si calcola come **valore atteso** (media pesata sulle probabilità) dei valori dei successori, anziché come max o min — da qui il nome *expectiminimax*. Non essendo questo argomento sviluppato nelle slide di riferimento del modulo, va eventualmente approfondito sul libro di testo (Russell & Norvig) se richiesto dal programma d'esame.

---

## Programmi storici che giocano

Le slide riportano una rassegna di sistemi che hanno raggiunto risultati storicamente rilevanti applicando (spesso in combinazione) i concetti visti:

- **Checkers (dama)**: Samuel, Chinook
- **Othello**: Logistello
- **Backgammon**: TD-gammon
- **Go**: AlphaGo
- **Bridge**: Bridge Baron, GIB
- **Scacchi**: DeepBlue

### DeepBlue

- Primo calcolatore a battere un Campione del Mondo in carica (Garry Kasparov) a scacchi, con cadenza di tempo da torneo (10 febbraio 1996)
- Hardware: sistema a parallelismo massivo con 30 nodi basati su RS/6000, supportato da 480 processori VLSI dedicati al gioco degli scacchi; sistema operativo AIX; algoritmo implementato in C
- Capacità: **200 milioni di posizioni al secondo**
- Algoritmo: **iterative deepening + alpha-beta search con tabella delle trasposizioni**
- Elemento chiave del successo: generare **estensioni oltre il limite di profondità** per le posizioni ritenute particolarmente interessanti (idea affine alla quiescenza)
- Di routine raggiungeva profondità 14, in certi casi fino a 40
- Funzione di valutazione: oltre **8000 feature**, inizializzate manualmente e poi raffinate automaticamente; database con 700.000 partite di gran maestri e ampio database di finali di partita (tutte le posizioni con 5 pezzi rimanenti, molte con 6)
- Curiosità: Kasparov sospettò (a torto o a ragione) che alcune mosse fossero state suggerite scorrettamente da un umano

### AlphaGo

- Sviluppato da Google, primo programma a battere un maestro umano a Go **senza handicap**, su goban di dimensione standard (2015)
- Nelle 500 partite disputate contro altri programmi: le vinse quasi tutte su singolo computer (tranne una), tutte quando eseguito su un cluster (1202 CPU + 176 GPU, circa 25 volte più hardware); la versione cluster batté quella single-computer nel 77% delle partite
- Approccio: combinazione di **deep learning (reti neurali)** e **ricerca su alberi**; le reti furono addestrate su un dataset di 30.000.000 di mosse umane e poi ulteriormente raffinate tramite **self-play** (partite contro se stesso)

## Un parallelo con la memoria umana

Le slide chiudono il modulo con un confronto tra la memoria "di lavoro" usata dagli algoritmi di ricerca (il numero di nodi che occorre mantenere in memoria durante la visita) e la capacità della memoria di lavoro (a breve termine) umana:

- **Legge di Miller (1956)**: la capacità della memoria a breve termine umana è stimata in **7 ± 2** elementi
- **Cowan (2001)**: revisione più recente, stima **4 ± 1** elementi ("The magical number 4 in short-term memory: A reconsideration of mental storage capacity")

Il parallelo è un modo per collegare, in chiave interdisciplinare, i limiti computazionali/di memoria degli algoritmi di ricerca con i limiti cognitivi umani nell'affrontare compiti analoghi (da cui l'uso di euristiche anche nel gioco umano).

---

## Riepilogo e punti chiave

- I **giochi** sono problemi di ricerca **multi-agente competitiva**: gli obiettivi degli agenti sono in conflitto, e le mosse dell'avversario non sono controllabili. Si distinguono per informazione (completa/incompleta) ed effetti delle scelte (deterministico/stocastico); questo modulo tratta soprattutto giochi **deterministici a informazione completa, a due giocatori, a somma zero**.
- In un **gioco a somma zero**, il guadagno di un giocatore è l'esatto opposto della perdita dell'altro: basta un solo valore di utilità per nodo per descrivere entrambi i giocatori.
- L'**albero di gioco** rappresenta tutte le evoluzioni possibili; i nodi si alternano tra turno di **MAX** (massimizza) e turno di **MIN** (minimizza, rappresenta l'avversario, assunto infallibile/ottimale).
- **Minimax** calcola ricorsivamente, dal basso verso l'alto, il valore di ogni nodo (max nei nodi MAX, min nei nodi MIN, utilità diretta nelle foglie), garantendo ad ogni giocatore il miglior risultato ottenibile contro un avversario ottimale. Complessità: **O(b^m)** in tempo, **O(bm)** in spazio; completo e ottimale (se entrambi giocano in modo ottimale).
- Gli approcci di **teoria delle decisioni** (maximax, maximin, minimax regret) generalizzano il ragionamento a scenari con esiti incerti non controllabili: **maximax** è ottimistico (massimizza il miglior caso), **maximin** è pessimistico/conservativo (massimizza il caso peggiore — è l'approccio concettualmente identico a Minimax), **minimax regret** minimizza il massimo rimpianto rispetto alla scelta ottimale a posteriori.
- La **potatura alfa-beta** rende Minimax praticabile potando i rami che non possono influenzare la decisione alla radice, mantenendo **α** (miglior garanzia per MAX) e **β** (miglior garanzia per MIN) lungo la ricorsione: si pota quando β ≤ α. Trova sempre lo **stesso risultato** di Minimax, ma con complessità che nel caso migliore scende a **O(b^(m/2))** — dimezzando l'esponente, quindi permettendo di raddoppiare la profondità esplorabile a parità di tempo.
- L'efficacia della potatura dipende **criticamente dall'ordinamento delle mosse**: esplorare prima le mosse più promettenti (killer move) è ciò che permette di avvicinarsi al caso migliore; senza un buon ordinamento la complessità peggiora fino a **O(b^(3m/4))**.
- Nei giochi reali, dove non si può visitare l'intero albero in tempo utile, si introducono **cutoff a profondità limitata** con **funzioni di valutazione euristica** (tipicamente combinazioni lineari pesate di feature), incorrendo però nel **problema dell'orizzonte**; la nozione di **quiescenza** aiuta a decidere in modo più robusto dove tagliare la ricerca.
- Programmi storici come **DeepBlue** (scacchi, iterative deepening + alfa-beta + tabelle di trasposizione) e **AlphaGo** (Go, reti neurali + ricerca ad albero + self-play) sono applicazioni celebri di questi principi, ciascuno esteso con tecniche aggiuntive (funzioni di valutazione enormi, apprendimento automatico) per gestire la complessità dei rispettivi giochi.
