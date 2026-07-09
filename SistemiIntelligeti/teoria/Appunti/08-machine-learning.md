# Modulo 8: Machine Learning — Classificazione, Alberi di Decisione, Reti Neurali

> Materiale parzialmente tratto dalle slide di Cristina Baroglio, in parte associate al libro *Introduction to Data Mining* di Tan, Steinbach e Kumar.

## Il problema della classificazione

### Le classi non sono "naturali"

Un punto concettuale che l'insegnamento sottolinea fin da subito: ***le classi non esistono in natura***. Non sono insite negli esempi, non sono raggruppamenti naturali inequivocabili: sono **definite a tavolino** da chi costruisce il sistema, in funzione dello scopo per cui si vuole costruire il predittore. Lo stesso insieme di oggetti (es. dei fiori) può essere raggruppato per colore, per forma, per "vero/finto" — dipende da cosa interessa a chi progetta il classificatore. Questo è un'osservazione importante perché ricorda che **il sistema non ha altra conoscenza oltre ai dati** e impara esattamente quello che c'è nei dati per come sono etichettati, non quello che il progettista *pensa* di aver messo nei dati.

### Definizione del problema

Dati:

- **Esempi** (istanze/record): gli oggetti da classificare (es. fiori, animali)
- **Categorie o classi**: le etichette di appartenenza (es. mammifero/rettile/pesce)

Obiettivo: costruire una **rappresentazione astratta (modello)** che permetta di associare correttamente nuove istanze alla classe (o alle classi) di appartenenza.

Si parla di **apprendimento supervisionato** quando gli esempi da cui si astraggono le definizioni delle classi hanno già associata la classe corretta (l'etichetta).

Il problema si scompone in tre sotto-problemi:

1. **Rappresentazione dei dati**
2. **Analisi dei dati e costruzione delle definizioni** (il modello)
3. **Utilizzo della conoscenza acquisita**

### Schema generale: training set, modello, test set

```
DATI TRAINING SET  --induzione-->  MODELLO: classe = f(descrizione)  --deduzione-->  CLASSE
                                          ↑
DATI TEST SET  ------------------------->|  (usato per la VALUTAZIONE del modello)
```

- **Training (learning) set**: la collezione di dati usati per l'apprendimento. Ogni istanza è una tupla `(x, y)` dove `x` è una tupla di valori di attributi descrittivi e `y` è la classe di appartenenza.
- Il processo di **induzione** (dai dati al modello) costruisce il modello partendo dal training set.
- Il processo di **deduzione** applica il modello a nuove descrizioni per ottenerne la classe.
- Il **test set** serve a valutare la bontà del modello appreso, applicandolo a dati non usati in fase di apprendimento e confrontando la classe predetta con quella reale.
- Una volta validato, il modello viene messo in **uso** per classificare nuovi dati.

Esempio di training set (dataset zoo-like): ogni riga è un animale (istanza), le colonne sono attributi descrittivi (temperatura corporea, copertura della pelle, viviparo, ecc.) e l'ultima colonna è la **classe target** (es. mammifero, rettile, pesce, uccello, anfibio).

Come classe si usano tipicamente attributi binari (sì/no, vero/falso) oppure etichette nominali categoriche (es. mammifero, pesce, ...).

### Modello predittivo vs modello descrittivo

| Modello predittivo | Modello descrittivo |
|---|---|
| Usato per predire la classe di istanze ignote, non viste in fase di apprendimento | Usato come strumento esplicativo che evidenzia quali caratteristiche distinguono le categorie |
| Es. data la descrizione di una salamandra si applicano le regole apprese per decidere la classe | Esprime sinteticamente delle descrizioni senza dover ragionare sugli esempi grezzi (es. "i mammiferi hanno sangue caldo e di solito non sono acquatici") |

### Valutazione: matrice di confusione, accuratezza, error rate

La qualità di un modello si valuta sperimentalmente: lo si usa per classificare le istanze del test set e si confronta l'esito con la classe reale.

**Matrice di confusione** (caso a 2 classi):

|  | classe predetta 1 | classe predetta 2 |
|---|---|---|
| **classe reale 1** | f11 (corretto) | f12 (errore) |
| **classe reale 2** | f21 (errore) | f22 (corretto) |

- **Accuratezza** = (f11 + f22) / (f11 + f22 + f12 + f21) — predizioni corrette su predizioni totali
- **Error rate** = (f12 + f21) / (f11 + f22 + f12 + f21) — predizioni sbagliate su predizioni totali

Esempio numerico (lattina vs altro oggetto): accuratezza = (18+19)/40 = 92.5%, error rate = 3/40 = 7.5%.

### Matrice dei costi

Non tutti gli errori hanno lo stesso peso. La **matrice dei costi** assegna un costo a ciascuna cella della matrice di confusione (costi degli errori e costi delle valutazioni corrette, che possono anche essere negativi, cioè un guadagno).

Esempio classico: è più grave dire a un malato che è sano (falso negativo, costoso) o dire a una persona sana che è malata (falso positivo, meno grave ma comunque un costo)? Il costo complessivo si calcola sommando, cella per cella, `costo_ij × frequenza_ij` della matrice di confusione (es. Costo = -1×18 + 50×2 + 10×1 + 0×19 = 92).

> ❓ **Domanda d'esame:** perché un'accuratezza del 99.9% non è automaticamente sinonimo di "ottimo classificatore"?
> **Risposta:** perché l'accuratezza va sempre letta insieme alla distribuzione delle classi nel dataset. Se il learning set è fortemente sbilanciato (es. 9990 istanze di classe A e solo 10 di classe B), un classificatore banale che risponde sempre "classe A" (regola `if TRUE then A`) ottiene un'accuratezza del 99.9% pur non avendo imparato nulla di utile: non ha individuato nessun pattern discriminante, si limita a sfruttare lo sbilanciamento delle classi. Bisogna quindi guardare anche altre metriche (matrice di confusione completa, per-classe) e la composizione del dataset.

### Insidie pratiche nella costruzione del classificatore

Alcuni errori tipici nella raccolta/uso dei dati (esempio guida: riconoscere "frutta" da altre cose usando solo foto di mele → il modello impara a riconoscere solo mele, non la frutta in generale). Cause tipiche:

- **Dati difficili da reperire** → si usano dataset di comodo, non rappresentativi
- **Fretta / risorse limitate** disponibili (es. usare solo un archivio fotografico locale)
- **Bias mentale** di chi costruisce il dataset (se vivo circondato da meleti, non mi viene naturale includere uva o ciliegie)
- **Attribuire all'algoritmo capacità umane**: un umano generalizza usando moltissima conoscenza di base senza accorgersene (es. sa che un frutto nasce dall'impollinazione di un fiore); un algoritmo non ha questa conoscenza, impara solo dai dati che vede.

Applicazioni ad alto impatto in cui questi errori sono particolarmente rischiosi: riconoscimento facciale, concessione di mutui, assicurazioni sanitarie, applicazioni militari (riconoscimento automatico di bersagli), agricoltura di precisione (see and spray). Da qui il tema della **responsabilità etica**: nel caso della guida autonoma (variante del *trolley problem*), chi è responsabile della decisione presa da un agente autonomo? Si parla di *problem of the many hands*: la responsabilità è distribuita fra molti attori (progettisti, produttori, chi addestra il modello, chi lo utilizza), rendendo difficile individuare un singolo responsabile.

### Rote learning (apprendimento meccanico) — un "non-modello"

Prima di introdurre gli alberi di decisione, le slide presentano il *rote learning* come caso limite/degenere di apprendimento:

- **Strategia**: memorizzare semplicemente tutte le istanze del training set. Non esiste un vero modello: il sistema "ricorda" i casi ma non generalizza.
- **Uso**: data una nuova istanza, cerca un'istanza identica in memoria; se la trova, restituisce la classe corrispondente.
- Se non trova un'istanza identica, cerca istanze **simili** (misura di distanza = misura di similitudine, "vicino = simile"):
  - se le istanze simili trovate hanno tutte la stessa classe, quella è l'output;
  - se le classi sono diverse, serve una strategia di composizione, ad esempio:
    - **votazione a maggioranza**: ogni corrispondenza vale un voto, vince la classe più votata;
    - **votazione pesata**: il peso del voto dipende dalla distanza fra le istanze (più vicino = peso maggiore). I pesi vengono calcolati, usati e poi dimenticati (non sono persistenti, a differenza dei pesi di una rete neurale).

Questo approccio anticipa concettualmente algoritmi come k-NN, ma qui serve soprattutto a introdurre il concetto di **generalizzazione**: algoritmi di apprendimento diversi producono modelli di tipo diverso (alberi di decisione → albero; sistemi a regole → insiemi di regole if-then; reti neurali → matrici di numeri; apprendimento per rinforzo → distribuzioni di probabilità e matrici di numeri).

---

## Alberi di decisione

### Cosa sono

Gli alberi di decisione (*decision tree*, DT) sono strumenti di supporto alle decisioni basati su modelli strutturati ad albero, usati storicamente per definire strategie mirate al raggiungimento di un obiettivo (es. la struttura di navigazione di un negozio online: "ti interessa un libro, un film o un gioco?").

Applicati alla classificazione: si induce da esempi un albero di decisione che, dato un nuovo record, permette di predirne la classe seguendo un percorso di test sui valori degli attributi fino a una foglia.

### Struttura

- **Nodi interni**: rappresentano un **test** su un attributo descrittivo; da ogni nodo interno partono rami corrispondenti ai possibili esiti/valori del test.
- **Foglie**: rappresentano una **decisione**, cioè l'assegnazione a una classe.
- Un percorso dalla radice a una foglia corrisponde a una sequenza di scelte/test e porta a una conclusione (classe).

Esempio concreto — dataset **Iris** (3 classi: *setosa*, *versicolor*, *virginica*; attributi continui: petal width, petal length, sepal width, sepal length):

```
Petal width ≤ 0.6?
├── sì → IRIS SETOSA
└── no → Petal width ≤ 1.7?
          ├── no → IRIS VIRGINICA
          └── sì → Petal length ≤ 4.9?
                    ├── sì → IRIS VERSICOLOR
                    └── no → Petal width ≤ 1.5?
                              ├── sì → IRIS VIRGINICA
                              └── no → IRIS VERSICOLOR
```

### Algoritmi per apprendere alberi di decisione

Le slide citano diversi algoritmi: **Algoritmo di Hunt** (lo schema ricorsivo di base, su cui si fondano i successivi), **ID3**, **C4.5**, **CART**.

### L'algoritmo di Hunt

L'albero viene costruito **ricorsivamente**, suddividendo il learning set in sottoinsiemi via via più "puri" (cioè sempre più concentrati su una singola classe).

Notazione:

- `Dt` = sottoinsieme del learning set associato al nodo `t`
- `y = {y1, y2, ..., yc}` = insieme delle etichette di classe possibili

**Procedura ricorsiva** (per ogni nodo `t` da elaborare):

1. **Caso base**: se tutte le istanze in `Dt` appartengono alla stessa classe `yt`, allora il nodo `t` diventa una **foglia** etichettata con la classe `yt`.
2. **Passo ricorsivo**: altrimenti, si sceglie un attributo tra quelli descrittivi e si produce un **nodo figlio per ogni possibile valore** dell'attributo. A ciascun nodo figlio si associano le istanze del padre per le quali l'attributo assume il valore corrispondente. Si richiama la procedura ricorsivamente su ciascun figlio.

**Note importanti sull'algoritmo:**

- *Nota 1*: se una combinazione di valori non è rappresentata da nessuna istanza del training set, a quel ramo/nodo si associa una **classe di default** (se prevista).
- *Nota 2*: se tutte le istanze associate a un nodo hanno **tuple identiche** (stessi valori di attributi) ma classi diverse (situazione di **non-determinismo** nei dati), il nodo non può essere ulteriormente scisso: diventa una foglia, etichettata con la classe più rappresentata (maggioranza).
- *Nota 3*: resta da definire **quando fermarsi** nella costruzione dell'albero (criteri di arresto).
- *Nota 4*: resta da definire **come si sceglie l'attributo di split** ad ogni passo (misure di impurità, vedi sotto).

### Strategia greedy e problemi aperti

La costruzione dell'albero segue una **strategia greedy**: ad ogni passo si seleziona l'attributo di split che massimizza (localmente) una misura di riferimento, senza backtracking. I problemi da risolvere sono:

1. Come specificare la condizione di test sui diversi tipi di attributo (binari, nominali, ordinali, continui)?
2. Come determinare quale sia lo split migliore?
3. Quando fermarsi nella costruzione dell'albero?

### Tipi di split in base al tipo di attributo

- **Attributi binari** (es. "viviparo: sì/no"): lo split produce esattamente 2 figli, uno per ciascun valore.
- **Attributi nominali** (valori su un insieme finito di etichette {L1,...,Ln}, senza ordine):
  - *split multivalore*: un figlio per ciascun valore possibile dell'attributo (es. "residenza": Asti, Torino, Ivrea, ...).
  - *split binario*: un figlio corrisponde a un valore (o a un sottoinsieme di valori), l'altro raccoglie il resto. Se l'attributo ha `k` valori possibili, esistono `2^(k-1) - 1` possibili raggruppamenti binari alternativi.
- **Attributi ordinali** (es. small < medium < large < extralarge): si possono fare split binari o multivalore, ma il raggruppamento dei valori **deve rispettare l'ordinamento** (es. {small, medium} vs {large, extralarge} è corretto; {small, large} vs {medium, extralarge} è scorretto perché "spezza" l'ordine).
- **Attributi continui**:
  - *split binario*: si individua un valore soglia `v` e si testa `A ≤ v` vs `A > v` (es. "Altezza ≤ 1.7").
  - *split multivalore*: si individuano più soglie `vi` e si producono test del tipo `vi ≤ A < vi+1`. Questo richiede di **discretizzare** la variabile continua individuando un numero finito di intervalli significativi.

### Quale attributo scegliere per lo split? Misure di impurità

Non tutti gli ordini di split sono equivalenti: la scelta dell'attributo (e dell'ordine degli split) incide sulla dimensione e la qualità dell'albero risultante.

***Criterio generale (Rasoio di Occam):*** a parità di prestazioni (stessa accuratezza/error rate), si preferiscono alberi più compatti, cioè che richiedono un numero minore di test. A parità di assunzioni, la spiegazione più semplice è da preferire.

**Idea intuitiva**: sono preferiti gli split che producono nodi figli con **minore confusione**, cioè con **grado di purezza maggiore** (più le istanze di un nodo appartengono alla stessa classe, meno "confuso" è il nodo, più è facile prevedere correttamente la classe di un elemento estratto a caso da quel nodo).

Per formalizzare questa idea si definisce, per un nodo `t`, `p(i|t)` = probabilità che un elemento estratto casualmente dall'insieme associato al nodo `t` sia di classe `i`. Su questa distribuzione di probabilità si costruiscono le **misure di impurità**:

#### Entropia

$$\text{Entropia}(t) = -\sum_{i=0}^{c-1} p(i|t) \cdot \log_2 p(i|t)$$

(con la convenzione `0·log2(0) = 0`).

Proprietà (caso a 2 classi):

- Distribuzioni (0,1) o (1,0): **purezza massima**, nessuna confusione → Entropia = `-0·log2(0) - 1·log2(1) = 0` (valore minimo).
- Distribuzione (0.5, 0.5): **massima confusione** → Entropia = `-0.5·log2(0.5) - 0.5·log2(0.5) = 1` (valore massimo per 2 classi).

L'entropia è quindi 0 quando il nodo è puro, ed è massima quando le classi sono equidistribuite.

#### Gini index

Citato tra le misure alternative di impurità insieme a entropia ed errore di classificazione (le slide non ne riportano la formula esplicita, ma è la misura tipicamente usata dall'algoritmo **CART**; nella pratica standard: `Gini(t) = 1 - Σ p(i|t)²`).

#### Errore di classificazione (misclassification error)

Citato come terza misura alternativa di impurità disponibile per la selezione dello split.

### Calcolo del guadagno (gain) di uno split

Per confrontare split alternativi si calcola quanto uno split riduce l'impurità rispetto al nodo genitore:

$$\text{guadagno} = I(\text{parent}) - \sum_{j=1}^{k} \frac{N(v_j)}{N} \cdot I(v_j)$$

dove:

- `I(parent)` = impurità del nodo genitore
- `k` = numero di nodi figli prodotti dallo split
- `N` = numero di record nel nodo genitore
- `N(v_j)` = numero di record del nodo figlio j-mo (quelli che nell'attributo scelto per lo split hanno tutti lo stesso valore `v_j`)
- `I(v_j)` = impurità del nodo figlio j-mo

In pratica: dall'impurità del nodo padre si sottrae la **media pesata** (pesata sulla numerosità) delle impurità dei nodi figli. Si sceglie lo split che **massimizza il guadagno** (equivalentemente, che minimizza l'impurità residua media).

#### Information gain

Quando la misura di impurità usata è l'entropia, il guadagno prende il nome di **information gain**:

$$\text{gain} = \text{entropia(parent)} - \sum_{j=1}^{k} \frac{N(v_j)}{N} \cdot \text{entropia}(v_j)$$

**Attenzione — limite dell'information gain (e di Gini)**: queste misure tendono a ***favorire attributi con molti valori diversi*** rispetto ad attributi con pochi valori. Caso estremo: un identificatore univoco (es. numero di matricola) annulla completamente l'entropia dei figli (ogni figlio conterrebbe una sola istanza, quindi puro), dando un information gain massimo — ma **non è affatto un attributo significativo** per generalizzare, anzi porta a overfitting totale. Una possibile soluzione è restringersi a **split binari**.

> ❓ **Domanda d'esame:** perché un identificatore univoco (es. matricola) non va mai scelto come attributo di split, nonostante massimizzi l'information gain?
> **Risposta:** perché produce tanti nodi figli quante sono le istanze, ciascuno con una sola istanza e quindi entropia zero (purezza massima) — l'information gain risulta massimo. Ma un simile split non generalizza affatto: il "modello" ottenuto equivale a un dizionario che memorizza ogni singola istanza (overfitting estremo), incapace di classificare correttamente istanze nuove mai viste, che quasi certamente avranno un valore di matricola non presente nel training set. Questo mostra il limite intrinseco di entropia/Gini, che favoriscono attributi con molti valori distinti indipendentemente dalla loro reale capacità discriminante/generalizzante.

### Criteri di arresto (cenni)

Le slide pongono esplicitamente la domanda "quando si termina la costruzione dell'albero?" (Nota 3 dell'algoritmo di Hunt) come uno dei problemi aperti della strategia greedy, insieme alla scelta dello split migliore. Il caso base naturale è quando un nodo è già puro (tutte le istanze della stessa classe) o quando non è più possibile scindere il nodo (istanze identiche ma classi diverse, gestito come da Nota 2).

---

## Reti neurali

### Ispirazione biologica

Le reti neurali (Neural Networks, NN) si ispirano al modo in cui i **neuroni biologici** agiscono e interagiscono fra loro. È importante però ricordare che **i neuroni artificiali non sono modelli fedeli** dei neuroni biologici: ne catturano solo alcuni principi essenziali (connessioni pesate, soglia di attivazione, propagazione del segnale).

Tra i primi modelli proposti: il **Perceptron** di Rosenblatt e la *B-machine* di Turing.

### Il neurone artificiale (Perceptron)

Un **perceptron** è un elemento computazionale dotato di una piccola memoria (i pesi), in grado di calcolare una funzione di attivazione codificata al suo interno, applicata a una combinazione pesata dei valori in ingresso:

$$\text{net} = \sum_{i=1}^{n} w_i \cdot X_i$$

$$Y = f(\text{net})$$

- `X1, ..., Xn`: valori in ingresso (attributi descrittivi dell'istanza)
- `w1, ..., wn`: pesi delle connessioni
- `net`: combinazione lineare pesata degli input
- `f`: funzione di attivazione

**Funzioni di attivazione:**

- **Funzione gradino (step)**: la funzione originariamente usata da Rosenblatt; produce valori discreti per `Y` (0 oppure 1). Non è derivabile, il che la rende poco adatta a tecniche di apprendimento basate sul gradiente.
- **Funzione sigmoide**:
  $$Y = f(\text{net}) = \frac{1}{1 + e^{-\alpha(\text{net} - \theta)}}$$
  dove `θ` è la soglia (bias, un parametro preimpostato) e `α` controlla la pendenza della curva. Il vantaggio della sigmoide rispetto al gradino è di essere **derivabile** (fondamentale per l'apprendimento via discesa del gradiente/backpropagation). Al crescere di `α`, la sigmoide tende alla forma della funzione gradino (approssimazione sempre più "brusca").

### Passata forward e interpretazione geometrica

Il perceptron elabora dati visti come punti in uno **spazio N-dimensionale** (spazio degli input), dove `N` è il numero di attributi descrittivi (feature) dell'istanza. Data un'istanza, questa viene propagata attraverso il neurone che calcola `Y` tramite la funzione di attivazione: il processo può essere visto come una forma di classificazione binaria (l'istanza ricade nella categoria 1 o nella categoria 0, a seconda dell'output del perceptron).

**Cosa codifica un perceptron?** Un **test lineare**, cioè un **iperpiano** nello spazio degli input:

$$w_1 x_1 + w_2 x_2 + \dots = 0$$

- Ciò che cade **sopra** l'iperpiano (definito dai pesi) fa attivare il neurone (output 1): riconosciuto come appartenente alla classe obiettivo.
- Ciò che cade **sotto** non fa attivare il neurone (output 0): istanze negative.

I pesi sulle connessioni in ingresso definiscono quindi **posizione e pendenza** dell'iperpiano nello spazio degli input. I pesi **caratterizzano il neurone** e ne costituiscono la conoscenza: sono **persistenti** (a differenza dei pesi "usa e getta" della votazione pesata nel rote learning).

Per un perceptron con 2 input, l'iperpiano è la retta `x1 = -(w2/w1)·x2`; il neurone si attiva per i punti tali che `w1·x1 + w2·x2 > 0`.

### Caratteristiche del perceptron

- Adatto a compiti di tipo numerico
- Risolve solo problemi ***linearmente separabili***
- La conoscenza è data dai pesi, che sono persistenti
- Apprendimento **da esempi, supervisionato**
- "Imparare" = individuare la posizione corretta dell'iperpiano nello spazio degli input

### Apprendimento del perceptron

Essendo un problema di tipo numerico, si può usare l'**errore** (differenza fra valore desiderato `d` e valore ottenuto `o`) come segnale per guidare l'apprendimento. Regola di aggiornamento del peso sulla connessione dall'input j-mo:

$$w_j^{(k+1)} = w_j^{(k)} + \eta \cdot (d - o) \cdot x_j$$

Il peso viene aggiornato sommando l'errore, moltiplicato per un **fattore di scalamento `η`** (learning rate) e per il valore della componente j-ma dell'input.

**Teorema di Novikoff**: se il problema è **linearmente separabile**, questo algoritmo di apprendimento **converge** alla soluzione; se il problema non è linearmente separabile, l'algoritmo **non converge**.

**Passata backward**: dopo la passata forward il perceptron produce un output `o`; essendo l'apprendimento supervisionato, si conosce l'output desiderato `d`. L'errore `(d - o)` è l'informazione usata per modificare i pesi, rendendo il comportamento futuro del perceptron più vicino a quello desiderato.

**Epoca di apprendimento**: l'elaborazione (forward + backward, aggiornamento pesi) di **tutte** le istanze del learning set costituisce un'epoca. L'addestramento richiede tipicamente molte epoche.

**Intuizione geometrica della convergenza**: ogni esempio "tira" l'iperpiano affinché il proprio caso venga classificato correttamente; l'iperpiano si sposta nello spazio delle istanze; il fattore di scalamento `η` evita che l'apprendimento "insegua" solo l'ultimo esempio visto, forzando una generalizzazione più stabile.

### Limiti del singolo perceptron: lo XOR

Il limite principale del perceptron fu dimostrato con un esempio semplicissimo: lo **XOR** (or esclusivo).

| A1 | A2 | XOR |
|---|---|---|
| 0 | 0 | 0 |
| 1 | 0 | 1 |
| 0 | 1 | 1 |
| 1 | 1 | 0 |

Interpretando le coppie (A1, A2) come coordinate di punti nel piano e l'output XOR come l'appartenenza sopra/sotto un ipotetico iperpiano separatore: i punti positivi (output 1) e negativi (output 0) **non sono linearmente separabili** da nessuna retta — non esiste un'unica retta che separi correttamente le due classi. Un singolo perceptron non può quindi apprendere lo XOR.

**Intuizione della soluzione**: un solo iperpiano non basta, ma se se ne avessero **due** disponibili, con la capacità di combinare le loro risposte, il problema si risolverebbe. Con più iperpiani a disposizione si possono addirittura circoscrivere regioni chiuse arbitrariamente complesse. Questa intuizione porta naturalmente all'introduzione delle reti **multi-strato**.

### Reti neurali: definizione generale e topologia

Una **rete neurale** è un **approssimatore universale di funzioni**, di natura distribuita, costituita da un insieme di neuroni collegati fra loro secondo una **topologia** (che dipende dal modello di rete). I neuroni possono implementare funzioni diverse e possono essere realizzati in software o hardware.

Esempi di topologia:

- **A strati (layered)**: i neuroni sono organizzati in livelli successivi (input, hidden, output).
- **A vicinato**: connessioni basate su prossimità/adiacenza fra neuroni, senza una stratificazione rigida.

### Multi-Layer Perceptron (MLP)

Il **MLP** è un modello di rete neurale con topologia **a strati**, di tipo **feed-forward** (il flusso di calcolo procede in una sola direzione, dall'input verso l'output, senza cicli):

- **Livello di input**: di solito i neuroni implementano la **funzione identità** (si limitano a "passare" il valore dell'attributo corrispondente).
- **Livello/i hidden**: i neuroni sono perceptron veri e propri, che usano tipicamente la **sigmoide** (o altre funzioni derivabili, es. varianti dello scalino). Si possono avere **più livelli hidden**.
- **Livello di output**: combina i risultati prodotti dai neuroni hidden.

Tipicamente la rete è **fully connected** (ogni neurone di un livello è connesso a tutti i neuroni del livello successivo).

### Codifica delle classi nell'output di un MLP

Il modo di codificare le classi nel livello di output dipende dal numero di classi del problema:

- **Riconoscimento di 1 classe** (es. "è un'istanza della classe X oppure no"): basta **1 solo neurone di output**. Se si attiva, l'istanza è riconosciuta come appartenente alla classe X.
- **Distinzione fra 2 classi** (X vs Y, classificazione binaria): basta ancora **1 neurone di output**, la cui attivazione viene associata convenzionalmente a una delle due classi (es. attivo = classe X, non attivo = classe Y).
- **Distinzione fra 3 o più classi**: qui si aprono due strade:
  - *Codifica binaria compatta*: userebbero almeno `⌈log2(numero classi)⌉` neuroni (es. con 2 neuroni si rappresentano fino a 4 combinazioni/classi in binario).
  - *Codifica "one-hot" (un neurone per classe)*: è **l'alternativa più usata in pratica**. Si impiega un neurone di output per ciascuna classe; il neurone corrispondente alla classe corretta deve attivarsi, tutti gli altri devono restare a zero.
    - Esempio con 2 classi codificate one-hot: output `10` → Classe A, output `01` → Classe B.

> ❓ **Domanda d'esame:** perché per un problema a più classi si preferisce spesso un neurone di output per classe (codifica one-hot) invece della codifica binaria compatta (log2 dei neuroni)?
> **Risposta:** con la codifica compatta, il significato di ciascun neurone di output è "distribuito" e non direttamente interpretabile: un piccolo errore nell'attivazione di un solo neurone può far scivolare l'output verso il codice binario di una classe completamente diversa e sbagliata (gli output non hanno una gerarchia naturale di "vicinanza semantica"). Con la codifica one-hot, invece, ogni neurone rappresenta direttamente e in modo indipendente il grado di attivazione/confidenza verso una specifica classe: è più robusta a piccoli errori (l'errore di solito si concentra su neuroni "vicini" in termini di somiglianza fra classi), più facile da interpretare e da addestrare con la delta rule/backpropagation standard (ogni neurone di output ha un proprio target 0/1 chiaro).

### Cosa imparano i diversi hidden layer

Con più livelli hidden, si osserva empiricamente una sorta di **gerarchia di astrazione**:

- il **primo layer** traccia dei confini (separazioni lineari elementari, come un singolo perceptron);
- il **secondo layer** combina questi confini per costruire delle **forme**;
- il **terzo layer** combina le forme per creare **forme arbitrariamente complesse**.

Questo spiega intuitivamente perché aggiungere strati hidden aumenti la capacità espressiva della rete rispetto al singolo perceptron (che può solo tracciare un iperpiano).

### Potere espressivo dell'MLP

Gli **MLP a 3 livelli** i cui neuroni usano come funzione di attivazione la sigmoide sono ***approssimatori universali di funzioni***, a patto di poter utilizzare un numero di neuroni hidden sufficientemente grande (senza limiti a priori).

La conoscenza appresa dalla rete è memorizzata nella **matrice dei pesi** che definisce la forza di tutte le connessioni.

### Apprendimento dell'MLP: backpropagation

Una rete MLP impara in modo **supervisionato**, inducendo la matrice dei pesi a partire da un insieme di esempi etichettati (nel caso della classificazione). Per ogni istanza si effettuano due passate:

1. **Passata forward**: l'istanza viene sottoposta alla rete, che la elabora strato per strato e produce un output.
2. **Passata backward**: l'errore commesso viene utilizzato per modificare i pesi, procedendo "a ritroso" a partire dalle connessioni più vicine ai neuroni di output verso quelle degli strati precedenti.

Anche qui, l'elaborazione dell'intero learning set costituisce un'**epoca di apprendimento**, e il training richiede tipicamente molte epoche.

#### Discesa del gradiente

L'errore complessivo `E` della rete dipende dalla matrice dei pesi `W`. Imparare significa **cercare la configurazione di pesi `W` che minimizza `E`**. Si usa la tecnica della **discesa del gradiente** (greedy, cerca un minimo — non necessariamente globale):

$$\Delta w_{ji} = -\eta \cdot \frac{\partial E(w)}{\partial w_{ji}}$$

Ogni peso `w_ji` (sulla connessione dal neurone j-mo al neurone i-mo) viene modificato sottraendo la derivata parziale dell'errore rispetto a quel peso, scalata da un fattore di apprendimento `η`.

Il **gradiente** `∇f = (∂f/∂x1, ..., ∂f/∂xn)` indica la direzione di massima crescita di una funzione; usato con segno negativo, permette di muoversi verso un minimo. Analogamente `∇E = (∂E/∂w1, ..., ∂E/∂wn)` indica come modificare i pesi per ridurre l'errore.

#### Errore globale dell'MLP

$$E = \frac{1}{2} \sum_{i=1}^{p} (t_i - y_i)^2$$

dove `p` = numero di neuroni di output, `t_i` = valore desiderato (target) del neurone di output i-mo, `y_i` = valore effettivamente prodotto dal neurone di output i-mo.

#### Il problema della distribuzione del credito/biasimo (credit assignment)

L'errore è calcolabile direttamente solo per i neuroni del **livello di output** (per i quali si conosce il target `t`). Ma come si distribuisce il "biasimo" per l'errore fra i pesi di tutti gli strati precedenti (hidden)? Questo è il problema centrale risolto dall'algoritmo di ***backpropagation***.

**Delta rule generalizzata per i neuroni di output:**

$$\Delta w_{ji} = \eta \cdot \delta_j \cdot x_{ji}$$

$$\delta_j = y_j \cdot (1 - y_j) \cdot (t_j - y_j)$$

dove `j` è un neurone di output, `i` un neurone del livello precedente connesso a `j`, `x_ji` il valore inviato da `i` a `j`, `y_j` l'output prodotto da `j`, `t_j` il target desiderato per `j`. Il termine `y_j(1-y_j)` deriva dalla derivata della funzione sigmoide.

**Delta rule per i neuroni hidden** — l'idea è distribuire l'errore all'indietro fra le connessioni, proporzionalmente alla forza dei pesi correnti:

$$\Delta w_{ki} = \eta \cdot \delta_k \cdot x_{ki}$$

$$\delta_k = y_k \cdot (1 - y_k) \cdot \sum_{j \in I_k} \delta_j \cdot w_{kj}$$

dove `k` è un neurone hidden e `I_k` è l'insieme dei neuroni del livello successivo a cui `k` è connesso. In pratica il `δ` di un neurone hidden è calcolato "propagando all'indietro" (da cui il nome *backpropagation*) i `δ` dei neuroni a cui è connesso nel livello successivo, pesati per la forza delle rispettive connessioni.

### Oltre la classificazione: la regressione

Una rete neurale (non necessariamente MLP) può risolvere sia problemi di **classificazione** sia problemi di **regressione**. La regressione, in statistica, è il problema di definire la relazione fra un insieme di variabili indipendenti e una variabile dipendente; più in generale, è il problema di costruire un'approssimazione di una **funzione continua** `y = f(x)` la cui forma analitica non è nota e va indotta da esempi.

Il learning set ha la stessa struttura vista per la classificazione (variabili indipendenti X1...Xn e variabile dipendente target), ma il target è un valore continuo anziché una classe discreta. Una rete neurale può anche imparare **funzioni a più valori** (più variabili dipendenti): basta prevedere un neurone di output per ciascun valore prodotto dalla funzione.

**Calcolo dell'errore in regressione**: non essendoci classi, non si può più usare la matrice di confusione né misure come precision/recall o accuratezza/error rate. Si usa invece l'**Errore Quadratico Medio (Mean Squared Error, MSE)**:

$$MSE(y) = \frac{\sum_{i=1}^{n} (y_o - y_d)^2}{n}$$

Somma dei quadrati degli errori (differenza fra output ottenuto `y_o` e output desiderato `y_d`) su tutte le istanze di test, divisa per il numero di istanze. Si usa il quadrato per evitare che errori di segno opposto si annullino a vicenda nella somma.

---

## Riepilogo e punti chiave

- **Classificazione**: le classi non sono naturali ma definite dal progettista; si apprende un modello dal *training set* (induzione) e lo si valuta sul *test set* (deduzione), tramite matrice di confusione, accuratezza (`(f11+f22)/tot`), error rate, ed eventualmente matrice dei costi quando gli errori hanno peso diverso. Attenzione a dataset sbilanciati: un'accuratezza alta non implica un buon modello.
- **Alberi di decisione**: nodi interni = test su attributi, foglie = decisioni/classi. Si costruiscono ricorsivamente con l'**algoritmo di Hunt**: se il nodo è puro diventa foglia, altrimenti si sceglie un attributo di split e si ricorre sui figli. La scelta dell'attributo migliore è **greedy** e si basa su misure di impurità — **entropia** (`-Σ p_i log2 p_i`), **Gini**, **errore di classificazione** — combinate nella formula del **guadagno** (impurità del padre meno media pesata delle impurità dei figli); con l'entropia si parla di **information gain**. Attenzione al bias verso attributi con molti valori (es. identificatori univoci) — un limite noto di entropia e Gini. Split diversi a seconda del tipo di attributo (binario, nominale, ordinale, continuo). Principio guida: Rasoio di Occam, preferire alberi compatti.
- **Reti neurali / perceptron**: ispirate (in modo non fedele) al neurone biologico. Il perceptron calcola `net = Σ wi·Xi` e applica una funzione di attivazione (gradino, poi sostituita dalla **sigmoide**, derivabile) per produrre `Y = f(net)`. Geometricamente codifica un **iperpiano** (test lineare) nello spazio degli input: risolve solo problemi **linearmente separabili** (limite dimostrato con lo **XOR**). Apprende per correzione dell'errore `(d-o)` con un fattore di scalamento `η`; converge solo se il problema è linearmente separabile (Novikoff).
- **MLP**: rete feed-forward a strati (input, uno o più hidden, output), tipicamente fully-connected, con hidden layer che usano la sigmoide. Con almeno 3 livelli e neuroni sigmoide a sufficienza è un **approssimatore universale di funzioni**. La codifica delle classi in output usa 1 neurone per problemi a 1-2 classi, e tipicamente **un neurone per classe (one-hot)** per problemi multiclasse. L'apprendimento avviene per **backpropagation**: passata forward per calcolare l'output, passata backward per propagare l'errore e aggiornare i pesi via **discesa del gradiente**, minimizzando l'errore globale `E = (1/2) Σ(ti - yi)²`; la *delta rule* per l'output usa `δj = yj(1-yj)(tj-yj)`, quella per gli hidden propaga i `δ` dei neuroni successivi pesati sulle connessioni. Le reti neurali risolvono anche problemi di **regressione** (funzione continua), valutati con l'**MSE** anziché con le metriche di classificazione.
