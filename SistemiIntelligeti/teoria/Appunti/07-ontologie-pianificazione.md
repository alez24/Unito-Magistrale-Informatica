# Modulo 7 — Tassonomie/Ontologie e Pianificazione automatica

---

## Parte A: Tassonomie e Ontologie

### 1. Cos'è una tassonomia

Una **tassonomia** è un'**organizzazione gerarchica di categorie o concetti**. L'esempio classico è la tassonomia del mondo animale (regno, phylum, classe, ordine, famiglia, genere, specie), ma il meccanismo si applica a qualsiasi dominio.

Il mattone concettuale è la **relazione di sottoclasse** (relazione **Is-a**): se `PalloneCalcio` è sottoclasse di `Pallone`, allora **tutte le istanze di `PalloneCalcio` sono anche istanze di `Pallone`**. Una tassonomia, in sostanza, è proprio l'organizzazione delle categorie che risulta dall'applicare in modo sistematico un insieme di regole di sottoclasse: è quindi un **albero** (o comunque una struttura gerarchica) di concetti collegati da relazioni Is-a.

**Perché è utile**: permette di caratterizzare le categorie tramite **proprietà** che valgono per tutte le istanze, ad esempio:

```
Member(X, Pallone) ⇒ Sferico(X)
```

Grazie alla relazione di sottoclasse, le istanze **ereditano** le proprietà delle sovraclassi: non serve ripetere `Member(X, PalloneCalcio) ⇒ Sferico(X)`, perché vale già per **ereditarietà**. Questo è il vero valore aggiunto di una tassonomia rispetto a un semplice elenco di fatti: evita ridondanza e permette inferenza automatica di proprietà non esplicitate.

Esempio analogo dalle slide: la tassonomia delle conifere, dove `Pinophyta ≡ Conifera` è la classe radice e si scompone in famiglie (Pinaceae, Araucariaceae, ..., Taxaceae, Cycadophyta).

### 2. Decomposizioni, disgiunzione, partizione

Quando si scompone una categoria C in sottocategorie, non basta l'intuizione che siano "separate": occorre **rendere esplicita** questa informazione al motore inferenziale con proprietà formali su un insieme di categorie S = {X1, ..., Xn}:

- **Disjoint(S)**: le categorie in S non hanno istanze in comune
  `∀Xi,Xj ∈ S, Xi ≠ Xj ⇒ Intersection(Xi, Xj) = {}`
- **ExhaustiveDec(S, C)**: ogni istanza di C appartiene ad almeno una delle categorie di S (decomposizione esaustiva)
  `∀I (Member(I, C) ⇔ ∃Xi Is-a(Xi, C) ∧ Member(I, Xi))`
- **Partition(S, C)**: S è sia disgiunto sia esaustivo rispetto a C
  `Partition(S, C) ⇔ Disjoint(S) ∧ ExhaustiveDec(S, C)`

Esempio: le famiglie delle Pinophyta costituiscono una partizione, perché per costruzione tassonomica sono disgiunte (nessuna specie appartiene a due famiglie) ed esaustive (ogni conifera appartiene a una famiglia).

### 3. Relazioni strutturali: Part-of e Bunch-of

Oltre a Is-a, un altro tipo naturale di conoscenza è quella **strutturale**, cioè "di cosa è fatta una cosa":

- `Part-of(Leg, Table)`: le gambe sono parte del tavolo
- `Part-of(Head, Body)`, `Part-of(Corolla, Flower)`, ecc.

**Part-of è transitiva**: `Part-of(X, Y) ∧ Part-of(Y, Z) ⇒ Part-of(X, Z)`.

Le relazioni strutturali comprendono anche predicati dipendenti dal dominio (`On-top`, `Implements`, ...) e permettono di catturare formalmente la struttura tipica di una categoria di oggetti, ad esempio:

```
Flower(x) ⇒ ∃Corolla, Stelo  Part-of(Corolla, x) ∧ Part-of(Stelo, x) ∧ On-top(Corolla, Stelo)
```

**Bunch-of** (mucchio) serve quando si vuole dire che un oggetto è composto da parti **senza specificare le relazioni fra queste**: `Bunch-of({Mela1, Mela2, Mela3})` indica il mucchio delle tre mele. Definizione: `∀x In(x, s) ⇒ Part-of(x, Bunch-of(s))`. Da notare: `s` non è una categoria ma un insieme di elementi, e `Bunch-of(s) = s`.

(Le slide trattano anche le **misure** — predicati per esprimere quantità puntuali, es. `Durata(d) = Ore(24)`, o ordinamenti come `Difficoltà(SISINT) > Difficoltà(BASIDATI)` — segnate come materiale di lettura, minore rilevanza per l'esame.)

### 4. T-box e A-box

Un'ontologia si struttura sempre in due parti:

- **T-box** (terminological box): la parte **generale/intensionale**, fatta di definizioni, specializzazioni e proprietà (le "regole" del dominio).
- **A-box** (assertional box): la parte **estensionale**, contiene fatti su istanze specifiche, che devono essere coerenti con la T-box.

Esempio: T-box → `Madre(X) ⇒ Donna(X)`; A-box → `Madre(Anna)`.

Questa distinzione è cruciale perché separa lo **schema concettuale** (cosa può esistere e come si relaziona) dai **dati concreti** (cosa esiste effettivamente), un po' come lo schema di un database rispetto ai suoi record.

### 5. Problematiche delle tassonomie/ontologie

- **Norma ed eccezioni**: molte proprietà valgono "di default" ma ammettono eccezioni (gli uccelli di solito volano, ma struzzi, pinguini, kiwi, emù no; i cani di solito hanno il pelo, ma il cane nudo peruviano no). Le eccezioni possono **cancellare** proprietà ereditate: una sottoclasse SC1 eredita la proprietà P della superclasse C; una sotto-sottoclasse SC2 può specializzarsi aggiungendo una proprietà Q; un'altra sotto-sottoclasse SC3 può invece essere un'**eccezione al default** e non avere P, pur essendo comunque sottoclasse di C.
- **Polisemia**: una stessa parola può denotare concetti diversi e appartenere ad alberi tassonomici differenti. Esempio: "cane" è sia un animale sia una costellazione (Canis Major) sia una persona vile sia un dente d'arresto meccanico. Il motore inferenziale non deve mischiare le tassonomie: non si vuole concludere che la costellazione Canis Major "ha il pelo". Il problema aperto è: **come identificare i concetti in modo univoco?** (è uno dei motivi per cui le ontologie del web semantico usano identificatori URI globalmente univoci, si veda oltre).

### 6. Dalla tassonomia all'ontologia

Una tassonomia, essendo un **albero** (ogni concetto ha un'unica super-classe diretta lungo la gerarchia Is-a), è un caso *particolare* e più limitato di struttura. Una base di conoscenza descrittiva può però assumere una forma più generale, in cui i concetti e le relazioni fra essi formano un **grafo** invece che un albero: questo insieme più generale di concetti e relazioni si chiama **ontologia** (o **rete semantica**).

> **Tassonomia vs Ontologia**: la tassonomia cattura *solo* le relazioni gerarchiche Is-a (e quindi ha una struttura ad albero); un'ontologia è più espressiva e può includere anche relazioni Part-of, relazioni di dominio specifiche (es. `haMoglie`, `ospitatoDa`), e in generale una rete arbitraria di concetti collegati da relazioni diverse (struttura a grafo). **Le tassonomie sono quindi un caso speciale di ontologia.**

I sistemi che usano ontologie seguono tipicamente lo schema: la **realtà/dati** viene astratta nell'**ontologia**, un **motore inferenziale** lavora sui fatti rappresentati e permette di **interrogare** il sistema e ottenere risposte.

**Tipi di interrogazione tipici su un'ontologia:**

1. Istanza appartiene a categoria? (*Fido è un mammifero?*)
2. Istanza gode di proprietà? (*Fido può volare?*)
3. Differenza fra categorie? (*Che differenza c'è fra rocce magmatiche e sedimentarie?*)
4. Identificazione di istanze (*Quali alberghi a tre stelle di Rimini offrono supporto tecnico ai ciclisti?*)

Queste interrogazioni sono spesso inserite in sistemi più ampi: categorizzazione di immagini, risposta a domande in linguaggio naturale, diagnosi medica da risultati di laboratorio, ecc.

### 7. Esempio applicativo: PROV (provenance)

PROV è un'ontologia del web semantico (W3C) che rappresenta, integra e traccia la **provenienza dei dati** (chi/cosa ha creato/modificato/usato una risorsa), utile ad esempio per verificare il rispetto della privacy o la liceità d'uso di materiale audio/video. I concetti chiave sono **Agente** (persona, organizzazione, software), **Attività** (uso/creazione di dati), **Entità** (dato/documento). Le slide mostrano un caso d'uso (evoluzione di un file di statistiche di crimini modificato da più giornalisti) codificato con predicati come `wasGeneratedBy`, `used`, `wasDerivedFrom`, `wasControlledBy`. Su una rappresentazione di questo tipo si possono automatizzare interrogazioni come "su cosa si basa questa risorsa?", "chi l'ha fatta?", "quali risorse derivano dalle stesse fonti?" (contenuto contrassegnato come facoltativo, utile solo per intuire un caso reale d'uso).

### 8. Semantic Web e linguaggi per rappresentare ontologie

Il **Semantic Web** (termine coniato da Tim Berners-Lee, Turing Award 2016) è l'estensione del web tradizionale in cui i contenuti pubblicati sono arricchiti da **metadati** che abilitano interpretazione, inferenza, interrogazione ed elaborazione automatica. I linguaggi sono standardizzati dal **W3C**.

**RDF (Resource Description Framework)**

- È il modello/linguaggio di rappresentazione **base** su cui poggiano altri linguaggi (OWL, SKOS per ontologie; FOAF per applicazioni sociali).
- La conoscenza è espressa tramite **triple** *soggetto – predicato – oggetto* (statement): il predicato mette in relazione soggetto e oggetto.
- Soggetto, predicato e oggetto sono **IRI** (internationalized resource identifier, tipo URL) — questo risolve proprio il problema di identificazione univoca dei concetti visto sopra (§5): ogni concetto ha un identificatore globale non ambiguo.
- **RDFS** (RDF Schema) permette di costruire tassonomie appoggiandosi a RDF.
- Un insieme di triple RDF forma un **grafo RDF**.
- Sintassi concreta: RDF è tipicamente serializzato in **XML** (`<rdf:RDF>...</rdf:RDF>`), ma esistono anche notazioni alternative come **Turtle** e **N3**.
- **SPARQL** è il linguaggio di interrogazione per dati RDF (analogo a SQL per i DB relazionali).

**OWL 2 (Web Ontology Language)**

Linguaggio dichiarativo del semantic web pensato specificamente per **definire ontologie** tramite classi, proprietà, individui e valori. Le ontologie OWL possono essere pubblicate sul web e riferite da altre ontologie per costruire basi di conoscenza più ricche e componibili.

OWL modella la conoscenza con tre tipi di elementi:

- **Entità**: elementi atomici che riferiscono oggetti del mondo reale (individui, classi, proprietà) — corrispondono a costanti (individui), predicati unari (classi), predicati binari (proprietà) della logica del primo ordine.
- **Assiomi**: affermazioni di base (es. `ClassAssertion(:Persona :Maria)` = "Maria è una Persona").
- **Espressioni**: combinazioni di entità che costruiscono descrizioni complesse (es. intersezione di "medico" e "donna" per ottenere "donna medico").

Costrutti principali (in sintassi *Functional-Style*, una delle possibili sintassi OWL insieme a RDF/XML, Turtle, Manchester):

- `Declaration(NamedIndividual(:Maria))`, `Declaration(Class(:Persona))`, `Declaration(ObjectProperty(:donna))`
- `ClassAssertion(:Persona :Maria)`: Maria è istanza di Persona
- `SubClassOf(:Madre :Donna)`: relazione di sottoclasse (Is-a)
- `EquivalentClasses(:Persona :Umano)`: equivalenza fra classi (sottoclasse reciproca)
- `DisjointClasses(:Donna :Uomo)`: le classi non condividono istanze
- `ObjectPropertyAssertion(:haMoglie :Giovanni :Maria)`: lega due individui con una proprietà
- `SubObjectPropertyOf(:haMoglie :haConiuge)`: gerarchia fra proprietà
- `ObjectPropertyDomain` / `ObjectPropertyRange`: dominio e codominio di una proprietà
- Costruttori per classi complesse: `ObjectIntersectionOf`, `ObjectUnionOf`, `ObjectComplementOf`
- Quantificazione: `ObjectSomeValuesFrom` (esistenziale, es. Genitore = chi ha *almeno* un figlio Persona), `ObjectAllValuesFrom` (universale, es. PersonaFelice = tutti i figli sono felici, vero anche vacuamente se non si hanno figli)
- **Datatype**: per vincolare i valori delle proprietà a un insieme (es. `DataPropertyRange(:haEta xsd:nonNegativeInteger)`)

**OWL 2 non è un framework per basi di dati**, anche se il vocabolario a volte richiama quello dei DB. Differenze semantiche fondamentali:

- DB: **closed world assumption** (un fatto non presente è falso) — OWL 2: **open world assumption** (un fatto non presente è semplicemente *sconosciuto/mancante*, non falso)
- OWL non impone che le uniche proprietà di un individuo siano quelle della sua classe
- Classi e proprietà possono avere definizioni multiple, distribuite anche su documenti diversi

OWL 2 non è un linguaggio di programmazione ma un linguaggio di **rappresentazione dichiarativa**: su di esso si applicano programmi di *reasoning* per rispondere a query.

**FOAF (Friend Of A Friend)**: ontologia per collegare persone sul web, con classi come `Agent`, `Person`, `Group`, `Organization` e proprietà come `name`, `knows`, `age`, `mbox`.

### 9. Costruire un'ontologia: metodologia pratica

Data l'esigenza tipica (esporre dati di un DB in un formalismo su cui fare inferenza), il procedimento è:

1. **Identificazione dei concetti**: elencare i sostantivi rilevanti nel DB, dare a ciascuno etichetta e descrizione, poi (in una seconda passata) identificare le sottoclassi. Esempio (dominio canili): Cane (specie), Bassotto (sottospecie), Cucciolo (età ≤ 6 mesi), Orfano, TagliaMedia, Struttura (canile), ecc.
2. **Identificazione delle proprietà**: elencare le relazioni del DB (tipicamente verbi), con etichetta e descrizione. Esempio: `ospitatoDa`, `coloreManto`, `haDisabilità`, `haTatuaggio`, `haMicrochip`.
3. **Riuso**: verificare se esistono ontologie già definite riutilizzabili (anche parzialmente), es. la *Wildlife Ontology* della BBC.
4. **Scrittura formale**: codificare quanto sopra in un linguaggio per ontologie (RDF o OWL) — si ottiene la **T-box**.
5. **Annotazione dei dati**: si popola la **A-box** con le istanze concrete.
6. **Validazione e raffinamento** della base di conoscenza.
7. **Costruzione di un sistema di interrogazione**: applicazioni che sfruttano ontologia e dati annotati appoggiandosi a motori inferenziali (esempio nelle slide: un sistema che sostituisce consigli statici testuali su quale cane adottare con un sistema interrogabile basato sull'ontologia).

**Strumenti citati**: Protégé (editor/IDE per KB, Stanford), reasoner (CEL, FaCT++, HermiT, Pellet, RacerPro), Alignment API, OWLTools, Sesame, Tripliser, W3C RDF Validator, Apache Jena, AllegroGraph (triplestore).

**Applicazioni citate**: Linked (Open) Data, DBpedia, CreativeCommons (licenze in RDF), FOAF, Press Association (notizie annotate semanticamente), beni culturali, musei, ambito legale/medico (es. Genoma), geografico, meteorologico, curricula transnazionali.

### 10. Relazioni fra ontologie

Quando esistono più ontologie (magari sviluppate indipendentemente) che descrivono domini simili o sovrapposti, è utile classificare formalmente il tipo di relazione fra loro:

- **Identical**: O1 e O2 sono **la stessa** ontologia (es. un'ontologia e la sua copia su un disco mirror — identità letterale, non solo concettuale).
- **Equivalent**: O1 e O2 condividono **vocabolario e assiomatizzazione** ma sono espresse in **linguaggi differenti** (es. la stessa concettualizzazione scritta una volta in **SKOS** e una volta in **RDF**). Concettualmente dicono la stessa cosa, cambia solo la "lingua" formale.
- **Extension**: O1 **estende** O2 quando tutti i simboli definiti in O2 sono preservati in O1 insieme a proprietà e relazioni, ma **non vale il viceversa** (O1 è O2 + qualcosa in più).
- **Weakly-Translatable**: data una ontologia sorgente Osource e una destinazione Odest, è possibile tradurre espressioni di Osource in espressioni di Odest, ma **con perdita di informazione**.
  *Esempio*: Osource ha `Fruit → {Agrume → {Citron, Orange, Pamplemousse}, Pomme, Poire}`; Odest ha solo `Fruit → {Apple, Lemon, Orange}`. Il mapping `Pomme→Apple, Citron→Lemon, Orange→Orange, Fruit→Fruit` funziona ma si perde l'informazione su Poire, Pamplemousse e sulla sotto-categorizzazione di Agrume.
- **Strongly-Translatable**: Osource è fortemente traducibile in Odest quando (a) il vocabolario è **totalmente mappabile**, (b) l'assiomatizzazione di Osource **vale** in Odest, (c) **non c'è perdita di informazione**, (d) **non si introducono inconsistenze**. È una traduzione "fedele", anche se Odest può comunque contenere concetti (es. Pamplemousse) che non hanno corrispondente in Osource — la condizione riguarda la direzione Osource→Odest, non il viceversa.
- **Approx-Translatable**: Osource è Weakly-Translatable in Odest **e** possono essere introdotte **inconsistenze**. Accade tipicamente quando concetti che dovrebbero corrispondere sono solo *affini*, non identici. Esempio dato: il coriandolo, a seconda della tradizione culinaria, è visto come affine al prezzemolo (si usano le foglie) o al pepe (si usano i semi) — è la stessa pianta ma con proprietà ontologiche differenti a seconda del riferimento.

L'esercizio pratico di costruire l'allineamento (*ontology alignment* / *matching*) fra due ontologie O1 e O2 consiste proprio nell'individuare queste corrispondenze fra concetti, che **in generale sono imperfette** (slide con esempio "Cosa/Oggetto, Macchina/Locomotore/Veicolo/Treno/Automobile..." per illustrare come concetti simili ma non identici in due tassonomie diverse possano essere allineati parzialmente).

Un contesto applicativo citato: gli standard **FIPA** (Foundation for Physical/Intelligent Agents) per agenti software prevedono un *ontology agent* dedicato che offre servizi di discovery di ontologie pubbliche, traduzione fra ontologie diverse, e risposta a query sulle differenze fra termini/ontologie — utile quando due agenti comunicano e devono condividere/riconciliare i rispettivi vocabolari concettuali.

> ❓ **Domanda d'esame:** Qual è la differenza fra una tassonomia e un'ontologia?
>
> Una tassonomia è una struttura **gerarchica ad albero** costruita esclusivamente tramite relazioni Is-a (sottoclasse): ogni concetto eredita le proprietà del proprio "genitore" nella gerarchia. Un'ontologia è un concetto più generale: un **grafo** di concetti collegati da relazioni di natura diversa (Is-a, Part-of, relazioni di dominio come `haMoglie` o `ospitatoDa`, ecc.), non necessariamente organizzato ad albero. Ogni tassonomia è quindi un caso particolare (più semplice) di ontologia, ma non vale il viceversa.

> ❓ **Domanda d'esame:** Perché Is-a e Part-of non bastano a rappresentare qualunque tipo di conoscenza?
>
> Perché sono relazioni essenzialmente **statiche**, adatte a descrivere *cosa è* qualcosa (categorizzazione) o *di cosa è fatto* qualcosa (composizione), ma non catturano il concetto di **azione** e di **cambiamento nel tempo**: non permettono di rappresentare che un agente compie un'azione che trasforma lo stato del mondo (esempio delle slide: l'inferenza ontologica pura non basta a decidere/rappresentare l'attraversare la strada). Per questo serve un formalismo diverso, orientato alle azioni e agli stati: il **Situation Calculus**, che è il ponte verso la Parte B — la pianificazione.

---

## Parte B: Pianificazione automatica

### 1. Dalle ontologie alla pianificazione: perché serve un nuovo formalismo

Le relazioni Is-a e Part-of descrivono conoscenza statica. Molte applicazioni reali dei sistemi di inferenza, invece, richiedono di **decidere quali azioni eseguire** per raggiungere un obiettivo: questo è il compito della **pianificazione** (planning).

> **Pianificare** significa costruire una **sequenza di azioni** che, applicata a partire da uno stato iniziale, soddisfa un certo obiettivo (goal). Un problema di pianificazione specifica: gli elementi di interesse del mondo (stato), le azioni disponibili, e l'obiettivo da raggiungere.

Il mondo è descritto da un insieme di variabili, tipicamente nel linguaggio **PDDL** (*Planning Domain Definition Language*, lo standard de facto per descrivere problemi di pianificazione). Uno **stato** è una congiunzione di **atomi ground** (senza variabili né funzioni), es. `At(Camion1, Bari) ∧ At(Camion2, Lecce)`. Le azioni sono descritte in modo **schematico** (parametriche) e hanno un impatto **limitato** sul mondo: in un dato stato solo un sottoinsieme di azioni è applicabile, e di queste ne viene scelta ed eseguita **una sola per volta**. Un aspetto pratico rilevante: se l'azione scelta viene davvero eseguita nel mondo reale, **potrebbe non essere possibile fare backtracking** (a differenza della ricerca "sulla carta").

### 2. Differenza rispetto alla ricerca classica

Nella ricerca nello spazio degli stati "classica" (vista in altri moduli, es. A*), si cerca un cammino fra stato iniziale e stato goal muovendosi fra stati rappresentati in modo essenzialmente atomico o con poca struttura interna, valutando ogni azione/operatore individualmente rispetto allo stato corrente.

Nella pianificazione, invece:

- Gli stati e le azioni hanno una **rappresentazione logica strutturata** (predicati, precondizioni, effetti), non atomica: questo permette ragionamenti più espressivi (es. dedurre che un'azione non è applicabile senza dover enumerare esplicitamente lo stato).
- L'obiettivo è tipicamente **complesso** e viene tipicamente **scomposto in sottoobiettivi** (si veda sotto), sfruttando la struttura logica per decidere l'ordine e l'interazione fra le azioni necessarie a soddisfare ciascun sottoobiettivo.
- Si presta esplicitamente attenzione al problema di **rappresentare gli effetti delle azioni** (assiomi di applicabilità/effetto, frame problem — vedi sotto), aspetto che nella ricerca "classica" è dato per scontato tramite la funzione successore.

### 3. Il Situation Calculus: fondamento logico della pianificazione

Il **Situation Calculus** è la rappresentazione logica (in FOL) su cui si basa storicamente il ragionamento su azioni. Introduce i concetti di:

- **Azione**: qualcosa che viene compiuto e influenza il mondo. In logica non è un predicato ma una **funzione** che restituisce un oggetto del dominio (un'azione è quindi un oggetto "intangibile"). Esempio: `Move(R, L1, L2)` denota l'azione di spostare R da L1 a L2.
- **Situazione**: lo stato risultante dall'esecuzione di una sequenza di azioni.
- **Fluente**: proprietà/relazione che può **cambiare valore** (fluire) con l'esecuzione delle azioni; ha sempre come parametro la situazione, es. `Holds(At(R, Loc), s)`, `Adjacent(R1, R2, s)`.
- **Predicato/funzione atemporale (eterno)**: il cui valore **non** dipende dalle azioni eseguite.

Il tempo non è rappresentato esplicitamente, ma scandito dalla sequenza di eventi: si parte da una situazione iniziale S0 e si applicano azioni a1, a2, a3... generando S1, S2, S3...

La funzione `Do(Azioni, S)` restituisce la situazione raggiunta applicando la sequenza `Azioni` a partire da S:

```
Do([], s) = s
Do([a | resto], s) = Do(resto, Risultato(a, s))
```

Nota fondamentale: **due situazioni sono identiche solo se derivano dallo stesso stato iniziale tramite la stessa sequenza di azioni** — una situazione è cioè identificata dalla sua "storia":
`Do(Azioni1, S1) = Do(Azioni2, S2) ⇔ (Azioni1=Azioni2) ∧ (S1=S2)`.

Tramite `Do` un agente può fare **proiezione**, cioè ragionare sugli effetti futuri delle azioni: verificare se un piano attraversa solo situazioni con certe proprietà (vincolo da mantenere lungo tutto il percorso, es. "non rimanere mai a secco di carburante"), oppure pianificare per raggiungere una situazione con una proprietà finale specifica (goal, es. "assemblare la bicicletta").

**Rappresentazione delle azioni** tramite due tipi di assiomi:

- **Assioma di Applicabilità**: `∀params,s  Applicable(Action(params), s) ⇔ Precond(params, s)` — un'azione è applicabile in una situazione se e solo se valgono le sue precondizioni. Esempio: `Applicable(go(X,Y), S) ⇔ At(X,S) ∧ Adjacent(X,Y)`.
- **Assioma di Effetto**: `∀params,s  Applicable(Action(params), s) ⇒ Effects(params, Result(Action(params), s))` — specifica cosa diventa vero nello stato risultante. Esempio: `Applicable(go(X,Y),S) ⇒ At(Y, Result(go(X,Y),S))`.

**Esempio guida — mondo dei blocchi**: l'azione `Move(X,Y,Z)` sposta il blocco X da Y a Z.

- Applicabilità: `Applicable(Move(x,y,z),s) ⇔ Clear(x,s) ∧ Clear(z,s) ∧ On(x,y,s) ∧ x≠z ∧ y≠z ∧ x≠Table` (X e Z devono essere liberi in cima, X deve essere effettivamente su Y, non si può spostare un blocco su se stesso, né "sopra" il tavolo con la stessa semantica di un blocco).
- Effetto: `Applicable(Move(x,y,z),s) ⇒ On(x,z,Result(...)) ∧ Clear(y,Result(...))`.

Da stato iniziale + assiomi di applicabilità + assiomi di effetto (la "KB") si possono **derivare** nuovi fatti sullo stato risultante, es. dopo `Move(A,B,D)` si deriva `On(A,D,...)` e `Clear(B,...)`.

### 4. Il Frame Problem

> **Frame problem (problema della cornice)**: le azioni hanno tipicamente un impatto **limitato** sul mondo — come rappresentare tutto ciò che **non** viene modificato da un'azione?

Il problema è che dalla sola conoscenza di stato iniziale + assiomi di applicabilità/effetto **non si può derivare** ciò che rimane invariato: si può ragionare su cosa è cambiato, ma nulla dice esplicitamente al sistema che il resto è rimasto com'era. Esempio: dopo `Move(A,B,D)`, sapevamo `On(B,C,s)` nello stato iniziale, ma nulla garantisce che il sistema possa inferire `On(B,C,s')` nello stato risultante s', a meno di dirglielo esplicitamente.

Due soluzioni proposte nelle slide:

1. **Enumerare esplicitamente ciò che non cambia** (assiomi di frame): per ogni azione e per ogni fluente non toccato da quell'azione si scrive un assioma tipo
   `∀params,vars,s  fluent(vars,s) ∧ params≠vars ⇒ fluent(vars, Result(Action(params),s))`
   **Problema pratico**: bisogna scrivere un assioma di frame per **ogni combinazione azione × fluente non toccato** — con molte proprietà (colore, materiale, ecc.) il numero di assiomi esplode rapidamente, rendendo l'approccio poco scalabile.

2. **Evitare l'enumerazione con un assioma di stato successore**: si introduce un unico schema generale che dice al sistema che ciò che non è esplicitamente indicato come effetto rimane implicitamente vero:
   `Azione applicabile ⇒ (fluente vero nella situazione risultante ⇔ (l'azione lo rende vero ∨ (era vero ∧ l'azione non l'ha reso falso)))`
   Questo compatta in un solo schema, per ciascun fluente, sia gli effetti positivi sia la "persistenza per default" di ciò che non è toccato — evitando l'esplosione combinatoria della soluzione 1.

Infine, il Situation Calculus è completato da assiomi di **unique action names**: azioni con nomi diversi sono oggetti diversi (`Ai(x,...) ≠ Aj(y,...)`), e due usi dello stesso nome d'azione sono uguali se e solo se hanno argomenti uguali (`A(x1,...,xn) = A(y1,...,yn) ⇒ x1=y1 ∧ ... ∧ xn=yn`) — condizioni tecniche necessarie perché l'inferenza logica funzioni correttamente senza ambiguità.

### 5. Perseguire goal complessi: scomposizione in sottogoal

L'approccio tipico alla pianificazione di un obiettivo complesso è **scomporlo in sottoobiettivi** e perseguirli, in linea di principio, uno alla volta.

**Esempio (mondo dei blocchi)**: stato iniziale con A e B sul tavolo, C sopra B (letto dalle slide: "A B" sul tavolo con C sopra uno di essi); goal = "A su B su C" (pila A-B-C). Il goal si scompone in due sottogoal:

- Sottogoal 1: A su B
- Sottogoal 2: B su C

L'idea è risolvere prima un sottogoal, poi l'altro, in sequenza.

### 6. L'anomalia di Sussman: quando i sottogoal interagiscono

> **Non sempre il perseguimento dei sottoobiettivi è sequenzializzabile in modo indipendente.** Questo è il fenomeno noto come **anomalia di Sussman**, un classico esempio di *interazione fra sotto-obiettivi* nella pianificazione.

Stato iniziale: C sul tavolo da solo, A sopra B (pila A/B) sul tavolo. Goal: pila A su B su C.

Il problema è che i due sottogoal ("A su B" e "B su C") sono **in conflitto** se perseguiti nell'ordine sbagliato:

- Se perseguo prima **"B su C"**: per liberare B devo spostare A altrove, quindi **disfo** la pila A/B che già avevo parzialmente — per ottenere B su C devo disfare la struttura A/B.
- Se perseguo prima **"A su B"**: metto A sopra B, ma poi per ottenere "B su C" dovrei spostare l'intera pila A/B, e quindi devo di nuovo **disfare** ciò che avevo appena costruito (togliere A da sopra B per poter mettere B su C, per poi rimettere A sopra B).

In entrambi i casi, risolvere un sottogoal **"disfa"** (annulla) i progressi fatti per l'altro: la scomposizione **sequenziale e indipendente** in sottogoal non funziona qui, perché i sottogoal **non sono indipendenti** — ci sono interazioni fra loro (l'ordine di esecuzione conta, e un ordine "ingenuo" porta a lavoro ripetuto o a cicli).

**Soluzione — interleaving dei passi**: la soluzione efficiente richiede di **intercalare** (fare interleaving) i passi provenienti dai due sottopiani, invece di completare un sottogoal per intero prima di iniziare l'altro. Sequenza corretta (una delle possibili):

1. Sposto C dal tavolo... (passo verso "B su C", cioè libero/posiziono C)
2. Sposto A da sopra B (passo di preparazione)
3. Sposto B su C (passo di "B su C")
4. Sposto A su B (passo di "A su B")

In sintesi: si esegue prima l'azione che porta B su C (dopo aver tolto A da B), e **solo dopo** si posiziona A su B, ottenendo la pila finale A-B-C senza dover disfare nulla. Questo dimostra che un planner efficace deve poter **intrecciare** le sequenze di azioni relative a sottogoal diversi, non semplicemente concatenarle.

### 7. Limiti pratici del Situation Calculus

- Il Situation Calculus ha permesso di usare la **logica del primo ordine (FOL)** per formalizzare rigorosamente il problema della pianificazione, ed è stato storicamente **fondamentale** per definirne le basi teoriche.
- Nella **pratica**, però, **non è molto usato**, perché **non esistono euristiche efficienti** che guidino efficacemente la ricerca della soluzione nello spazio (molto grande) delle sequenze di azioni possibili. I planner moderni usano rappresentazioni più specializzate (es. PDDL con algoritmi dedicati, planning graph, euristiche ad hoc) proprio per rendere la ricerca trattabile.
- La pianificazione (planning) come argomento a sé stante viene approfondita nel corso magistrale **"IA e Laboratorio"** della laurea in Intelligenza Artificiale e Sistemi Informatici — qui è trattata solo nei suoi fondamenti concettuali e logici.

> ❓ **Domanda d'esame:** Cos'è l'anomalia di Sussman e cosa dimostra?
>
> È l'esempio classico (mondo dei blocchi: stato iniziale A su B, C isolato; goal: pila A su B su C) che mostra come la scomposizione di un obiettivo complesso in sottoobiettivi **non sia in generale risolvibile perseguendo i sottoobiettivi in sequenza indipendente**: risolvere un sottogoal (es. "B su C") può richiedere di disfare i progressi fatti per un altro sottogoal (es. "A su B") già raggiunto, e viceversa. Dimostra quindi che i sottoobiettivi possono **interagire** fra loro, e che un planner corretto deve poter fare **interleaving** dei passi provenienti da piani diversi invece di eseguirli a blocchi separati e sequenziali.

> ❓ **Domanda d'esame:** Cos'è il frame problem e come si risolve?
>
> È il problema di rappresentare esplicitamente **ciò che un'azione NON modifica**, dato che dalla sola conoscenza di stato iniziale, assiomi di applicabilità e assiomi di effetto non si può derivare automaticamente la persistenza delle proprietà non toccate da un'azione. Si risolve in due modi: (1) enumerando esplicitamente un assioma di frame per ogni coppia azione/fluente non toccato (soluzione corretta ma che esplode combinatoriamente al crescere di azioni e proprietà); (2) tramite un **assioma di stato successore** unico per fluente, che stabilisce per default che un fluente resta vero nella situazione risultante se lo era prima e l'azione non lo ha reso falso (o se l'azione lo rende vero) — soluzione compatta che evita l'enumerazione esplicita.

---

## Riepilogo e punti chiave

**Parte A — Tassonomie e Ontologie**

- **Tassonomia** = organizzazione gerarchica (ad albero) di concetti tramite relazioni **Is-a** (sottoclasse): le istanze di una sottoclasse ereditano le proprietà della superclasse, evitando ridondanza.
- Su un insieme di sottocategorie si possono definire formalmente le proprietà **Disjoint**, **ExhaustiveDec**, **Partition** per rendere esplicita al motore inferenziale l'organizzazione voluta.
- Relazioni **strutturali** (Part-of, transitiva; Bunch-of per aggregati senza struttura interna) affiancano le relazioni Is-a per descrivere la composizione degli oggetti.
- Ogni ontologia si divide in **T-box** (schema/definizioni, intensionale) e **A-box** (istanze/fatti, estensionale).
- Problemi aperti delle tassonomie: gestire **eccezioni** alla norma (cancellazione di proprietà ereditate) e la **polisemia** (una parola → concetti/alberi tassonomici diversi).
- Un'**ontologia** generalizza la tassonomia: da albero (solo Is-a) a **grafo** (relazioni arbitrarie, incluse Part-of e relazioni di dominio). Ogni tassonomia è un'ontologia, non viceversa.
- Il **Semantic Web** standardizza (W3C) linguaggi per ontologie: **RDF** (triple soggetto-predicato-oggetto, IRI come identificatori univoci, grafo RDF, sintassi XML/Turtle/N3), **RDFS**, **OWL 2** (classi, proprietà, individui, assiomi come SubClassOf/EquivalentClasses/DisjointClasses, quantificatori esistenziale/universale), **SPARQL** (query), **FOAF** (ontologia sociale).
- Costruire un'ontologia: identificare concetti → identificare proprietà → riusare ontologie esistenti → formalizzare (T-box) → annotare dati (A-box) → validare → costruire sistema di interrogazione.
- OWL 2 **non** è un DB: usa **open world assumption** (a differenza della closed world assumption dei DB) e ammette conoscenza incompleta/distribuita.
- **Relazioni fra ontologie**: Identical (stessa ontologia), Equivalent (stesso contenuto, linguaggio diverso, es. SKOS vs RDF), Extension (una include l'altra + di più), Weakly-Translatable (traduzione con perdita), Strongly-Translatable (traduzione fedele, senza perdita né inconsistenze), Approx-Translatable (traduzione debole con possibili inconsistenze per concetti solo affini). Il matching/allineamento fra ontologie è in generale imperfetto.
- Is-a e Part-of **non bastano** a rappresentare le **azioni**: serve un formalismo dedicato → ponte verso la pianificazione.

**Parte B — Pianificazione automatica**

- **Pianificare** = costruire una sequenza di azioni che porta da uno stato iniziale a uno stato che soddisfa il goal; si differenzia dalla ricerca classica per la rappresentazione logica strutturata di stati/azioni (precondizioni/effetti) e per l'attenzione a scomposizione e interazione dei sottoobiettivi.
- Il **Situation Calculus** fornisce il fondamento logico (FOL): Azione (funzione), Situazione, Fluente (proprietà parametrizzata sulla situazione), predicati atemporali; funzione `Do(Azioni, S)` per il concatenamento di azioni; assiomi di **Applicabilità** (precondizioni) e di **Effetto** (conseguenze), illustrati con l'esempio del mondo dei blocchi (`Move(X,Y,Z)`).
- Il **frame problem** riguarda la rappresentazione di ciò che un'azione **non** modifica: risolvibile per enumerazione esplicita (poco scalabile) o con l'**assioma di stato successore** (soluzione compatta standard).
- La scomposizione di un goal in **sottogoal** è l'approccio base alla pianificazione, ma i sottogoal possono **interagire**: l'**anomalia di Sussman** è l'esempio canonico in cui risolvere un sottogoal disfa i progressi di un altro, e la soluzione richiede **interleaving** dei passi dei diversi (sotto-)piani anziché una sequenza rigida.
- Il Situation Calculus è stato storicamente fondamentale ma è **poco usato in pratica** per mancanza di euristiche efficienti; la pianificazione vera e propria è approfondita in corsi successivi (IA e Laboratorio, magistrale).
