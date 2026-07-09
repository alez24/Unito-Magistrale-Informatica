# Modulo 6: Logica del primo ordine (FOL)

> "Rappresentiamo mondi complessi in cui gli oggetti sono in relazione gli uni con gli altri e studiamo come ragionare su queste rappresentazioni più espressive." (C. Baroglio)

## Perché non basta la logica proposizionale

### Pregi della logica proposizionale (da mantenere)

La logica proposizionale è un buon punto di partenza perché ha tre proprietà preziose che **vogliamo conservare** anche nel passaggio a una logica più potente:

- **È dichiarativa**: separa nettamente la conoscenza (le formule) dall'inferenza (l'algoritmo che le manipola); consente di derivare fatti da fatti sfruttando una semantica basata su una relazione di verità fra formule e mondi possibili.
- **È composizionale**: il valore di verità di una formula si ottiene componendo i valori di verità delle sue parti (es. il valore di `A ∧ B` dipende solo dai valori di `A` e di `B`).
- **Non è ambigua**: ogni formula ha un significato preciso, indipendente dal contesto.

### I limiti espressivi

Il problema della logica proposizionale è la **mancanza di espressività**:

1. **Non permette rappresentazioni compatte.** Per dire che "una persona quando è felice ascolta musica" dobbiamo scrivere una proposizione *per ogni singola persona*:

   ```
   ascoltaMusica(mia) ⇐ felice(mia)
   ascoltaMusica(jody) ⇐ felice(jody)
   ascoltaMusica(yolanda) ⇐ felice(yolanda)
   ...
   ```

   Non esiste un modo per scrivere l'affermazione generale una sola volta.

2. **Non permette di esprimere relazioni fra elementi** (es. `padre(x, y)`): in proposizionale ogni fatto è un simbolo atomico indivisibile, non si può parlare di *oggetti* che stanno in *relazione* fra loro.

In sintesi: la logica proposizionale tratta il mondo come un insieme di fatti vero/falso "piatti", senza struttura interna. Serve una logica che parli di **oggetti** e delle **relazioni** che li legano.

> Nota di contesto (cenno da slide): esistono molte altre logiche specializzate — temporale (ragiona sul tempo, es. "A non è vero finché B non diventa vero"), epistemica (conoscenza: "l'agente i sa A"), deontica (obblighi/permessi/proibizioni), fuzzy (gradi di verità in [0,1], utile per predicati vaghi come `vecchio(X)`). FOL è la strada scelta dal corso perché aggiunge espressività mantenendo semantica dichiarativa e composizionale, senza ambiguità.

## Dalla logica proposizionale a FOL

**Logica proposizionale**: ogni fatto è vero o falso, punto.

**Logica del prim'ordine (FOL, First-Order Logic)**: il mondo è fatto di **oggetti** in **relazione** fra loro; una relazione può essere verificata oppure no per una data tupla di oggetti.

| | Modello proposizionale | Modello FOL |
|---|---|---|
| Cosa contiene | Attribuzione di valori di verità a simboli proposizionali | Un **dominio** D (insieme di oggetti del mondo) più delle **relazioni** fra tali oggetti |

### Elementi sintattici di FOL

- **Simboli di costante**: `Richard`, `John`, `2`, `Gamba`, `Corona` — nominano oggetti specifici.
- **Simboli di predicato**: `Fratello`, `<`, `>`, `SullaTesta` — esprimono relazioni/proprietà.
- **Simboli di funzione**: `+`, `Antenato` — restituiscono un oggetto a partire da altri oggetti.
- **Simboli di variabile**: `x`, `y`, `z`.
- **Connettivi**: `⇒ ⇔ ∧ ∨ ¬` (stessi della proposizionale).
- **Uguaglianza**: `=`.
- **Quantificatori**: `∀ ∃` (il vero elemento nuovo).
- **Punteggiatura**: `( ) ,`.

Per convenzione (nel libro di testo) i simboli di costante, predicato e funzione iniziano con la maiuscola. I simboli di predicato e di funzione hanno un'**arità** fissa (numero di parametri) e ogni simbolo ha un'**interpretazione**.

### Grammatica di FOL

```
formula        → formulaAtomica | (formula connettivo formula)
                 | quantificatore variabile,… formula | ¬ formula
formulaAtomica → predicato(termine, …) | termine = termine
termine        → funzione(termine, …) | costante | variabile
connettivo     → ⇒ | ⇔ | ∧ | ∨
quantificatore → ∀ | ∃
```

### Predicati vs funzioni

Entrambi operano su tuple di oggetti del dominio, ma restituiscono cose diverse:

- **Predicati**: dato un insieme di oggetti, catturano una proprietà e restituiscono **vero/falso**. Esempio: `Uomo(Andrea)`, `Accanto(X, a)`.
- **Funzioni**: dato un insieme di oggetti, restituiscono **un oggetto** del dominio. Esempio: `più(3,5)`, `parent(X)`.

Una relazione, in generale, è un insieme di tuple di oggetti del dominio: ad es. `{ <GiovanniSenzaTerra, RiccardoCuorDiLeone>, <RiccardoCuorDiLeone, GiovanniSenzaTerra> }` rappresenta "chi è fratello di chi".

### Modelli e interpretazione

Un **modello** in FOL è una coppia `M = (D, I)`:

- `D` (dominio del discorso): insieme di ≥ 1 oggetti e delle loro relazioni.
- `I` (interpretazione): associazione fra i simboli del linguaggio e gli elementi/relazioni del dominio:
  - simboli costanti → elementi del dominio;
  - simboli di predicato → relazioni fra elementi del dominio;
  - simboli di funzione → relazioni funzionali fra oggetti del dominio.

Come nella proposizionale, `M` è un modello di `α` se `α` è vera in `M`.

**Un punto sottile ma importante**: il valore di verità di una formula dipende interamente dall'interpretazione scelta.

- Se **cambio coerentemente i nomi dei simboli** (es. `John`→`JohnUsurpatore`, `Richard`→`RichardRe`) ma **mantengo la stessa struttura di interpretazione**, il valore di verità **non cambia**.
- Se invece **cambio l'interpretazione** (es. faccio corrispondere `John` alla "Corona" invece che a Giovanni senza terra), il valore di verità **può cambiare**: `Fratello(John, Richard)` può diventare falsa anche se sintatticamente è la stessa formula di prima.
- Anche cambiare l'interpretazione dei **predicati** (es. `Fratello` come "fratellanza fra monaci" invece che "fratellanza di sangue") cambia il valore di verità.
- Se cambio il **dominio del discorso** stesso, devo necessariamente ridefinire l'interpretazione, e la verità delle formule può cambiare di conseguenza.

In breve: ***una formula FOL non ha un valore di verità assoluto***, lo ha solo relativamente a un modello `(D, I)` fissato. Questo è coerente con l'idea (già vista in proposizionale) che la verità è definita rispetto a un'interpretazione.

### Soddisfacibilità, validità, insoddisfacibilità (richiamo)

- **Soddisfacibile**: esiste almeno un modello che la rende vera.
- **Valida**: vera in tutti i modelli.
- **Insoddisfacibile**: mai vera in nessun modello.

### Quanti modelli ha una KB FOL?

In proposizionale, con N simboli proposizionali, ci sono `2^N` modelli possibili (enumerabili). In FOL la situazione è molto peggiore: bisognerebbe considerare, per ogni possibile cardinalità `n` del dominio (da 1 a ∞), ogni possibile interpretazione di ciascun predicato k-ario su n oggetti, ogni possibile riferimento di ciascuna costante, ecc. — un'enumerazione a più livelli annidati, potenzialmente **infinita**.

> ❓ **Domanda d'esame:** Perché in FOL non si può verificare la conseguenza logica per enumerazione dei modelli, come si faceva in proposizionale?
> **Risposta:** perché se il dominio D è illimitato e una formula contiene quantificatori, per stabilirne il valore di verità servirebbe calcolare il valore di verità di infinite istanze (una per ogni possibile elemento del dominio sostituito alla variabile quantificata). I modelli possibili in FOL possono quindi essere infiniti, e l'enumerazione — strumento che funzionava in proposizionale — smette di essere praticabile. Occorrono altre tecniche di inferenza (regole di inferenza "liftate", risoluzione, ecc., vedi sotto).

## Termini e formule atomiche

Un **termine** è un'espressione che si riferisce a un oggetto del dominio:

```
termine → funzione(termine, …) | costante | variabile
```

- Le **costanti** danno un nome a oggetti specifici e noti.
- Le **funzioni** permettono di riferirsi a oggetti che *non hanno un nome proprio*. Importante: una funzione **non costruisce** l'oggetto restituito, si limita a **riferirlo**. Esempio: `GambaSinistra(John)` è un modo per indicare l'oggetto "gamba sinistra di John" già esistente nel dominio — non serve sapere come sia fatta una gamba per usare questo termine.

**Termine ground**: un termine che non contiene variabili (es. `GambaSinistra(John)`, `Richard`, `Corona`).

**Interpretazione di un termine** (processo ricorsivo):

- se è una costante, l'identificazione con l'oggetto del dominio è immediata;
- se è `f(t1, …, tk)`, prima si interpretano ricorsivamente `t1, …, tk` ottenendo gli oggetti `O1, …, Ok`, poi si applica la funzione `F` (l'interpretazione di `f`) a questi oggetti, ottenendo l'oggetto risultato `O`.

Da notare: l'oggetto `O` (es. "la gamba sinistra di Giovanni") non compare mai esplicitamente nelle formule con un proprio nome, ma esiste comunque nel dominio e viene "raggiunto" passando attraverso il termine funzionale.

**Formula atomica**:

```
formulaAtomica → predicato(termine, …) | termine = termine
```

È vera quando, dato un modello con una certa interpretazione, la relazione denotata dal predicato è verificata dagli oggetti denotati dai termini. Esempi:

- `sposato(madre(Richard), padre(John))`
- `padre(Richard) = padre(John)`

**Formule complesse** si ottengono componendo formule atomiche con i connettivi, come in proposizionale:

- `Re(John) ⇒ ¬Re(Richard)`
- `Persona(X) ∧ SullaTesta(Corona, X) ⇒ Re(X)`

## Quantificatori

I quantificatori permettono di esprimere proprietà su **collezioni** di oggetti, facendo riferimento a oggetti generici tramite variabili (es. "tutti gli uomini" diventa "tutti gli X che sono uomini").

- `∀`: quantificatore **universale** ("per ogni")
- `∃`: quantificatore **esistenziale** ("esiste")

### Quantificatore universale ∀

**Semantica**: dati una formula `F` e un modello `M = (D, I)`, l'espressione `∀x F` è vera in `M` se e solo se `F` è vera per **qualsiasi** interpretazione di `x` in `M` (cioè per ogni oggetto del dominio sostituito a `x`, senza filtri di "tipo").

**Forma generale**: `∀ ⟨variabili⟩ ⟨formula⟩`

**Esempio**: "Al corso di sistemi intelligenti tutti sono intelligenti":

```
∀x Partecipa(x, SISINT) ⇒ Intelligente(x)
```

Concettualmente questa formula si può "espandere" (se il dominio fosse finito) in una **congiunzione**:

```
(Partecipa(Miriam, SISINT) ⇒ Intelligente(Miriam)) ∧
(Partecipa(Matteo, SISINT) ⇒ Intelligente(Matteo)) ∧ … 
```

per ogni oggetto del dominio, non solo per gli studenti.

### Quantificatore esistenziale ∃

**Semantica**: `∃x F` è vera in `M` se e solo se `F` è vera per **almeno una** (qualche) interpretazione di `x` in `M`.

**Forma generale**: `∃ ⟨variabili⟩ ⟨formula⟩`

**Esempio**: "Al corso di sistemi intelligenti qualcuno è intelligente":

```
∃x Partecipa(x, SISINT) ∧ Intelligente(x)
```

Si espande in una **disgiunzione**:

```
(Partecipa(Miriam, SISINT) ∧ Intelligente(Miriam)) ∨
(Partecipa(Matteo, SISINT) ∧ Intelligente(Matteo)) ∨ …
```

### Regola pratica: ∀ va con ⇒, ∃ va con ∧

Questo è uno dei punti in cui si commettono più errori. Le slide lo mostrano esplicitamente con un confronto:

> ❓ **Domanda d'esame:** Che differenza c'è fra `∀x Partecipa(x, SISINT) ⇒ Intelligente(x)` e `∀x Partecipa(x, SISINT) ∧ Intelligente(x)`? Sono equivalenti?
> **Risposta: NO.**
> 1. `∀x Partecipa(x, SISINT) ⇒ Intelligente(x)` significa "tutti quelli che partecipano a SISINT sono intelligenti" — l'implicazione filtra correttamente solo i partecipanti, gli altri oggetti del dominio rendono vera l'implicazione per vacuità (antecedente falso).
> 2. `∀x Partecipa(x, SISINT) ∧ Intelligente(x)` significa "tutti (ogni oggetto del dominio, comprese sedie e numeri) partecipano a SISINT E sono intelligenti" — affermazione quasi certamente falsa e comunque non quella voluta.
>
> **Motivo strutturale**: con `∀` la formula è valutata per *ogni* oggetto del dominio; usare `∧` costringe *ogni* oggetto a soddisfare entrambe le condizioni, mentre di solito si vuole restringere il discorso a una sottoclasse (i partecipanti) — e questo si ottiene con l'implicazione, che è vera automaticamente quando l'oggetto non è nella sottoclasse.

> ❓ **Domanda d'esame:** E per `∃x Partecipa(x, SISINT) ⇒ Intelligente(x)` vs `∃x Partecipa(x, SISINT) ∧ Intelligente(x)`? Sono equivalenti?
> **Risposta: NO, e qui l'errore è ancora più insidioso.**
> 1. `∃x Partecipa(x,SISINT) ⇒ Intelligente(x)` è equivalente (per la legge `A⇒B ≡ ¬A∨B`) a `∃x ¬Partecipa(x,SISINT) ∨ Intelligente(x)`: basta che esista **un solo oggetto qualsiasi** che *non* partecipa al corso (es. una sedia) per rendere vera la formula, indipendentemente da chi sia intelligente! Questa formula quindi **non cattura l'intento** di "esiste qualcuno intelligente fra i partecipanti".
> 2. `∃x Partecipa(x,SISINT) ∧ Intelligente(x)` invece dice correttamente "esiste (almeno) un partecipante a SISINT che è intelligente" — questa è la traduzione corretta dell'intento.
>
> **Conclusione pratica**: quando si traduce dal linguaggio naturale, usare ***`∀ ... ⇒ ...`*** per affermazioni universali su una sottoclasse, e ***`∃ ... ∧ ...`*** per affermazioni esistenziali su una sottoclasse. Usare `∀` con `∧` o `∃` con `⇒` produce quasi sempre formule sbagliate o triviali.

### Quantificatori annidati: l'ordine conta

Regole di equivalenza per quantificatori dello stesso tipo (commutano liberamente fra loro):

1. `∃x ∃y F ≡ ∃y ∃x F` (si scrive anche `∃x,y F`)
2. `∀x ∀y F ≡ ∀y ∀x F` (si scrive anche `∀x,y F`)

Ma **quantificatori di tipo diverso NON commutano**:

3. `∀x ∃y F`: "per ogni x esiste un y (che può dipendere da x)". Esempio: `∀x ∃y Ama(x,y)` = "tutti amano qualcuno (potenzialmente un qualcuno diverso per ciascuno)".
4. `∃y ∀x F`: "esiste un y (fisso) tale che vale per tutti gli x". Esempio: `∃y ∀x Ama(x,y)` = "esiste qualcuno (uno specifico) che è amato da tutti".

> ❓ **Domanda d'esame:** Perché `∀x ∃y Ama(x,y)` e `∃y ∀x Ama(x,y)` non sono equivalenti?
> **Risposta:** nel primo caso ogni `x` può scegliere un `y` diverso (ognuno ama qualcuno, magari persone diverse); nel secondo caso esiste un **singolo** oggetto `y`, fissato una volta per tutte, che soddisfa la relazione con *ogni* `x` (una sola persona amata da tutti). La seconda formula è molto più forte e implica la prima, ma non viceversa. L'ordine di annidamento dei quantificatori determina quindi la "portata" (scope) delle dipendenze fra variabili: la variabile quantificata più esternamente è fissata prima, quella più interna può dipendere dalla precedente. Questo concetto tornerà cruciale nella **skolemizzazione**.

### Quantificatori e negazione (leggi di De Morgan generalizzate)

1. `∀x ¬F ≡ ¬∃x F` — "a nessuno piace il cavolfiore" ≡ "non esiste nessuno a cui piaccia il cavolfiore"
2. `∃x ¬F ≡ ¬∀x F` — "c'è qualcuno a cui non piace il cavolfiore" ≡ "non è vero che piace a tutti"
3. `∀x F ≡ ¬∃x ¬F` — "per tutti vale F" ≡ "non esiste nessuno per cui non vale F"
4. `∃x F ≡ ¬∀x ¬F` — "c'è qualcuno per cui vale F" ≡ "non è vero che per tutti non vale F"

In pratica, `∀` e `∃` sono duali fra loro esattamente come `∧` e `∨` lo sono rispetto alla negazione in proposizionale.

### Uguaglianza e quantificatori

L'**uguaglianza** (`=`) riguarda esclusivamente **termini** (oggetti), non formule.

Problema tipico: come esprimere "John ha almeno due fratelli"?

- **Tentativo sbagliato**: `∃y,z Fratello(John,y) ∧ Fratello(John,z)` — **non basta**, perché è soddisfatta anche se `y` e `z` vengono unificati con lo stesso oggetto (es. entrambi con `Richard`).
- **Correzione**: bisogna imporre esplicitamente che `y` e `z` si riferiscano a oggetti diversi:
  ```
  ∃y,z Fratello(John,y) ∧ Fratello(John,z) ∧ ¬(y=z)
  ```

### Il problema dell'unicità dei nomi

Consideriamo l'asserzione `Fratello(John,Richard) ∧ Fratello(John,Ramon)`. Intuitivamente sembra dire che John ha due fratelli, ma **nella semantica standard di FOL** è soddisfatta anche se `Richard` e `Ramon` sono due nomi diversi per la **stessa persona**! Per escluderlo servirebbe aggiungere `¬(Richard=Ramon)`. E se volessimo dire che John ha *esattamente* due fratelli (non di più), servirebbe anche:

```
∀x (Fratello(John,x) ⇒ (x=Richard ∨ x=Ramon))
```

Il risultato è corretto ma **le formule diventano rapidamente complicatissime e poco intuitive**.

### Database semantics (semantica alternativa più intuitiva)

Per evitare queste complicazioni, la programmazione logica adotta spesso la **database semantics**, basata su tre assunzioni:

1. **Unicità dei nomi (Unique Names Assumption)**: costanti diverse denotano sempre oggetti diversi.
2. **Closed-world assumption**: le formule atomiche di verità sconosciuta sono considerate false.
3. **Domain closure**: il modello non contiene più oggetti di quelli nominati dalle costanti presenti.

Con questa semantica, semplicemente `Fratello(John,Richard) ∧ Fratello(John,Ramon)` rappresenta correttamente "John ha (esattamente) due fratelli, Richard e Ramon" — molto più intuitivo. Riduce anche il numero di modelli possibili, rendendoli tipicamente finiti.

> Nota importante per l'esame: **il libro di testo (Russell & Norvig) usa la semantica standard di FOL** anche dopo aver introdotto la database semantics — quest'ultima è tipica di Prolog/programmazione logica, va tenuta distinta e usata solo quando siamo certi dell'identità di tutti gli elementi del dominio.

## Inferenza in FOL: due approcci

1. **Proposizionalizzazione** della KB e uso di un algoritmo per la logica proposizionale.
2. **Lifting** delle regole di inferenza al prim'ordine (con unificazione) — l'approccio più efficiente ed usato in pratica.

### Interrogare una KB FOL

Due tipi di query:

- `ask(KB, Re(John))`: formula **ground** (senza variabili) — risposta `true`/`false`.
- `ask(KB, Re(x))`: formula con variabile libera — risposta `false` se non esiste alcun valore che renda vera la formula, altrimenti un **termine ground** che, sostituito a `x`, la rende vera.

### Sostituzione

Una **sostituzione** `θ` è un insieme `{x1/g1, x2/g2, …, xn/gn}` dove le `xi` sono variabili e le `gi` sono termini ground. La notazione `F/θ` (o `Fθ`) indica la formula ottenuta applicando `θ` a `F`.

Esempio: `F = Fratello(x,y)`, `θ = {x/John}` ⟹ `Fθ = Fratello(John, y)`.

### Proposizionalizzazione: UI ed EI

**Regola di istanziazione universale (UI)**:

```
     ∀x α
—————————————
 SUBST({x/g}, α)
```

Da una formula universalmente quantificata si può inferire qualunque istanza ottenuta sostituendo alla variabile un **qualsiasi termine ground** del vocabolario. Esempio: da `∀x (Partecipa(x,SISINT) ⇒ Intelligente(x))`, con `θ1={x/Rufus}` si inferisce `Partecipa(Rufus,SISINT) ⇒ Intelligente(Rufus)`.

**Regola di istanziazione esistenziale (EI)**:

```
     ∃x α
—————————————
 SUBST({x/k}, α)
```

dove `k` deve essere una **costante nuova** (non ancora usata nella KB). Esempio: da `∃x Corona(x) ∧ SullaTesta(x,John)` si inferisce `Corona(C1) ∧ SullaTesta(C1,John)`, con `C1` costante nuova generata appositamente — questo processo di generare un nome nuovo si chiama **skolemizzazione** (le costanti così introdotte sono dette **costanti di Skolem**).

**Differenza fondamentale fra UI ed EI**:

- **UI**: produce tutte le istanze possibili; la nuova KB è **logicamente equivalente** a quella originaria.
- **EI**: si applica **una sola volta** per ciascuna formula esistenziale e poi la formula quantificata viene scartata; la nuova KB **non** è logicamente equivalente all'originaria, ma è **soddisfacibile se e solo se** lo era la KB originaria (equivalenza *inferenziale*, non logica).

### Il problema delle funzioni e il teorema di Herbrand

Se il vocabolario contiene funzioni, esse possono essere annidate ricorsivamente (`f(f(f(…x…)))`), quindi l'insieme dei possibili termini ground — e delle sostituzioni possibili per UI — diventa **potenzialmente infinito**.

**Teorema di Herbrand**: se una formula è conseguenza logica della KB FOL originaria, allora esiste una dimostrazione **finita** della sua verità a partire dalla KB proposizionalizzata. I termini vengono costruiti "in ampiezza" (breadth-first): prima le sole costanti, poi i termini con una sola applicazione di funzione, poi quelli con due applicazioni, ecc.

**Conseguenza — semidecidibilità di FOL**:

- **Completezza**: se una formula consegue dalla KB, la si troverà (dimostrazione finita, per Herbrand).
- Ma se la conseguenza **non** vale, la ricerca (a causa delle funzioni ricorsive) può proseguire **all'infinito** senza mai terminare.
- Quindi: non esiste un algoritmo generale in grado di dimostrare che una conseguenza *non* vale in FOL. FOL è ***semidecidibile*** (si può confermare il "sì" ma non sempre il "no").

### Inefficienza della proposizionalizzazione

Esempio:
```
∀x Re(x) ∧ Avido(x) ⇒ Malvagio(x)
Re(John)
Avido(John)
Fratello(Richard, John)
```
La proposizionalizzazione genera un'istanza dell'implicazione **per ogni costante del vocabolario**, incluso `Re(Richard) ∧ Avido(Richard) ⇒ Malvagio(Richard)`, anche se è ovvio a colpo d'occhio che solo `John` può risultare malvagio. Si "spreca tempo" a creare istanze inutili — tanto più gravoso quanto più il vocabolario è ampio (e peggio ancora se sono presenti variabili universali multiple, come `∀y Avido(y)`, che moltiplicano ulteriormente le istanze inutili).

Questo motiva il passaggio a regole di inferenza **"liftate"** direttamente al prim'ordine, che evitano l'esplosione combinatoria della proposizionalizzazione.

## Modus Ponens Generalizzato (MPG)

### Formula

```
p'1, p'2, …, p'n,   (p1 ∧ p2 ∧ … ∧ pn ⇒ q)
———————————————————————————————————————————
                    qθ
```

dove `p'i θ = pi θ` per ogni `i ∈ [1,n]`.

**Spiegazione**: la regola ha come premesse `n` formule atomiche `p'1, …, p'n` e una singola implicazione la cui antecedente è la congiunzione `p1 ∧ … ∧ pn`. Se esiste una sostituzione `θ` tale che ciascuna `p'i` unifica con la corrispondente `pi` (cioè `p'iθ = piθ`), allora si può concludere `qθ`, cioè la conseguenza dell'implicazione con `θ` applicata.

`qθ` è la notazione sintetica per `SUBST(θ, q)`.

### Esempio

Premesse: `Re(John)`, `Avido(y)`, `Re(x) ∧ Avido(x) ⇒ Malvagio(x)`.

Per applicare MPG serve unificare `Re(John)` con `Re(x)` (dando `x/John`) e `Avido(y)` con `Avido(x)` (dando `y/x`, e con `x/John` ottenuto sopra, quindi `y/John`). La sostituzione complessiva è `θ = {x/John, y/John}`, e si conclude:

```
Malvagio(John)
```

Le clausole guidano quindi la **ricerca della sostituzione** giusta, e permettono di ragionare **direttamente in FOL** senza passare per l'espansione esaustiva di tutte le costanti del vocabolario (a differenza della proposizionalizzazione).

### Lifting

Il modus ponens proposizionale non pone restrizioni sulla forma della formula antecedente. Il ***Modus Ponens Generalizzato*** invece richiede che l'antecedente sia una ***congiunzione di letterali positivi***, e generalizza la regola:

- consentendo un numero arbitrario di premesse atomiche (non solo due, come nel modus ponens classico);
- operando su formule con **variabili**, tramite unificazione.

Il termine "generalizzato" deriva proprio dall'aver "sollevato" (**lifted**) la regola dalla logica proposizionale a quella del prim'ordine — questo procedimento generale si chiama **lifting** e verrà applicato anche alla risoluzione (vedi sotto).

## Unificazione

**Definizione**: l'unificazione è l'algoritmo chiave di tutte le tecniche di inferenza in FOL. Date due formule `F1` e `F2`:

```
UNIFY(F1, F2) = θ   tale che   F1θ = F2θ
```

Il risultato è una sostituzione `θ` che, applicata a entrambe le formule, le rende **sintatticamente identiche**. Tale sostituzione, se esiste, è detta **unificatore**. Se ne esistono più di una, si preferisce calcolare e usare il **Most General Unifier (MGU)**, l'unificatore più generale (quello che vincola meno le variabili, lasciando aperte più possibilità).

### Esempi passo-passo

1. `UNIFY(Conosce(John,x), Conosce(John,Richard))`:
   `John` coincide già; `x` deve unificare con `Richard` ⟹ `θ = {x/Richard}`.

2. `UNIFY(Conosce(John,x), Conosce(y,Richard))`:
   `John` deve unificare con `y`; `x` deve unificare con `Richard` ⟹ `θ = {x/Richard, y/John}`.

3. `UNIFY(Conosce(John,x), Conosce(y,MadreDi(y)))`:
   `John` unifica con `y` ⟹ `y/John`; sostituendo nel secondo termine, `x` deve unificare con `MadreDi(y)` che con `y/John` diventa `MadreDi(John)` ⟹ `θ = {x/MadreDi(John), y/John}`.

4. `UNIFY(Conosce(John,x), Conosce(x,Richard))`:
   **fallisce**, perché la stessa variabile `x` dovrebbe assumere contemporaneamente due valori diversi (`John` a sinistra, `Richard` a destra) — è un conflitto di occorrenza/legame.
   Per evitare questo tipo di collisioni accidentali fra variabili di formule diverse, si applica la **standardizzazione separata** (*standardizing apart*): si rinominano le variabili di una formula in modo che non collidano mai con quelle di un'altra formula prima di tentare l'unificazione.

## Clausole di Horn del prim'ordine

Analoghe a quelle proposizionali: sono disgiunzioni di letterali di cui **al più uno è positivo**. In pratica, nella pratica di modellazione:

- **Formule atomiche** (fatti): es. `Avido(x)` (variabile intesa universalmente quantificata), oppure `Avido(John)` (fatto ground).
- **Implicazioni** il cui antecedente è una congiunzione di letterali positivi: `Re(x) ∧ Avido(x) ⇒ Malvagio(x)`.

Non tutte le KB sono traducibili in clausole di Horn, ma molte lo sono — e a queste si può applicare il **forward chaining** (con MPG) per fare inferenza.

### KB di esempio: "Sotto Casa"

Enunciato: *"La legge dice che è un reato per un negozio vendere alcolici a un minorenne. Marco, minorenne, possiede della birra. Tale birra gli è stata venduta dal minimarket Sotto Casa."* Obiettivo: dimostrare che Sotto Casa è reo.

Vocabolario:

- Costanti: `Marco`, `SottoCasa`
- Predicati: `Vende` (ternario), `Negozio`, `Supermarket`, `Birra`, `Alcolico`, `Minorenne`, `Possiede`, `Reo`
- Funzioni: nessuna

Formalizzazione:

```
C1) Negozio(x) ∧ Vende(x,y,z) ∧ Alcolico(y) ∧ Minorenne(z) ⇒ Reo(x)
```
("è un reato per un negozio vendere alcolici a un minorenne")

```
∃x Possiede(Marco,x) ∧ Birra(x)
```
("Marco possiede della birra") — applicando **EI**, si introduce la costante di Skolem `B` ("la birra"):
```
C2) Possiede(Marco, B)
C3) Birra(B)
```

```
C4) Possiede(Marco,x) ∧ Birra(x) ⇒ Vende(SottoCasa,x,Marco)
```
("se Marco possiede della birra, l'ha comprata al minimarket")

```
C5) Birra(x) ⇒ Alcolico(x)
```
("la birra è un alcolico")

```
C6) Minimarket(SottoCasa)
C7) Minimarket(x) ⇒ Negozio(x)
C8) Minorenne(Marco)
```

Questa KB è composta da clausole di Horn del prim'ordine **senza funzioni**: questa particolare sottoclasse (Horn + no funzioni) è chiamata **DATALOG**.

> Nota (citazione da slide, statistico George Box): "tutti i modelli sono sbagliati, alcuni sono utili" — la modellazione in clausole di Horn qui proposta non è l'unica possibile, ma è una semplificazione utile.

### Forward Chaining in FOL

L'algoritmo è concettualmente simile al caso proposizionale, ma richiede cautele aggiuntive per via delle variabili:

- Un fatto è considerato una **rinomina** di un altro se sono identici a meno dei nomi delle variabili (es. `Fratello(John,x)` e `Fratello(John,y)` sono rinomine l'uno dell'altro).
- In proposizionale un fatto inferito si aggiunge alla KB solo se non è già presente; in FOL si aggiunge solo se **non è una rinomina** di un fatto già presente.

**Esempio (continuazione KB Sotto Casa)**: da `C2, C3, C4` si applica MPG unificando `x` con `B` (`θ = {x/B}`), ottenendo:
```
Vende(SottoCasa, B, Marco)
```
Il processo continua costruendo un **grafo AND-OR**: si combina con `C5` per ottenere `Alcolico(B)`, con `C6`/`C7` per ottenere `Negozio(SottoCasa)`, con `C8` (`Minorenne(Marco)`) e infine con `C1` (unificando `x/SottoCasa, y/B, z/Marco`) si conclude:
```
Reo(SottoCasa)
```

Punto chiave: **non si propagano solo valori di verità** (come in proposizionale) ma anche **le sostituzioni**, che fanno da collante fra le diverse applicazioni successive di MPG lungo il grafo di inferenza.

**Proprietà**:

- **Correttezza**: garantita, perché si basa sulla regola di inferenza corretta (MPG, *Generalized Modus Ponens*).
- **Completezza**: se la KB è DATALOG (Horn, senza funzioni), l'algoritmo è completo e **termina**. Se la KB contiene funzioni, per il teorema di Herbrand l'algoritmo può **non terminare** se la risposta cercata non è implicata dalla KB.

### Backward Chaining (BC) in FOL

Come nel caso proposizionale, il ragionamento è **guidato dall'obiettivo** (goal-driven):

1. L'obiettivo viene inserito in uno **stack**.
2. Iterativamente si estrae un obiettivo dallo stack e si cercano clausole la cui **testa** (conseguente) sia **unificabile** con l'obiettivo:
   - se l'obiettivo unifica con un **fatto** (clausola a corpo vuoto), viene semplicemente rimosso (risolto);
   - altrimenti, per ogni clausola applicabile si avvia un procedimento **ricorsivo** che inserisce nello stack le premesse della clausola (con le variabili opportunamente sostituite secondo l'unificatore trovato).
3. Quando lo stack è vuoto: **successo**. Se non si possono applicare altre inferenze: **fallimento**.

**Esempio (KB Sotto Casa), traccia sintetica**:

- Stack iniziale: `Reo(SottoCasa)`.
- Unifica con la testa di `C1` (`θ1={x/SottoCasa}`) ⟹ Stack: `Negozio(SottoCasa), Vende(SottoCasa,y,z), Alcolico(y), Minorenne(z)`.
- `Negozio(SottoCasa)` unifica con la testa di una clausola tipo `Supermarket(x) ⇒ Negozio(x)`, che a sua volta si risolve con il fatto `Supermarket(SottoCasa)` (analogo a `C6`/`C7`).
- `Alcolico(y)` unifica con la testa di `C5` (`Birra(x) ⇒ Alcolico(x)`, con `θ2={y/x}`), che si risolve con `C3) Birra(B)` (`θ2={x/B}`).
- `Vende(SottoCasa,y,z)` (con `y` ormai legata a `B`) unifica con la testa di `C4`, che genera i sotto-obiettivi risolti da `C2) Possiede(Marco,B)` e `C3) Birra(B)`.
- `Minorenne(z)` (con `z` legata a `Marco` tramite le sostituzioni composte) unifica con il fatto `C8) Minorenne(Marco)`.
- Stack vuoto ⟹ **successo**, `Reo(SottoCasa)` dimostrato.

**Composizione delle sostituzioni**: l'algoritmo BC applica ripetutamente la composizione `COMPOSE(θ1,θ2) = θ3`, con la proprietà:
```
SUBST(COMPOSE(θ1,θ2), F) = SUBST(θ2, SUBST(θ1, F))
```
cioè applicare la sostituzione composta equivale ad applicare prima `θ1` e poi `θ2` in sequenza. È necessario concatenare correttamente le sostituzioni via via trovate lungo la catena di risoluzione degli obiettivi per ottenere l'inferenza corretta finale.

**Valutazione di BC**:

- **Corretto**.
- **Incompleto**, perché implementa una strategia depth-first: può incorrere in **loop infiniti** e generare stati ripetuti.
- Come nel caso proposizionale, è generalmente **più efficiente** del forward chaining (perché esplora solo ciò che serve a dimostrare l'obiettivo, non tutte le conseguenze possibili della KB).

## Risoluzione in FOL: lifting e refutazione

Nel caso proposizionale, la regola di **risoluzione** unita all'algoritmo di **refutazione** costituisce una procedura di inferenza **completa** (vedi Modulo 5). Questa combinazione può essere "liftata" (sollevata) anche a FOL:

- La KB va tradotta in **CNF** (Conjunctive Normal Form: congiunzione di clausole, ciascuna disgiunzione di letterali).
- Le variabili nelle clausole sono intese **implicitamente quantificate universalmente**.
- Ogni KB FOL può essere tradotta in una KB CNF **inferenzialmente equivalente**: la CNF è insoddisfacibile se e solo se lo è la KB FOL originaria. Questo è ciò che rende lecita l'applicazione della procedura di refutazione.

### Procedura per tradurre FOL in CNF

Esempio guida: `∀x [∀y Animale(y) ⇒ Ama(x,y)] ⇒ [∃y Ama(y,x)]` ("tutti coloro che amano gli animali sono amati da qualcuno").

**Passo 1 — Elimina l'implicazione** (`A⇒B ≡ ¬A∨B`):
```
∀x ¬[∀y Animale(y) ⇒ Ama(x,y)] ∨ [∃y Ama(y,x)]
∀x ¬[∀y ¬Animale(y) ∨ Ama(x,y)] ∨ [∃y Ama(y,x)]
```

**Passo 2 — Sposta la negazione all'interno** (usando `¬∀ ≡ ∃¬` e De Morgan):
```
∀x [∃y Animale(y) ∧ ¬Ama(x,y)] ∨ [∃y Ama(y,x)]
```

**Passo 3 — Standardizzazione delle variabili**: le due occorrenze di `∃y` sono variabili quantificate indipendenti (scope diversi), vanno rinominate per evitare ambiguità:
```
∀x [∃y Animale(y) ∧ ¬Ama(x,y)] ∨ [∃z Ama(z,x)]
```

**Passo 4 — Skolemizzazione** (vedi sezione dedicata sotto): elimina i quantificatori esistenziali.

**Passo 5 — Cancella i quantificatori universali** (rimasti impliciti, dato che in CNF tutte le variabili libere si intendono universali).

**Passo 6 — Distribuisci `∨` su `∧`** per ottenere la forma a clausole (congiunzione di disgiunzioni).

Il risultato finale non è pensato per essere leggibile da un umano, ma per essere processato automaticamente da un algoritmo di inferenza.

## Skolemizzazione

### Perché serve

Al passo 4 sopra, non si può applicare direttamente la regola EI (istanziazione esistenziale con una singola costante) perché la formula non ha la forma semplice `∃x F(x)`: l'esistenziale è annidato dentro lo scope di un quantificatore universale (`∀x [∃y …]`).

Se, sbagliando, si sostituisse `∃y Animale(y)` con una singola costante `A` (come farebbe EI ingenuamente), si otterrebbe:
```
∀x [Animale(A) ∧ ¬Ama(x,A)] ∨ [Ama(B,x)]
```
che significa "**tutti** amano uno **stesso specifico** animale `A`" e "sono amati da uno **stesso specifico** essere `B`" — `A` e `B` sarebbero costanti fisse, uguali per ogni `x`. Questo è **sbagliato**: l'animale amato o l'amante possono variare da persona a persona.

### Procedura (regola generale)

Si sostituisce ogni variabile quantificata esistenzialmente con una ***funzione di Skolem*** i cui argomenti sono **tutte le variabili universalmente quantificate nel cui scope ricade** l'esistenziale:

```
∀x1,x2,... [∃y P(y,x1,...) … ∃z Q(z,x1,...)]
          diventa
∀x1,x2,... [P(S1(x1,x2,…),...) … Q(S2(x1,x2,…),...)]
```

`S1`, `S2` sono dette **funzioni di Skolem**.

**Caso particolare**: se l'esistenziale **non** ricade nello scope di alcun universale, la funzione di Skolem degenera in una **costante di Skolem** (è esattamente il caso della regola EI vista prima, con la costante `B`/`C1` nell'esempio "Sotto Casa" — lì infatti non c'era nessun `∀` esterno a `∃x Possiede(Marco,x) ∧ Birra(x)`).

**Applicando la regola all'esempio guida**: le variabili esistenziali `y` e `z` ricadono entrambe nello scope di `∀x`, quindi diventano funzioni di `x`:
```
∀x [Animale(F(x)) ∧ ¬Ama(x,F(x))] ∨ [Ama(G(x),x)]
```

Dopo la skolemizzazione si completano i passi 5 e 6 (elimina `∀` residui, distribuisci `∨` su `∧`):
```
[Animale(F(x)) ∨ Ama(G(x),x)] ∧ [¬Ama(x,F(x)) ∨ Ama(G(x),x)]
```

### Esempio più semplice, passo-passo (per fissare l'intuizione)

Consideriamo: `∀x ∃y persona(x) ⇒ (abita(x,y) ∧ paese(y))` ("ogni persona abita in un luogo che è in un paese").

**Errore da non fare**: applicare EI ingenuamente eliminerebbe `∃y` con una singola costante `K`:
```
∀x persona(x) ⇒ (abita(x,K) ∧ paese(K))
```
Questo fissa **un'unica costante K uguale per tutti gli x**, cioè affermerebbe che **tutte le persone abitano nello stesso posto** — chiaramente sbagliato: persone diverse possono abitare in paesi diversi (o anche nello stesso paese, ma non è imposto che sia sempre lo stesso).

**Soluzione corretta**: il luogo in cui una persona abita **dipende** (è funzione) dallo specifico individuo, quindi si introduce una funzione di Skolem `luogo(x)`:
```
∀x persona(x) ⇒ (abita(x, luogo(x)) ∧ paese(luogo(x)))
```
Ora il luogo può variare correttamente da persona a persona.

### Funzioni di Skolem con più argomenti

Le funzioni di Skolem hanno come argomenti **tutte** le variabili universali nel cui scope ricadono, quindi possono avere arità > 1. Esempio: in un rally, per ogni coppia di persone `x, y` esiste un'auto `z` di cui `x` è il pilota e `y` il navigatore:

```
∀x,y ∃z persona(x) ∧ persona(y) ∧ auto(z) ∧ ¬(x=y) ⇒ (pilota(x,z) ∧ navigatore(y,z))
```

Skolemizzando (`z` dipende sia da `x` che da `y`, quindi funzione a due argomenti `A(x,y)`):

```
∀x,y persona(x) ∧ persona(y) ∧ auto(A(x,y)) ∧ ¬(x=y) ⇒ (pilota(x,A(x,y)) ∧ navigatore(y,A(x,y)))
```

### Caso limite: l'esistenziale "esterno" a tutti gli universali

Attenzione allo **scope**: le funzioni di Skolem dipendono dalle variabili universali nel cui scope ricade l'esistenziale, e lo scope dipende dall'**ordine di annidamento**, non dall'ordine di scrittura sulla carta.

- Se la formula è `∀x,y ∃z formula(x,y,z)`: `z` è dentro lo scope di `x` e `y` ⟹ funzione di Skolem `S(x,y)` con 2 argomenti.
- Se la formula è invece `∃z [∀x,y formula(x,y,z)]`: qui è `∃z` a essere **più esterno**, quindi sono `x` e `y` a ricadere nello scope dell'esistenziale (e non viceversa!) — la formula dice che esiste un **unico** valore di `z` che vale per *tutti* i possibili `x,y`. In questo caso la funzione di Skolem **non ha argomenti**, cioè degenera in una **costante di Skolem** (si applica l'istanziazione esistenziale semplice, EI), esattamente come accadrebbe per la formula ancora più semplice `∃z formula(x,y,…,z)` priva di universali che la "contengono".

> ❓ **Domanda d'esame:** Da cosa dipendono gli argomenti di una funzione di Skolem, e perché a volte si riduce a una costante?
> **Risposta:** gli argomenti sono esattamente le variabili quantificate universalmente il cui scope contiene (racchiude) il quantificatore esistenziale da eliminare — perché il valore "esistente" può, in linea di principio, variare al variare di quelle variabili universali già fissate più esternamente. Se non ci sono variabili universali che "contengono" l'esistenziale (l'esistenziale è il quantificatore più esterno, o comunque non è annidato dentro nessun `∀`), allora il valore esistente è **unico e fisso**, non dipende da nulla, e la funzione di Skolem degenera in una semplice **costante di Skolem** — esattamente il caso della regola EI.

## Binary resolution in FOL (lifting della risoluzione)

Formula generale (risoluzione binaria liftata):

```
     l1 ∨ … ∨ lk,   m1 ∨ … ∨ mn
—————————————————————————————————————————————————
 SUBST(θ, l1∨…∨li-1∨li+1∨…∨lk∨m1∨…∨mj-1∨mj+1∨…∨mn)
```

dove `θ` è una sostituzione tale che, per una coppia di indici `i,j`, `θ` **unifica** `li` con `¬mj` (cioè rende `li` e la negazione di `mj` sintatticamente identici).

**Esempio**: `Re(John)` e `¬Re(x)` sono "opposte"; la sostituzione `θ={x/John}` rende `Re(John)θ ≡ ¬¬Re(x)θ`, quindi le due clausole risolvono fra loro eliminando questi due letterali.

Osservazioni tecniche:

- Le due clausole da risolvere **non devono condividere variabili** (da qui la necessità della standardizzazione separata, come nell'unificazione).
- Va fatto anche il lifting della **fattorizzazione**: due letterali di una stessa clausola si riducono a uno solo non se sono sintatticamente uguali, ma se sono **unificabili** — e l'unificatore trovato va applicato all'**intera clausola**.
- **Binary resolution + fattorizzazione** insieme costituiscono una regola di inferenza **completa**.

### Dimostrazione per refutazione: l'esempio "Curiosity ha ucciso il gatto?"

Grazie al lifting della risoluzione, si può applicare la procedura di **refutazione** anche a FOL. Esempio classico:

- A) Tutti coloro che amano gli animali sono amati da qualcuno.
- B) Tutti coloro che uccidono un animale non sono amati da nessuno.
- C) Jack ama tutti gli animali.
- D) O Jack o Curiosity ha ucciso il gatto, il cui nome è Tuna.
- E) Gatto(Tuna).
- F) Tutti i gatti sono animali.

Query: **Curiosity ha ucciso il gatto?**

Formalizzazione FOL:
```
A) ∀x [∀y Animale(y) ⇒ Ama(x,y)] ⇒ [∃y Ama(y,x)]
B) ∀x [∃z Animale(z) ∧ Uccide(x,z)] ⇒ [∀y ¬Ama(y,x)]
C) ∀x Animale(x) ⇒ Ama(Jack,x)
D) Uccide(Jack,Tuna) ∨ Uccide(Curiosity,Tuna)
E) Gatto(Tuna)
F) ∀x Gatto(x) ⇒ Animale(x)
```

Per dimostrare per **refutazione** che la risposta è "sì", si aggiunge il **goal negato**:
```
G) ¬Uccide(Curiosity,Tuna)
```
e si cerca di derivare una contraddizione (clausola vuota) da `KB ∧ ¬Q`. Se ci si riesce, allora `KB ⊨ Q`.

**Traduzione in CNF** (applicando i 6 passi visti sopra, con skolemizzazione dove serve — nella formula A l'esistenziale `∃y` dipende da `x`, quindi diventa funzione di Skolem `G(x)`; analogamente in B `∃z` diventa `F(x)`):

```
A1) Animale(F(x)) ∨ Ama(G(x),x)
A2) ¬Ama(x,F(x)) ∨ Ama(G(x),x)
B)  ¬Ama(y,x) ∨ ¬Animale(z) ∨ ¬Uccide(x,z)
C)  ¬Animale(x) ∨ Ama(Jack,x)
D)  Uccide(Jack,Tuna) ∨ Uccide(Curiosity,Tuna)
E)  Gatto(Tuna)
F)  ¬Gatto(x) ∨ Animale(x)
G)  ¬Uccide(Curiosity,Tuna)
```

**Catena di risoluzione** (schema concettuale, unificando via via le variabili con le costanti opportune):

1. `E) Gatto(Tuna)` risolve con `F) ¬Gatto(x)∨Animale(x)` (unificando `x/Tuna`) ⟹ `Animale(Tuna)`.
2. `D) Uccide(Jack,Tuna)∨Uccide(Curiosity,Tuna)` risolve con `G) ¬Uccide(Curiosity,Tuna)` ⟹ `Uccide(Jack,Tuna)`.
3. `Animale(Tuna)` risolve con `B) ¬Ama(y,x)∨¬Animale(z)∨¬Uccide(x,z)` (unificando `z/Tuna`) ⟹ `¬Ama(y,x)∨¬Uccide(x,Tuna)`.
4. Questa risolve con `Uccide(Jack,Tuna)` (unificando `x/Jack`) ⟹ `¬Ama(y,Jack)`.
5. `¬Ama(y,Jack)` risolve con `A2) ¬Ama(x,F(x))∨Ama(G(x),x)` (unificando `y/Jack` da un lato e cercando di far coincidere `Jack` con `F(x)`... nello sviluppo delle slide, la catena prosegue unificando opportunamente fino a produrre `¬Animale(F(Jack))∨Ama(G(Jack),Jack)`.
6. `¬Animale(F(Jack))∨Ama(G(Jack),Jack)` risolve con `A1) Animale(F(x))∨Ama(G(x),x)` (istanziato in `x/Jack`, dando `Animale(F(Jack))∨Ama(G(Jack),Jack)`) ⟹ per fattorizzazione/risoluzione si giunge a `Ama(G(Jack),Jack)`.
7. Il ramo produce infine la **clausola vuota** (contraddizione), confermando che `KB ∧ ¬Q` è insoddisfacibile, dunque **Curiosity ha ucciso il gatto** è conseguenza logica della KB.

(Lo schema esatto dell'albero binario di risoluzione, come presentato nelle slide originali, è un albero con foglie `Gatto(Tuna)`, `¬Gatto(Tuna)∨Animale(Tuna)`, `Uccide(Jack,Tuna)∨Uccide(Curiosity,Tuna)`, `¬Uccide(Curiosity,Tuna)` e le clausole A1/A2/B/C, che si combinano a coppie fino a produrre il nodo radice `Ama(G(Jack),Jack)` seguito dalla clausola vuota — utile soprattutto per intuire il meccanismo, il dettaglio grafico esatto è secondario rispetto a comprendere che ogni passo è un'applicazione di risoluzione binaria con unificazione.)

### Refutation-completeness

La risoluzione **non** è in grado di generare (enumerare) *tutte* le conseguenze logiche di una KB, ma è **refutation-complete**:

- Se una KB è **insoddisfacibile**, la risoluzione sarà ***sempre in grado di derivare, in un numero finito di passi, la clausola vuota (contraddizione)***.
- Di conseguenza, è in grado di derivare **tutte le risposte** a una query `Q(x)` a partire da una KB, a patto di verificare che `KB ∧ ¬Q(x)` sia insoddisfacibile — è esattamente lo schema della dimostrazione per refutazione già visto in proposizionale, ora esteso a FOL grazie al lifting.

## Costruire una KB in FOL: ingegneria della conoscenza

Processo generale (*knowledge engineering*):

1. Identificare l'uso che si desidera fare della KB.
2. Raccogliere la conoscenza rilevante (in forma informale).
3. Definire un vocabolario di costanti, funzioni e predicati.
4. Formalizzare la conoscenza in formule FOL.

Quando poi si vuole interrogare la KB:

1. Descrivere in modo formale la specifica istanza del problema.
2. Interrogare la KB (query).

## Riepilogo e punti chiave

- La logica proposizionale è dichiarativa, composizionale e non ambigua, ma **manca di espressività**: non permette rappresentazioni compatte né relazioni fra oggetti. FOL aggiunge **oggetti**, **relazioni (predicati)**, **funzioni** e **quantificatori**, mantenendo le buone proprietà della proposizionale.
- Un **modello FOL** è la coppia `M=(D,I)`: dominio + interpretazione. Il valore di verità di una formula dipende sempre dal modello scelto, non è assoluto.
- **Termini** (costanti, variabili, applicazioni di funzione) denotano oggetti; le **formule atomiche** (predicato applicato a termini, o uguaglianza fra termini) esprimono fatti su di essi.
- **∀** si accompagna naturalmente a **⇒** (per restringere il discorso a una sottoclasse), **∃** si accompagna naturalmente a **∧** (per affermare l'esistenza di un caso con più proprietà congiunte). Usare la combinazione sbagliata è l'errore più comune in FOL.
- L'**ordine dei quantificatori annidati di tipo diverso conta**: `∀x∃y` ≠ `∃y∀x`. Quantificatori dello stesso tipo invece commutano liberamente.
- L'**uguaglianza** serve a distinguere/identificare oggetti; senza `¬(x=y)` esplicito, FOL standard non assume l'unicità dei nomi (a differenza della *database semantics*, con Unique Names + Closed World + Domain Closure, usata in programmazione logica).
- L'inferenza in FOL può avvenire per **proposizionalizzazione** (UI/EI + algoritmo proposizionale, corretto e completo per il teorema di Herbrand ma inefficiente e a rischio di non terminazione se la KB contiene funzioni) o per **lifting delle regole di inferenza** (più efficiente).
- Il **Modus Ponens Generalizzato (MPG)** collega n premesse atomiche più un'implicazione con antecedente congiuntivo a una conclusione istanziata tramite sostituzione: è il motore del **forward chaining** e del **backward chaining** su clausole di Horn.
- L'**unificazione** (`UNIFY(F1,F2)=θ`) trova la sostituzione (idealmente il Most General Unifier) che rende identiche due formule; può fallire per conflitti di variabile, risolvibili con la standardizzazione separata.
- **Forward chaining**: guidato dai dati, corretto, completo e terminante su KB DATALOG (Horn senza funzioni); propaga sia verità che sostituzioni lungo un grafo AND-OR.
- **Backward chaining**: guidato dall'obiettivo, corretto ma incompleto (depth-first, rischio di loop), generalmente più efficiente del forward chaining.
- La **risoluzione** proposizionale può essere "liftata" a FOL (risoluzione binaria + fattorizzazione, con unificazione al posto dell'uguaglianza sintattica): è **refutation-complete**, cioè capace di rilevare sempre l'insoddisfacibilità di `KB ∧ ¬Q` quando la query `Q` è davvero conseguenza logica.
- Per applicare la risoluzione, la KB va portata in **CNF**: elimina `⇔`/`⇒`, sposta le negazioni all'interno, standardizza le variabili, **skolemizza** gli esistenziali, elimina gli universali residui, distribuisci `∨` su `∧`.
- La **skolemizzazione** sostituisce ogni variabile esistenziale con una **funzione di Skolem** i cui argomenti sono le variabili universali nel cui scope essa ricade (o con una **costante di Skolem** se non ricade nello scope di alcun universale). È un passo cruciale: sbagliarlo (es. usare EI ingenuamente sotto un `∀`) porta a formule che fissano erroneamente un unico valore condiviso da tutti gli oggetti, invece di un valore che può variare al variare degli altri parametri.
