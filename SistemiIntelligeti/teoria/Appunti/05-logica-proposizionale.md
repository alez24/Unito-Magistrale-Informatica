# Modulo 5: Rappresentazione della conoscenza e Logica proposizionale

## Perché rappresentare la conoscenza

Rappresentare la conoscenza significa dotarsi di un **linguaggio formale** in cui esprimere ciò che si sa del mondo, in modo tale da poter applicare a quella conoscenza dei **processi di ragionamento automatici (inferenze)**. Lo scopo dell'inferenza è duplice:

- derivare **nuova conoscenza**, cioè informazioni che erano implicite e diventano esplicite;
- **prendere decisioni**, in particolare decidere quale azione eseguire (nel caso di un agente).

### Cosa vuol dire "ragionare"

Ragionare significa **rendere esplicita conoscenza che era implicita**. Esempio classico:

- So che *tutti i cetacei vivono in mare* e che *tutte le balene sono cetacei*.
- Posso concludere che *tutte le balene vivono in mare*, **senza aver verificato personalmente** ogni singola balena: mi basta **assumere vere** le due premesse e applicare uno schema di ragionamento valido.

Il punto cruciale è che questo tipo di ragionamento **lavora sulla forma delle affermazioni**, trattate come schemi astratti (Tutti gli A hanno la proprietà P; Tutti i B sono A ⟹ Tutti i B hanno P), indipendentemente dal contenuto specifico. Questo è ciò che rende il ragionamento **automatizzabile**: basta

1. un **linguaggio** per strutturare le affermazioni in modo standard;
2. delle **regole di ragionamento** codificate (quando un'affermazione si può dire vera, quando una conclusione segue da altre);
3. un **algoritmo** che sappia applicare le regole alla conoscenza rappresentata.

### Agenti basati sulla conoscenza

Un agente basato sulla conoscenza è caratterizzato da:

- **Knowledge Base (KB)**: insieme di formule espresse nel linguaggio di rappresentazione, possedute dall'agente. Può cambiare nel tempo. La conoscenza posseduta all'inizio è la **background knowledge**.
- **Tell (assert)**: meccanismo per aggiungere nuove formule alla KB.
- **Ask (query)**: meccanismo per interrogare la KB.

Sia `ask` che `tell` possono attivare processi di inferenza. Vincolo fondamentale: **ogni risposta a una `ask` deve essere conseguenza logica** delle `tell` fatte e della background knowledge. Esempio: se la KB contiene "quando piove la strada è bagnata" e faccio `tell(piove)`, allora `ask(strada bagnata?)` deve rispondere *Yes*.

**Schema generale dell'agente (KB-Agent):**

```
Agente ha: KB
Tempo = 0

function KB-Agent(percezione) returns azione:

  1. tell(KB, costruisci-formulaP(percezione, tempo))
  2. azione ← ask(KB, costruisci-interrogazioneA(tempo))
  3. tell(KB, costruisci-formulaA(azione, tempo))
  4. tempo ← tempo + 1
  5. return azione
```

L'agente parte da una KB iniziale; ad ogni ciclo la percezione corrente viene tradotta in formula e aggiunta alla KB (tell), si interroga la KB per decidere l'azione (ask), si registra l'azione eseguita (tell), e si avanza il tempo (necessario per mantenere una "storia").

Una **versione 2** sostituisce la prima `tell` con `modify` (che può sia aggiungere sia **rimuovere** elementi, non solo accumulare fatti) e usa `add` per la seconda operazione. Esempio: se la KB contiene "il bicchiere è vuoto" e l'azione è "riempi il bicchiere", `modify` cancella quel fatto e aggiunge "bicchiere pieno" — necessario perché il mondo cambia, non solo si accumula.

La KB quindi evolve nel tempo: `background knowledge + percezione(0) + azione(0) + percezione(1) + azione(1) + ...`

### Dato, informazione, conoscenza

Distinzione concettuale importante:

- **Dato**: il risultato grezzo della percezione sensoriale, privo di significato (es. un segno grafico).
- **Informazione**: ciò che il dato rappresenta (es. quel segno è la lettera "u" di un certo alfabeto) — in parte legata allo scopo per cui si percepisce.
- **Conoscenza**: cattura le **relazioni** fra le informazioni (es. le regole per comporre lettere in parole e frasi).

### Esempio: bug algorithm

Un agente con conoscenza solo locale dell'ambiente, capace di procedere in linea retta e, incontrato un ostacolo, di applicare **wall following** (segue il muro tenendosi parallelo, dopo aver scelto una direzione di rotazione). Percezioni ∈ {ostacolo, libero, allineato, arrivato}, azioni ∈ {avanza, ruota}. Mostra concretamente come la KB si accresce ciclo dopo ciclo con i `tell` di percezioni e azioni.

### Programmazione dichiarativa

Programmare un agente basato sulla conoscenza significa **specificare la KB** (che include anche la specifica delle azioni disponibili, precondizioni ed effetti) **in forma dichiarativa**: si dice *cosa* è vero/cosa fare, non *come* calcolarlo procedurabilmente. L'agente è dotato di meccanismi generali di `ask`/`tell` validi per qualsiasi KB — è un paradigma radicalmente diverso da quello procedurale, dove tutto è codificato da procedure specifiche del dominio.

Esempi di programmazione dichiarativa: XML (descrive la struttura di un documento, non come renderizzarlo), una query SQL (dice quali dati estrarre, non come attraversare le tabelle), un'espressione regolare (descrive una forma, non l'algoritmo di ricerca).

### Esempio: il mondo dei blocchi

Blocchi su un tavolo, impilabili uno sull'altro, un blocco alla volta. Predicati: `holding(x)`, `handempty`, `clear(x)`, `ontable(x)`, `on(x,y)`. Le azioni sono descritte dichiarativamente con **precondizioni** ed **effetti** (add/delete), ad esempio l'azione `pick(x,y)`:

```
pick(x, y)
Preconditions: on(x,y) ∧ clear(x) ∧ handempty
Effects:
  add(clear(y))
  add(holding(x))
  delete(on(x,y))
  delete(clear(x))
  delete(handempty)
```

Qui `add` corrisponde a `tell`, `delete` rimuove elementi dalla descrizione dello stato (è l'operazione "opposta" al tell). La **background knowledge** è la descrizione delle azioni, la **percezione** è lo stato iniziale, e il **metodo** è l'applicazione di un criterio generale (non specifico del dominio) per determinare l'azione successiva — questo è esattamente lo spirito della programmazione dichiarativa applicata alla pianificazione.

---

## Rappresentare la conoscenza tramite la logica

Un **linguaggio di rappresentazione** è lo strumento che permette di codificare la conoscenza in una forma su cui si può applicare un ragionamento automatico. Una formula che rispetta le regole grammaticali del linguaggio è **ben formata**. La **semantica** del linguaggio definisce la verità delle formule rispetto a un mondo possibile (es. `on(E,A) ∧ clear(B)` può essere FALSA in un certo stato, mentre `clear(E) ∨ clear(C)` VERA).

I concetti chiave della logica come strumento di rappresentazione sono: **modello**, **conseguenza**, **inferenza**, **algoritmo di inferenza**, **grounding**.

### Modello

Un **modello** è un "mondo possibile": fissa il valore di verità di tutte le formule assegnando valori agli elementi da cui quei valori dipendono. Esempio: per la formula `x + y = 4`, è vera nei modelli x=1,y=3 o x=2,y=2 ecc., falsa in x=0,y=0 ecc. Quando il dominio è la realtà fisica, il modello è un'**astrazione matematica/simbolica** significativa di quella realtà.

Definizione formale: dati un modello *m* e una formula α, **m è un modello di α se α è vera in m**. Si indica con **M(α)** l'insieme di tutti i modelli di α.

### Conseguenza logica (entailment, ⊨)

**A ⊨ B** ("A implica logicamente B", "B è conseguenza logica di A") significa: **in tutti i modelli in cui A è vera, è vera anche B**. Esempio: (x+y=4) ⊨ (x+y<5).

Attenzione alla **direzionalità**: A ⊭ B (B non è conseguenza di A) significa solo che *esiste almeno un modello* in cui A è vera e B è falsa — non che B sia sempre falsa quando A è vera. Esempio: (x+y=4) ⊭ (x<3), perché nel modello x=4,y=0 la prima è vera e la seconda falsa (basta un controesempio, anche se in altri modelli entrambe potrebbero essere vere).

**Visione insiemistica**: A ⊨ B corrisponde all'inclusione insiemistica **M(A) ⊆ M(B)** — l'insieme dei modelli che rendono vera A è un sottoinsieme di quelli che rendono vera B.

### Equivalenza

**A ≡ B** se e solo se A ⊨ B e B ⊨ A, cioè le due formule sono vere esattamente negli stessi modelli: **M(A) = M(B)**.

### Validità, insoddisfacibilità, soddisfacibilità

- **Validità (tautologia)**: una formula P è **valida** se è vera in **tutti** i modelli (P ≡ True). Esempio: `Q ∨ ¬Q` è una tautologia.
- **Insoddisfacibilità (contraddizione)**: una formula P è **insoddisfacibile** se è **falsa** in tutti i modelli (P ≡ False). Esempio: `Q ∧ ¬Q`.
- **Soddisfacibilità**: una formula P è **soddisfacibile** se esiste **almeno un** modello in cui è vera. Se m soddisfa P si dice che *m è un modello di P*. (Applicazione pratica: nei CSP si cerca proprio un modello, cioè un assegnamento che soddisfi tutti i vincoli.)

Relazione importante: **P è valida se e solo se ¬P è insoddisfacibile** (e viceversa, per dualità).

### Inferenza

**Inferenza** (dal latino *in ferre*, "portare dentro"): processo con cui, da una proposizione accettata come vera, si passa a una seconda proposizione la cui verità è derivata dalla prima. Punto essenziale: ***l'inferenza è sintattica***, lavora sulla struttura delle formule secondo le regole del linguaggio, non sul loro "significato".

Esempio: da "tutti gli uomini sono mortali" e "Socrate è un uomo" si inferisce "Socrate è mortale", applicando lo schema generale `uomo(X) ⇒ mortale(X), uomo(X) ⊢ mortale(X)`.

**Regole di inferenza principali:**

- **Modus Ponens**: da `A ⇒ B` e `A` si deriva `B`. È il fondamento del ragionamento deduttivo ("Se piove, la strada è bagnata. Piove. ⟹ La strada è bagnata").
- **Eliminazione della congiunzione**: da `A ∧ B` si deriva `B` (o `A`).

**Formalizzazione**: sia *i* un algoritmo di inferenza. **KB ⊢ᵢ A** significa che A è derivabile da KB usando l'algoritmo i, cioè esiste una sequenza di passi che da KB porta ad A. Si dice anche: "A segue da KB", "A può essere inferito da KB", "esiste una dimostrazione di A a partire da KB".

**Proprietà desiderate di un algoritmo di inferenza:**

- **Correttezza (soundness)**: l'algoritmo deriva *solo* conseguenze logiche vere — se KB ⊢ᵢ A allora KB ⊨ A. Non produce mai conclusioni sbagliate.
- **Completezza (completeness)**: l'algoritmo è in grado di derivare *tutte* le conseguenze logiche — se KB ⊨ A allora KB ⊢ᵢ A. Non "perde" conclusioni valide.

Le logiche devono **sempre** garantire la correttezza (altrimenti le inferenze non corrispondono a reali conseguenze nel mondo); non sempre garantiscono la completezza.

**Piano dell'astrazione vs piano della realtà**: le formule sono astrazioni usate per ragionare sul mondo; la semantica collega le formule al mondo reale dando loro significato; i modelli catturano il mondo reale insieme alla relazione di conseguenza.

### Grounding

Il **grounding** cattura il legame fra la rappresentazione simbolica/formale e l'ambiente reale che essa rappresenta — possiamo pensarlo come derivante dalla percezione. Esempio: so che "quando piove le strade sono bagnate"; vedo (percepisco) che piove, e quindi concludo che nel mondo reale le strade sono bagnate. Il grounding è ciò che rende la logica utile per ragionare sul mondo reale e non solo su simboli astratti.

---

## Logica proposizionale

È uno dei tipi di logica più semplici: **le formule non contengono variabili**. Si articola in: sintassi, semantica, inferenza, e i concetti di equivalenza/validità/soddisfacibilità già visti in generale.

### Sintassi

**Formule atomiche:**

- i **simboli proposizionali** rappresentano ciascuno una formula elementare che può essere vera o falsa (per convenzione hanno un nome che inizia con la maiuscola, es. `Piove`);
- `True` e `False` sono formule atomiche speciali.

**Formule complesse**, costruite componendo formule tramite operatori (connettivi):

- **Negazione** (¬): un **letterale** è una formula atomica, eventualmente negata;
- **Congiunzione** (∧): le formule combinate sono dette **congiunti**;
- **Disgiunzione** (∨): le formule combinate sono dette **disgiunti**;
- **Implicazione** (⇒): collega una **premessa/antecedente** a una **conclusione/conseguente**;
- **Biimplicazione/equivalenza** (⇔).

**Grammatica formale:**

```
formula          → formulaAtomica | formulaComplessa
formulaAtomica    → True | False | simbolo
simbolo           → P | Q | R | ...
formulaComplessa  → ¬ formula                    (negazione)
                  | (formula ∧ formula)           (congiunzione)
                  | (formula ∨ formula)           (disgiunzione)
                  | (formula ⇒ formula)           (implicazione)
                  | (formula ⇔ formula)           (equivalenza)
```

**Precedenza degli operatori** (dal più forte/legante al più debole): ¬, ∧, ∨, ⇒, ⇔. Esempio: `¬Q ∨ P` equivale a `((¬Q) ∨ P)`.

> ❓ **Domanda d'esame:** "Vero o falso? Si consideri la formula `Piove ∧ Vento`: è vera o falsa?"
> **Risposta ragionata:** la domanda è mal posta finché non si fissa un **modello**. Il valore di verità di una formula proposizionale non è assoluto: dipende dall'assegnamento di verità ai simboli atomici che la compongono. `Piove ∧ Vento` è vera **solo** nel modello in cui sia `Piove` sia `Vento` sono vere (T,T); è falsa in tutti gli altri tre casi (T,F), (F,T), (F,F), perché la congiunzione richiede che *entrambi* i congiunti siano veri. Questo è il punto pedagogico della slide: senza specificare il modello di riferimento, non si può rispondere "vera" o "falsa" in assoluto.

### Semantica

La semantica definisce le regole per calcolare il valore di verità di ogni formula. Un **modello**, in logica proposizionale, è un **assegnamento di un valore di verità a ciascun simbolo proposizionale**. Con **N simboli proposizionali** ci sono **2ᴺ modelli possibili**. La semantica è definita **ricorsivamente**:

**Formule atomiche:**

- `True` è sempre vera, `False` è sempre falsa in ogni modello;
- il valore di verità di ogni altro simbolo va specificato esplicitamente dal modello.

**Formule complesse** (P, Q formule qualsiasi):

- `¬Q` è vera **se e solo se** Q è falsa;
- `Q ∧ P` è vera **se e solo se** sia P sia Q sono vere;
- `Q ∨ P` è vera **se e solo se** almeno una fra P e Q è vera;
- `Q ⇒ P` è sempre vera, **tranne** quando Q è vera e P è falsa;
- `Q ⇔ P` è vera **se e solo se** P e Q hanno lo **stesso** valore di verità.

**Tabella di verità dei connettivi:**

| P | Q | ¬P | P∧Q | P∨Q | P⇒Q | P⇔Q |
|---|---|----|----|-----|-----|-----|
| F | F | T  | F  | F   | T   | T   |
| F | T | T  | F  | T   | T   | F   |
| T | F | F  | F  | T   | F   | F   |
| T | T | F  | T  | T   | T   | T   |

#### L'implicazione: come interpretarla

`P ⇒ Q` è **equivalente a** `¬P ∨ Q`. Va letta così:

- se P è **falsa**, non ci si preoccupa del valore di Q: l'implicazione è comunque **vera** (il conseguente non deve necessariamente essere vero, l'affermazione è "vacuamente" soddisfatta);
- se P è **vera**, allora Q deve **necessariamente** essere vera perché l'implicazione sia vera.

In sintesi: `P ⇒ Q` serve a catturare le situazioni in cui **ogni volta che è vero l'antecedente, è vero anche il conseguente**; quando l'antecedente è falso, l'implicazione non dice nulla e viene considerata vera per convenzione.

**Attenzione**: l'implicazione logica ***non è una relazione causale***. È vera o falsa solo in base ai valori di verità di P e Q, indipendentemente dal legame di significato/causa fra le due proposizioni. Esistono altri tipi di implicazione legati al significato delle parole (non trattati come implicazione logica):

- "Fido è un cane ⟹ Fido è un mammifero" (ragionamento **ontologico**);
- "John ha vinto la partita ⟹ John ha giocato la partita" (ragionamento **temporale**);
- "John è stato condannato per furto ⟹ il furto è un crimine" (ragionamento **causale**).

> ❓ **Domanda d'esame:** "È vera l'implicazione `Torino è in Lombardia ⇒ Giulio Cesare governò Roma`?"
> **Risposta ragionata:** sì, è **vera**. Sembra assurda perché intuitivamente attribuiamo all'implicazione un legame causale/di significato, ma l'implicazione logica dipende **solo** dai valori di verità: `Torino è in Lombardia` è **falsa** (Torino è in Piemonte), e quando l'antecedente è falso `P ⇒ Q` è vera **indipendentemente** dal valore di verità di Q. Questo è l'esempio didattico standard per mostrare che l'implicazione logica non coincide con la nozione intuitiva di causa-effetto.

#### Biimplicazione

`P ⇔ Q` si legge "P se e solo se Q" ed è vera esattamente quando P e Q hanno **lo stesso** valore di verità (entrambe vere o entrambe false).

### Verificare l'entailment: KB ⊨ P?

Esistono due approcci:

1. **Model checking**: enumerare tutti i possibili modelli, selezionare quelli in cui KB è vera, e verificare che in *tutti* questi P sia vera. È **costoso**: con N simboli proposizionali ci sono 2ᴺ modelli — crescita esponenziale.
2. **Theorem proving**: usare regole di inferenza per cercare una derivazione **senza costruire esplicitamente i modelli**. Più efficiente perché ignora le proposizioni irrilevanti alla dimostrazione (che possono essere numerose).

Il theorem proving si basa su due risultati fondamentali:

**Teorema di deduzione**: date due formule R e Q, **(R ⊨ Q) se e solo se (R ⇒ Q) è valida** (cioè è una tautologia). Quindi per verificare KB ⊨ P si può:

- dimostrare che `KB ⇒ P` è vera in ogni modello (enumerazione, costoso), oppure
- dimostrare **per inferenza sintattica** (manipolando la forma delle formule) che `(KB ⇒ P) ≡ True`.

**Dimostrazione per refutazione**: sfruttando che validità e soddisfacibilità sono legate dalla negazione (A è valida sse ¬A è insoddisfacibile), e che `(R ⇒ Q) ≡ (¬R ∨ Q)`, negando si ottiene `¬(¬R ∨ Q) ≡ (R ∧ ¬Q)` (De Morgan). Si arriva quindi al risultato: **date R e Q, (R ⊨ Q) se e solo se (R ∧ ¬Q) è insoddisfacibile**.

Questo corrisponde esattamente a una **dimostrazione per assurdo/contraddizione**: per verificare KB ⊨ P,

1. si assume **per assurdo** ¬P;
2. si dimostra che `KB ∧ ¬P` è insoddisfacibile, cioè che partendo da `KB ∧ ¬P` si deriva `False` (una contraddizione);
3. la ricerca della dimostrazione è formalmente analoga a una ricerca in uno spazio degli stati (stato iniziale = background knowledge, azioni = regole di inferenza, goal = stato che contiene la formula da dimostrare — in questo caso `False`).

Il ragionamento si applica a **logiche monotone**: se KB ⊨ P allora anche KB ∧ Q ⊨ P — aggiungere informazione non invalida mai le conclusioni già derivate, l'insieme delle conseguenze può solo crescere.

### Regole di inferenza (equivalenze logiche)

Oltre a modus ponens ed eliminazione della congiunzione, altre regole derivano da equivalenze logiche standard:

| Equivalenza | Nome |
|---|---|
| (α ∨ β) ≡ (β ∨ α) | Commutatività ∨ |
| (α ∧ β) ≡ (β ∧ α) | Commutatività ∧ |
| ((α ∧ β) ∧ γ) ≡ (α ∧ (β ∧ γ)) | Associatività ∧ |
| ((α ∨ β) ∨ γ) ≡ (α ∨ (β ∨ γ)) | Associatività ∨ |
| ¬(¬α) ≡ α | Eliminazione doppia negazione |
| (α ⇒ β) ≡ (¬β ⇒ ¬α) | Contrapposizione |
| (α ⇒ β) ≡ (¬α ∨ β) | Eliminazione implicazione |
| ¬(α ∧ β) ≡ (¬α ∨ ¬β) | De Morgan |
| ¬(α ∨ β) ≡ (¬α ∧ ¬β) | De Morgan |
| (α ∧ (β ∨ γ)) ≡ ((α ∧ β) ∨ (α ∧ γ)) | Distributività |
| (α ∨ (β ∧ γ)) ≡ ((α ∨ β) ∧ (α ∨ γ)) | Distributività |
| (α ⇔ β) ≡ ((α ⇒ β) ∧ (β ⇒ α)) | Eliminazione bicondizionale |

**Correttezza e completezza**: la dimostrazione avviene combinando (1) un algoritmo di inferenza e (2) un insieme di regole di inferenza. L'insieme completo delle regole viste è **corretto** (deriva solo conseguenze vere) e **completo** (deriva tutte le conseguenze logiche). Se si usa solo un **sottoinsieme** delle regole, si rischia di perdere completezza: ad esempio, senza la regola del doppio negato non si può derivare `P ⊢ ¬¬P`.

### La regola di risoluzione (Resolution)

La **risoluzione** è una singola regola di inferenza che, combinata con un algoritmo di ricerca completo, produce un algoritmo di inferenza ***corretto e completo***: se KB ⊢ P allora KB ⊨ P (correttezza) e se KB ⊨ P allora KB ⊢ P (completezza). Permette di realizzare **dimostrazioni per refutazione** sia in logica proposizionale sia in logica del prim'ordine.

Si applica a **clausole**, cioè disgiunzioni di letterali. Date due clausole che contengono un **letterale complementare** Pᵢ e Qⱼ (uno negazione dell'altro):

```
(P1 ∨ ... ∨ Pi ∨ ... ∨ Pn)      (Q1 ∨ ... ∨ Qj ∨ ... ∨ Qm)
─────────────────────────────────────────────────────────
  (P1 ∨...∨ Pi-1∨ Pi+1∨...∨ Pn ∨ Q1∨...∨ Qj-1∨ Qj+1∨...∨ Qm)
```

La clausola risultante (**resolvent**) contiene tutti i letterali delle due clausole originali **tranne** la coppia complementare; se un letterale compare più volte viene **fattorizzato** (mantenuto una sola volta): es. `A ∨ A` diventa `A`.

**Esempio**: da `A ∨ B ∨ ¬C` e `C ∨ A` (letterali complementari ¬C e C), si ottiene `A ∨ B ∨ A`, che fattorizzato diventa `A ∨ B`.

**Relazione con il modus ponens**: il modus ponens è un **caso particolare** di risoluzione. Si evidenzia eliminando l'implicazione: da `C` e `C ⇒ A` (cioè `¬C ∨ A`), risolvendo su C/¬C si ottiene `A` — esattamente il risultato del modus ponens.

### Dall'agente alla necessità della forma clausale

Nello schema dell'agente basato sulla conoscenza, la `ask` attiva un processo di inferenza in cui **la query, negata**, viene aggiunta alla KB e, applicando iterativamente la risoluzione, si cerca di derivare la clausola vuota (contraddizione), confermando così l'entailment.

**Prerequisito**: la risoluzione si applica a clausole, quindi la KB proposizionale va prima **tradotta in CNF** (Conjunctive Normal Form).

### Forma Normale Congiuntiva (CNF)

**CNF (Conjunctive Normal Form)**: data una qualunque formula proposizionale, esiste sempre una **congiunzione di clausole** ad essa equivalente.

**Grammatica delle clausole:**

```
CNFsentence → Clause ∧ ... ∧ Clause
Clause      → Literal ∨ ... ∨ Literal
Literal     → Symbol | ¬Symbol
Symbol      → P | Q | ...
```

**Algoritmo di traduzione in CNF** (4 passi):

1. **Eliminare la biimplicazione**: `(α ⇔ β)` diventa `((α ⇒ β) ∧ (β ⇒ α))`.
2. **Eliminare l'implicazione**: `(α ⇒ β)` diventa `(¬α ∨ β)`.
3. **Portare la negazione all'interno** applicando De Morgan ed eliminando le doppie negazioni: `¬(α ∧ β)` → `(¬α ∨ ¬β)`; `¬(α ∨ β)` → `(¬α ∧ ¬β)`; `¬¬α` → `α`.
4. **Distribuire l'∨ sull'∧** dove necessario: `(α ∨ (β ∧ γ))` → `((α ∨ β) ∧ (α ∨ γ))`.

Il risultato finale è una congiunzione di clausole, ciascuna disgiunzione di letterali — la forma richiesta dalla risoluzione.

#### Esempio completo: dalle formule alle clausole

Partendo da una base di conoscenza proposizionale su pioggia/atmosfera/strada, tradotta in clausole:

```
C1)  ¬Piove ∨ Atmosfera_umida
C2)  ¬Notte ∨ Vento ∨ Atmosfera_umida
C3a) ¬Atmosfera_umida ∨ Prato_bagnato
C3b) ¬Atmosfera_umida ∨ Strada_Bagnata
C4)  ¬Innaffiatore_on ∨ Prato_bagnato
C5)  ¬Piove ∨ Ombrello_aperto
C6)  ¬Sole ∨ ¬Vento ∨ Innaffiatore_on
C7)  ¬Sole ∨ ¬Vento ∨ Atmosfera_asciutta
C8)  ¬Sole ∨ ¬Notte
C10) ¬Atmosfera_asciutta ∨ ¬Atmosfera_umida
```

(Osservazione: due regole diverse della KB originale possono tradursi nella *stessa* clausola, come accade per C8.)

### Algoritmo di risoluzione proposizionale

```
function CP-RISOLUZIONE(KB, A) returns true | false
  Input: KB (base di conoscenza), A (query, formula proposizionale)

  clausole ← clausole della CNF di (KB ∧ ¬A)
  new ← { }

  loop do:
    for each coppia Ci, Cj in clausole do:
        resolvents ← IR-RISOLUZIONE(Ci, Cj)
        if resolvents contiene la clausola vuota:
            return true
        new ← new ∪ resolvents
    if new ⊆ clausole:
        return false
    clausole ← clausole ∪ new
```

Il funzionamento è quello di una **dimostrazione per refutazione**: si nega la query, la si aggiunge alla KB in CNF, e si cerca — risolvendo iterativamente tutte le coppie di clausole — di generare la **clausola vuota** (che rappresenta `False`, cioè una contraddizione). Se la si trova, KB ⊨ A è confermato (return true). Se non si generano più nuove clausole (new è già incluso in clausole, punto fisso raggiunto) senza aver trovato la clausola vuota, allora KB ⊭ A (return false).

**Teorema di completezza della risoluzione** (non dimostrato a lezione): se un insieme di clausole è insoddisfacibile, la **chiusura della risoluzione** (l'insieme di tutte le clausole derivabili) contiene la clausola vuota.

#### Esempio applicativo: pioggia, atmosfera, strada

Data la KB precedente, si aggiungono i fatti percepiti F1) `Sole` e F2) `Vento`. Si vuole verificare:

**KB ⊨ ¬Piove ?**

Si usa la refutazione: si nega il goal ottenendo la clausola **GN) Piove**, la si aggiunge alla KB in CNF, e si cerca di derivare la clausola vuota:

1. **GN) Piove** risolve con **C1) ¬Piove ∨ Atmosfera_umida** → **C21) Atmosfera_umida**
2. **C21)** risolve con **C10) ¬Atmosfera_asciutta ∨ ¬Atmosfera_umida** → **C22) ¬Atmosfera_asciutta**
3. **C22)** risolve con **C7) ¬Sole ∨ ¬Vento ∨ Atmosfera_asciutta** → **C23) ¬Sole ∨ ¬Vento**
4. **C23)** risolve con **F1) Sole** → **C24) ¬Vento**
5. **C24)** risolve con **F2) Vento** → **clausola vuota**

Si è generata la clausola vuota: la KB (con `Piove` aggiunto) è insoddisfacibile, quindi per refutazione **KB ⊨ ¬Piove** è confermato: la risposta è **true**.

---

## Clausole di Horn, Forward Chaining, Backward Chaining

In molti contesti pratici la conoscenza si presenta in una forma molto specifica — le **clausole di Horn** — per cui sono stati sviluppati meccanismi di inferenza dedicati, molto più efficienti della risoluzione generale.

### Clausole di Horn

**Definizione**: una clausola di Horn è una disgiunzione di letterali in cui **al più uno** è positivo (non negato).

- Se la clausola contiene **esattamente un** letterale positivo, si dice **clausola definita**.
- Esempi di clausole di Horn: `¬B ∨ C`, `¬A ∨ ¬B ∨ C` (queste due sono anche clausole definite, avendo esattamente un positivo), `¬A ∨ ¬B` (nessun positivo, non è definita ma è comunque di Horn).

Le clausole di Horn **catturano implicazioni** in cui l'antecedente è una congiunzione di letterali positivi e il conseguente è un singolo letterale positivo: `¬B ∨ C` equivale a `B ⇒ C`; `¬A ∨ ¬B ∨ C` equivale a `A ∧ B ⇒ C`. Sono la **base della programmazione logica** (es. Prolog).

**Perché sono importanti**: su clausole di Horn si possono applicare meccanismi di inferenza **molto naturali** per il ragionamento umano, e soprattutto permettono di verificare la conseguenza logica in un ***tempo lineare*** rispetto alla dimensione della KB — mentre la risoluzione generale non ha questa garanzia di efficienza. Questo rende l'inferenza proposizionale su clausole di Horn **computazionalmente economica**.

### Forward Chaining (concatenazione in avanti)

Permette di derivare una query costituita da un **singolo simbolo proposizionale**, a partire da una KB di sole clausole di Horn. È un procedimento **iterativo**, **guidato dai dati (data-driven)**:

1. Si parte dai **fatti noti** (letterali già veri).
2. Si applica **modus ponens**: da `F ⇒ Q` e `F` (con F verificata) si deriva `Q`.
3. Ogni volta che **tutte le premesse** di un'implicazione risultano vere, si **aggiunge** il letterale conseguente all'insieme dei fatti noti.
4. **Terminazione**: se si deriva la query cercata → `return true`; se ad un certo punto non si possono fare altre inferenze senza aver derivato la query → `return false`.

Ha **complessità lineare** nella dimensione della KB.

#### Esempio (rappresentazione a grafo AND-OR)

KB:
```
P ⇒ Q
L ∧ M ⇒ P
B ∧ L ⇒ M
A ∧ P ⇒ L
A ∧ B ⇒ L
```
Fatti: `A`, `B`. Obiettivo: dimostrare `Q`.

Nel grafo AND-OR gli archi uniti da un "archetto" rappresentano letterali in AND (tutte le premesse di una stessa regola), mentre frecce distinte verso lo stesso nodo rappresentano OR (regole diverse con la stessa conclusione — un arco OR si attiva se almeno un disgiunto/regola è vero). Partendo dai fatti A e B, l'attivazione si propaga: A∧B attivano L (tramite `A∧B⇒L`); con L noto e B noto si attiva M (tramite `B∧L⇒M`); con L e M noti si attiva P (tramite `L∧M⇒P`); infine con P noto si attiva Q (tramite `P⇒Q`). Tutti questi letterali risultano quindi veri.

**Osservazioni sul forward chaining:**

- **Complessità lineare**.
- **Completo**: deriva tutte le formule atomiche dimostrabili a partire dalla KB.
- ***"Inconscio" (data-driven)***: è guidato solo dai dati disponibili, senza usare l'informazione sul goal che si vuole dimostrare — non sa dove sta andando.
- Adatto a problemi come il **riconoscimento di oggetti** (si parte da osservazioni per arrivare a conclusioni).
- Svantaggio: può attivare **molte inferenze inutili**, irrilevanti ai fini della query specifica.

### Backward Chaining (concatenazione all'indietro)

Parte dalla formula da dimostrare (il **goal**):

- se il goal è **già vero** (è un fatto noto), termina restituendo `true`;
- altrimenti cerca clausole di Horn di cui il goal è la **conclusione**, e cerca ricorsivamente di dimostrarne le **premesse**, usando anche i fatti noti come base.

È quindi un ragionamento ***goal-driven*** (guidato dagli obiettivi), opposto in direzione al forward chaining.

#### Esempio 1

```
R1) A ∧ C ⇒ F1
R2) B ∧ F1 ⇒ F2
```
Si vuole dimostrare `F2`, dati i fatti A, B, C. `F2` non è un fatto noto, ma esiste R2 la cui conclusione è F2: bisogna dimostrare `B` (fatto noto, verificato subito) e `F1`. `F1` non è un fatto noto, ma esiste R1 la cui conclusione è F1: bisogna dimostrare `A` e `C`, entrambi fatti noti. Quindi F1 è vera, e di conseguenza F2 è vera. I **valori di verità si propagano dal basso verso l'alto** (come valori di ritorno di una ricorsione).

#### Esempio 2 (stessa KB del forward chaining)

Con la stessa KB (`P⇒Q`, `L∧M⇒P`, `B∧L⇒M`, `A∧P⇒L`, `A∧B⇒L`) e fatti A, B, si vuole dimostrare `Q`:

- `Q` è vera se `P` è vera (regola `P⇒Q`);
- `P` è vera se `L` **e** `M` sono vere (regola `L∧M⇒P`);
- `M` è vera se `L` e `B` sono vere: `B` è un fatto noto, `L` va dimostrata;
- `L` è vera se `A` e `B` sono vere (regola `A∧B⇒L`): entrambi sono fatti noti! Oppure, alternativamente, se `A` e `P` sono vere (regola `A∧P⇒L`), ma di `P` non si conosce ancora il valore — non importa, **basta che una delle due alternative (regole con conclusione L) sia vera** per concludere che L è vera;
- una volta stabilito che L è vera, anche M risulta vera (avendo B e L); quindi P risulta vera (avendo L e M); infine Q risulta vera.

Nella ricerca si presta attenzione a **evitare loop** (nell'esempio, il tentativo di dimostrare L passando per P che a sua volta dipende da L viene "ignorato" una volta che L è già stata dimostrata per un'altra via) e a **non ridimostrare** un sottogoal già dimostrato in precedenza.

**Osservazioni sul backward chaining:**

- Realizza un ragionamento **guidato dagli obiettivi (goal-driven)**.
- È usato nel **theorem proving** e nella **programmazione logica** (es. Prolog) come meccanismo di inferenza principale.
- È spesso **più efficiente** del forward chaining perché l'uso esplicito del goal **focalizza** la ricerca solo sulle regole rilevanti, evitando di derivare fatti inutili.
- La complessità temporale è **meno che lineare** (nella pratica, grazie al focus sul goal).

### Forward vs Backward chaining: confronto

| Aspetto | Forward Chaining | Backward Chaining |
|---|---|---|
| Direzione | dai fatti verso le conclusioni | dal goal verso le premesse |
| Guida | *data-driven* (guidato dai dati) | *goal-driven* (guidato dagli obiettivi) |
| Completezza | completo (deriva tutto ciò che è dimostrabile) | dimostra solo ciò che serve al goal |
| Efficienza | lineare, ma può fare inferenze inutili | spesso più efficiente, focalizzato |
| Uso tipico | riconoscimento di pattern/oggetti | theorem proving, programmazione logica (Prolog) |

---

## Riepilogo e punti chiave

- **Rappresentare la conoscenza** significa dotarsi di un linguaggio formale su cui applicare **inferenza automatica**: da conoscenza esplicita (KB) si derivano conclusioni implicite. Un agente basato sulla conoscenza è definito da una **KB**, dalle operazioni **tell** (aggiungere formule) e **ask** (interrogare), con il vincolo che ogni risposta a una ask sia conseguenza logica di quanto asserito.
- I concetti fondamentali della logica come strumento sono: **modello** (mondo possibile che assegna valori di verità), **conseguenza logica ⊨** (A ⊨ B: B vera in tutti i modelli in cui A è vera), **equivalenza ≡**, **validità/tautologia** (vera in ogni modello), **insoddisfacibilità/contraddizione** (falsa in ogni modello), **soddisfacibilità** (vera in almeno un modello), e **inferenza** (processo sintattico che deriva nuove formule).
- Un buon algoritmo di inferenza deve essere **corretto** (soundness: deriva solo conseguenze vere) e idealmente **completo** (completeness: deriva tutte le conseguenze vere).
- La **logica proposizionale** ha sintassi basata su simboli atomici e connettivi (¬, ∧, ∨, ⇒, ⇔), e semantica definita ricorsivamente tramite tabelle di verità; con N simboli si hanno 2ᴺ modelli. L'**implicazione** P⇒Q equivale a ¬P∨Q ed è vera sempre tranne quando P è vera e Q falsa — **non è una relazione causale**.
- Per verificare **KB ⊨ P** si può fare model checking (costoso, esponenziale) oppure **theorem proving**, basato sul teorema di deduzione o, più praticamente, sulla **dimostrazione per refutazione**: si nega il goal, lo si aggiunge alla KB, e si dimostra che l'insieme è insoddisfacibile.
- La **CNF** (forma normale congiuntiva: congiunzione di clausole, ciascuna disgiunzione di letterali) si ottiene eliminando biimplicazione e implicazione, portando le negazioni all'interno (De Morgan), e distribuendo ∨ su ∧. È il prerequisito per applicare la **risoluzione**.
- La **regola di risoluzione** combina due clausole con letterali complementari producendo un resolvent; combinata con un algoritmo di ricerca completo è **corretta e completa**. Il **modus ponens è un caso particolare** di risoluzione. L'algoritmo `CP-RISOLUZIONE` cerca di derivare la **clausola vuota** da (KB ∧ ¬query) in CNF: se ci riesce, KB ⊨ query.
- Le **clausole di Horn** (al più un letterale positivo) permettono inferenza in **tempo lineare**, molto più efficiente della risoluzione generale, e sono alla base della programmazione logica.
- **Forward chaining**: parte dai fatti, applica modus ponens iterativamente, è **data-driven**, completo, lineare, ma può fare inferenze irrilevanti.
- **Backward chaining**: parte dal goal, cerca le regole che lo concludono e ne dimostra ricorsivamente le premesse, è **goal-driven**, generalmente più efficiente perché focalizzato, usato in Prolog e nel theorem proving.
