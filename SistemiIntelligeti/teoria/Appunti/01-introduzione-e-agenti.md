# Modulo 1 — Introduzione all'IA e Agenti Intelligenti

> Corso di Sistemi Intelligenti, Cristina Baroglio, Università di Torino. Riferimento: Russell & Norvig, *Intelligenza Artificiale: un approccio moderno* (in particolare il cap. 2 per la parte sugli agenti).

## 1. Cos'è l'intelligenza artificiale?

### 1.1 Un punto di partenza informale: cosa sanno fare i sistemi di IA generativa oggi

Le slide aprono mostrando esempi reali (DeepSeek, ChatGPT, febbraio 2025) a cui viene posta la stessa domanda ("Chi era Napoleone VII di Baviera?", personaggio storico **inesistente**). I due sistemi rispondono con sicurezza ma con contenuti diversi e **inventati** (allucinazioni): DeepSeek lo descrive come figlio di Napoleone III morto nel 1879, ChatGPT come figlio di Massimiliano I di Baviera morto nel 1837. Nessuna delle due risposte è vera, ma entrambe sono fluenti e plausibili.

Nel secondo esempio, allo stesso sistema viene chiesto di scrivere un articolo che metta "in buona luce" e poi "in cattiva luce" le lumache: il sistema produce entrambi i testi senza alcuna difficoltà, adattando tono e argomentazione alla richiesta.

**Perché questi esempi aprono il corso?** Servono a mostrare, prima ancora di dare definizioni, il problema centrale che il modulo affronterà: questi sistemi producono output linguisticamente ineccepibili e convincenti, ma ciò **non implica che "comprendano"** quello che dicono, né che possiedano conoscenza verificata. È un'anticipazione informale del dibattito Turing/Searle che viene formalizzato più avanti.

### 1.2 IA nell'immaginario collettivo vs. IA reale

- **Immaginario comune**: robot antropomorfo, capace di risolvere problemi complessi, capace di imparare (fantascienza).
- **IA realmente diffusa intorno a noi** (spesso in modo "invisibile", cioè in **contatto quotidiano ma inconsapevole**):
  - servizi di streaming (raccomandazioni),
  - fotocamere/smartphone (riconoscimento volti, cibo, scene),
  - social network (annunci e suggerimenti personalizzati),
  - assistenti virtuali (chat, voce, mappe),
  - supporto alla decisione (es. concessione di mutui),
  - logistica e consegne a domicilio (calcolo percorsi).

Il punto pedagogico: l'IA che usiamo ogni giorno è quasi sempre **specializzata e invisibile**, non un robot antropomorfo generalista.

### 1.3 Definizione di "intelligenza" e problema della IA

Il vocabolario definisce l'intelligenza (umana) come il complesso di facoltà psichiche che permettono di pensare, comprendere, spiegare fatti/azioni, elaborare modelli astratti della realtà, farsi intendere dagli altri, giudicare, adattarsi a situazioni nuove e modificarle. È una facoltà propria dell'uomo (con gradazioni riconosciute anche agli animali), che si sviluppa nell'infanzia insieme alla consapevolezza.

**Intelligenza artificiale** = una forma di intelligenza **non naturale**, ottenuta con procedimenti tecnici (cioè costruita dall'uomo tramite l'informatica, non frutto di sviluppo biologico).

### 1.4 Breve storia: le origini

| Anno | Evento |
|---|---|
| 1936 | Alan Turing formalizza la **Macchina di Turing**, pietra miliare dell'informatica teorica |
| 1940 | ENIAC, tra i primi calcolatori |
| 1950 | Turing propone il **Test di Turing**: quando un computer può dirsi intelligente? |
| 1951 | UNIVAC |
| 1956 | **Nasce ufficialmente l'IA** come disciplina: Dartmouth Summer Research Project |

**Anni '40 — automazione del calcolo**: il computer esegue una sequenza di istruzioni predefinita, senza operatore umano che intervenga passo-passo. Questo pone subito la domanda: *l'automazione (eseguire automaticamente un programma) equivale a intelligenza?*

Le slide insistono molto su questa domanda mostrando esempi progressivi (una calcolatrice esegue un programma ed è automatica — ma non diremmo che è intelligente) per portare lo studente a capire che **automazione ≠ intelligenza**: eseguire automaticamente istruzioni non basta. Serve qualcos'altro — capacità di adattarsi, di scegliere di fronte a situazioni non previste esplicitamente dal programmatore.

> ❓ **Domanda d'esame: Automazione è intelligenza?**
> No. Un programma che esegue automaticamente una sequenza di istruzioni predefinite (es. una calcolatrice) è automatico ma non è considerato intelligente: non si adatta, non affronta situazioni nuove, non delibera. L'intelligenza (artificiale) richiede in più la capacità di **adattarsi**, di scegliere l'azione più opportuna in funzione di percezioni e obiettivi, eventualmente anche di **imparare** dall'esperienza. Questo è il punto di svolta che porta dal concetto di "programma automatico" a quello di "agente".

### 1.5 Il Dartmouth Summer Research Project (1956)

- Il termine "Artificial Intelligence" nasce nel 1956, proposto da **John McCarthy**.
- Un gruppo di circa venti ricercatori di discipline diverse (Solomonoff, Minsky, McCarthy, Shannon, Rochester, Selfridge, Newell, Simon, ecc.) si riunisce per circa due mesi per fare brainstorming sulle "thinking machines". Notare: né Turing (morto nel 1954) né von Neumann (gravemente malato) parteciparono.
- **"Carta di identità" dell'IA**:
  - Nascita: Dartmouth Conference, USA, 1956; nome scelto da McCarthy.
  - Prima del 1956 (primi anni '50): si discuteva già se una macchina potesse "pensare" (cibernetica, teoria degli automi, elaborazione dell'informazione complessa; Test di Turing).
  - Dopo il 1956 (primi anni '60): primi tentativi applicativi (scacchi, giochi, dimostrazione automatica di teoremi).
- Contesto tecnologico dell'epoca: niente tastiere, dischi magnetici o monitor come li intendiamo oggi; solo al MIT si sperimentava l'input diretto da tastiera (anziché schede perforate), mentre IBM sviluppava i precursori dei dischi magnetici.

### 1.6 Il Test di Turing

Proposto da Alan Turing nel 1950 nell'articolo "Computing Machinery and Intelligence" come **The Imitation Game**: sostituisce la domanda mal posta "può una macchina pensare?" con una domanda operativa.

**Come funziona**: un intervistatore umano comunica per iscritto con due interlocutori nascosti (uno umano, uno macchina) senza sapere quale sia quale. Può fare qualsiasi domanda. Se, al termine, l'intervistatore non riesce a distinguere in modo affidabile la macchina dall'umano (o giudica erroneamente che la macchina sia umana), la macchina **supera il test**.

Esempio dalle slide:
```
Q: Please write me a sonnet on the subject of the Forth Bridge.
A: Count me out on this one. I never could write poetry.
Q: Add 34957 to 70764.
A: (pausa di 30 secondi) 105621.
Q: Do you play chess?
A: Yes.
```
Da notare: la macchina finge persino di essere lenta a fare un calcolo (per sembrare più umana) — il test valuta la capacità di **imitare risposte plausibili**, di comportarsi *come se* fosse un essere umano, non un meccanismo interno particolare.

> ❓ **Domanda d'esame: Il test di Turing cattura davvero l'intelligenza?**
> Questo è uno dei nodi filosofici centrali del modulo. Il test si basa solo sull'osservazione dei comportamenti esterni (input/output): se gli output sono indistinguibili da quelli umani, la macchina "passa". Ma **produrre gli output attesi è sufficiente per dire che c'è comprensione?** Le slide rispondono con l'esempio del quiz sulla geografia: due persone (Valeria e Rossella) danno entrambe la risposta corretta "Piemonte" alla domanda "dove si trova Torino?", ma Valeria la sa perché ha studiato geografia e ha usato conoscenza + ragionamento per collegare la domanda alla risposta, mentre Rossella ha semplicemente tirato a caso ed è stata fortunata. Dall'esterno (stesso input, stesso output) i due comportamenti sono indistinguibili, ma solo uno dei due implica reale comprensione. Questo mostra che **stesso output non implica stessa comprensione**: il Test di Turing, valutando solo il comportamento osservabile, non può distinguere questi due casi, e quindi è un test necessario ma probabilmente non sufficiente per l'intelligenza "vera" (nel senso forte).

### 1.7 La Stanza Cinese di John Searle (1980)

Argomento filosofico contro l'idea che superare il Test di Turing implichi comprensione reale (Searle, *Minds, brains, and programs*, 1980).

**Esperimento mentale**: una persona che non conosce il cinese è chiusa in una stanza. Riceve dall'esterno frasi scritte in ideogrammi cinesi (input). All'interno della stanza ha un manuale di istruzioni (equivalente a un programma) che le dice, per ogni sequenza di simboli in ingresso, quali simboli produrre in uscita, puramente in base alla loro forma sintattica, senza capirne il significato. Seguendo meccanicamente le istruzioni, la persona restituisce risposte in cinese perfettamente sensate, tanto che chi sta fuori dalla stanza (un madrelingua cinese) crede di conversare con qualcuno che capisce il cinese.

**Domanda**: quella persona (o il sistema stanza+persona+manuale) **parla davvero cinese**? **Lo capisce**?

Secondo Searle, no: la persona sta solo manipolando simboli sintatticamente, senza avere accesso alla semantica, all'intenzionalità, alla comprensione. Questo è esattamente ciò che fa un computer che esegue un programma: manipola simboli seguendo regole sintattiche, senza "capire" nulla nel senso in cui lo capisce un umano. Da qui la tesi di Searle: *"Instantiating a computer program is never by itself a sufficient condition of intentionality"* — eseguire un programma non è mai di per sé condizione sufficiente per avere intenzionalità (cioè stati mentali "rivolti verso" un significato).

Questo argomento si collega direttamente all'apertura del modulo (DeepSeek/ChatGPT): questi sistemi possono essere impressionanti nelle risposte, ma la domanda "capiscono quello che dicono, oppure no?" resta aperta e filosoficamente delicata.

### 1.8 Test di Turing inverso: CAPTCHA

**CAPTCHA** = "Completely Automated Public Turing-test to tell Computers and Humans Apart". A differenza del test di Turing classico (dove un umano cerca di riconoscere la macchina), qui è **un computer** che pone un test per distinguere se dall'altra parte c'è un umano o un bot, tipicamente per impedire l'accesso automatizzato a form o dati. Sviluppato nel 1997 nel contesto del motore di ricerca AltaVista.

### 1.9 Strong AI vs. Weak AI

Due modi diversi di intendere l'obiettivo della disciplina:

| | Strong AI (IA forte) | Weak AI (IA debole) |
|---|---|---|
| Obiettivo | Riprodurre realmente l'intelligenza umana | Trovare metodi per risolvere problemi che, se risolti da un umano, richiederebbero intelligenza |
| Approccio | Studio del pensiero e comportamento umano (scienze cognitive) | Task-oriented: studio del pensiero e comportamento *razionale* (non necessariamente umano) |
| Criterio di successo | La macchina deve effettivamente pensare/capire come un umano | Basta che il sistema *funzioni* producendo la soluzione corretta, indipendentemente dal meccanismo interno |

Questa distinzione anticipa le "quattro scuole" di definizione dell'IA (§1.11) e chiarisce perché il corso, seguendo Russell & Norvig, adotterà come riferimento pratico l'approccio del **comportamento razionale** (weak AI, task-oriented), più operativo e ingegnerizzabile.

### 1.10 Dall'esempio "attraversare la strada" nasce l'astrazione di agente

Le slide usano un esempio guida ricorrente: *quanto è difficile attraversare una strada?*

Un **uomo** che attraversa la strada deve: identificare il passaggio pedonale, rilevare possibili ostacoli, rilevare oggetti in movimento, rilevare segnali significativi (es. semaforo), costruire un piano d'azione. L'ambiente in cui opera è **complesso**, **parzialmente prevedibile**, **parzialmente collaborativo** (altri conducenti/pedoni possono cooperare o no).

La domanda diventa: **come si programma un agente artificiale** capace di fare le stesse cose, nello stesso tipo di ambiente? Da qui emergono le prime astrazioni fondamentali del corso: il binomio **⟨agente, ambiente⟩**.

**Definizione di agente**: un agente è un'**astrazione che rappresenta un qualsiasi sistema che percepisce il proprio ambiente tramite dei sensori e agisce su di esso tramite degli attuatori**.

Punti chiave impliciti in questa definizione:
- Non esistono agenti che non siano **situati in un ambiente**: agente e ambiente sono un **binomio inscindibile**, non ha senso parlare di un agente "nel vuoto".
- Tra la percezione (input dai sensori) e l'azione (output verso gli attuatori) c'è una **funzione deliberativa** (rappresentata spesso nei diagrammi con un punto interrogativo "?" dentro l'agente) che decide quale azione eseguire sulla base di ciò che è stato percepito. È proprio il "contenuto" di questo punto interrogativo — come viene implementata la deliberazione — a differenziare i vari tipi di agente che vedremo più avanti (agenti reattivi, basati su modello, su obiettivi, sull'utilità, che apprendono).

Questo schema **agente ↔ ambiente** (percezione tramite sensori → deliberazione → azione tramite attuatori, in un ciclo continuo) è lo schema concettuale centrale attorno a cui ruota tutto il resto del modulo.

### 1.11 Le quattro scuole di definizione dell'IA

Russell & Norvig classificano le definizioni storiche di IA lungo due assi: *pensiero vs. comportamento* e *fedeltà umana vs. razionalità*.

| | Riproduce il **pensiero** | Riproduce il **comportamento** |
|---|---|---|
| **come l'uomo** | Sistemi che **pensano come esseri umani**<br>Haugeland 1985: "far sì che i computer arrivino a pensare... macchine dotate di mente"<br>Bellman 1978: automazione di decisione, risoluzione problemi, apprendimento | Sistemi che **agiscono come esseri umani**<br>Kurzweil 1990: "creare macchine che eseguono attività che richiedono intelligenza se svolte da persone"<br>Rich & Knight 1991: far eseguire ai computer ciò in cui, al momento, gli umani sono più bravi |
| **in modo razionale** | Sistemi che **pensano razionalmente**<br>Charniak & McDermott 1985: studio delle facoltà mentali tramite modelli computazionali<br>Winston 1992: studio dei processi computazionali che rendono possibile percepire, ragionare, agire | Sistemi che **agiscono razionalmente**<br>Poole et al. 1998: progettazione di agenti intelligenti<br>Nilsson 1998: comportamento intelligente negli artefatti |

Confronto sintetico con l'esempio dell'attraversamento pedonale:

| | Pensiero | Comportamento |
|---|---|---|
| **Umano** (approccio forte) | Ragionamento logico esplicito sul fatto che c'è un passaggio pedonale, sgombro, senza auto in arrivo (Modellazione Cognitiva, es. *General Problem Solver* di Newell & Simon) | Guardo a sinistra e a destra prima di attraversare (valutato col Test di Turing: il comportamento è "umano" se un esaminatore non lo distingue da quello di un umano) |
| **Razionale** (approccio debole) | Una rete neurale che decide se ci sono le condizioni per attraversare (codifica formale del ragionamento, es. inferenza logica) | Un robot con sonar schiva passanti e auto in modo diverso da un umano, ma **funzionalmente efficace** (codifica di comportamenti che "fanno la cosa giusta" senza necessariamente imitare meccanismi umani) |

Il corso adotta prevalentemente l'ottica **"agire razionalmente"** (in linea con Poole/Nilsson e con Russell & Norvig), perché è la più operativa per progettare e valutare agenti artificiali: non serve che l'agente "pensi come un umano", basta che scelga sempre l'azione che massimizza il risultato atteso.

### 1.12 Quando serve davvero l'IA?

- **Non è adatta** dove esistono già modelli matematici precisi o metodi algoritmici specifici (in quei casi conviene usare un algoritmo tradizionale).
- **È utile o necessaria** quando si hanno: problemi non deterministici, molteplicità di soluzioni possibili, preferenze tra soluzioni diverse, dati di natura simbolica, conoscenza ampia e incompleta, informazione parzialmente strutturata, necessità di interazione con l'ambiente e con esseri umani.

### 1.13 Discipline di fondamento dell'IA

L'IA è un campo intrinsecamente interdisciplinare: **Filosofia, Matematica, Economia, Neuroscienze, Psicologia, Informatica, Teoria del controllo e cibernetica, Linguistica**.

Due esempi approfonditi dalle slide:

- **Filosofia — Aristotele** (*Etica Nicomachea*, Libro III): Aristotele osserva che non deliberiamo sui fini (un medico non delibera *se* debba guarire) ma sui **mezzi** per raggiungerli, una volta posto il fine. Se il fine è raggiungibile con più mezzi, si valuta quale sia il più facile/migliore; si procede a ritroso dai mezzi fino a una "causa prima" (ciò che è ultimo nell'analisi è primo nella costruzione). Questo è considerato il **primo esempio storico di algoritmo di deliberazione backward** (dal goal ai mezzi), concettualmente identico alla ricerca all'indietro usata nella risoluzione di problemi in IA — implementato circa 2300 anni dopo nel **General Problem Solver (GPS)** di Newell & Simon.
- **Psicologia — Ivan Pavlov**: nasce nel XIX secolo lo studio scientifico del comportamento animale/umano. Pavlov studia l'apprendimento per **riflesso condizionato**: la salivazione del cane è un riflesso naturale (incondizionato) davanti al cibo (stimolo incondizionato); associando ripetutamente un campanello (stimolo neutro) alla presentazione del cibo, il campanello da solo diventa uno **stimolo condizionato** che induce salivazione. Questo mostra come un comportamento possa essere modificato dall'esperienza — idea alla base dell'apprendimento automatico.

### 1.14 Risoluzione automatica di problemi (anticipazione)

Le slide chiudono anticipando i temi successivi del corso: definire cosa sia un problema e una soluzione (distinguendo soluzione da soluzione *ottima*), con tre categorie principali di approcci:
1. ricerca nello spazio degli stati,
2. ricerca in spazi con avversario (giochi a informazione completa),
3. risoluzione di problemi mediante soddisfacimento di vincoli (CSP).

---

## 2. Agenti e ambienti

### 2.1 Agente e ambiente: il binomio fondamentale

Ribadendo la definizione già introdotta: un **agente** è un'astrazione che rappresenta un qualsiasi sistema che **percepisce** il proprio ambiente tramite **sensori** e **agisce** su di esso tramite **attuatori**. Non esistono agenti scollegati da un ambiente: **agente e ambiente formano un binomio inscindibile**. Il simbolo "?" nel diagramma dell'agente rappresenta la **funzione deliberativa**, cioè il meccanismo interno (non ancora specificato) che, sulla base di ciò che è stato percepito, determina quale azione eseguire.

Esempi di sensori fisici reali (per dare concretezza al concetto): sensori di luce/ottici, infrarossi, suono (microfoni), accelerazione (accelerometri), temperatura, calore, radiazione (contatori Geiger), resistenza/corrente/tensione elettrica, magnetismo, pressione, gas e flusso di liquidi, movimento, orientamento, forza (celle di carico, estensimetri), prossimità, distanza, biometrici, chimici.

### 2.2 Sequenza percettiva

**Definizione**: la **sequenza percettiva** è la storia completa di tutte le percezioni che un agente ha ricevuto fino a un certo istante.

Un agente sceglie la prossima azione in base alla **situazione in cui si trova**, cioè in base a tutto ciò che ha percepito fino a quel momento (non solo alla percezione istantanea). Il modo più generale (ma anche più oneroso) di realizzare il modulo deliberativo è una **tabella percepito → azione** che associa ad ogni possibile sequenza percettiva un'azione. In alcuni casi è possibile prescindere dalla storia intera e basarsi sulla sola percezione corrente; in altri casi serve davvero l'intera sequenza (o una sintesi di essa, come uno "stato interno").

#### Esempio: il mondo dell'aspirapolvere

Un piccolo mondo giocattolo con due sole posizioni, A e B, ciascuna delle quali può essere pulita o sporca. Una possibile tabella percepito-azione:

| Sequenza percettiva | Azione |
|---|---|
| [A, pulito] | destra |
| [A, sporco] | aspira |
| [B, pulito] | sinistra |
| [B, sporco] | aspira |
| [A, pulito],[A, pulito] | destra |
| [A, pulito],[A, sporco] | aspira |
| ... sequenze di lunghezza crescente | ... |

Le slide mostrano poi una **seconda tabella diversa** per lo stesso ambiente (dove, ad esempio, [A, pulito] produce "aspira" invece di "destra"): rappresenta un **agente diverso**, con un comportamento differente pur nello stesso ambiente. Questo porta alla domanda cruciale: **due aspirapolvere che si comportano diversamente sono confrontabili? Sulla base di cosa?** Serve un criterio oggettivo per stabilire quale dei due comportamenti sia "migliore" — da qui nasce la nozione di misura di prestazione (§2.3).

### 2.3 Razionalità

#### 2.3.1 "Fare la cosa giusta"

In termini informali, un agente **razionale** è un agente che "fa la cosa giusta", cioè opera per conseguire il "successo". Per rendere questa idea precisa serve una **misura di prestazione (performance measure)**: un criterio che valuta la bontà degli **stati** attraversati dall'ambiente, definito in funzione dell'effetto che si desidera ottenere (non della singola azione in sé, ma delle sue conseguenze sullo stato del mondo).

Esempio nel mondo dell'aspirapolvere — una possibile misura di bontà degli stati:

| Stato | Bontà |
|---|---|
| [A pulito], [B pulito] | 1 |
| [A pulito], [B sporco] | 0.5 |
| [A sporco], [B pulito] | 0.5 |
| [A sporco], [B sporco] | 0 |

#### 2.3.2 Definizione formale di comportamento razionale

Il comportamento razionale di un agente dipende da **quattro fattori**:
1. le **azioni** nelle facoltà dell'agente (il repertorio di azioni disponibili),
2. la **misura di prestazione** che definisce il criterio di successo,
3. la **conoscenza dell'ambiente** posseduta dall'agente,
4. la **sequenza percettiva** fino a quel momento.

**Definizione**: un agente razionale dovrebbe scegliere sempre, per ogni possibile sequenza percettiva, l'azione che **massimizza la misura di prestazione attesa**, date la sequenza percettiva stessa e le informazioni derivabili dalla conoscenza dell'ambiente in possesso dell'agente.

Nota il termine "attesa": la razionalità si valuta rispetto a ciò che l'agente può ragionevolmente prevedere dato ciò che sa, **non** rispetto all'esito effettivo (che dipende anche da fattori che l'agente non poteva conoscere).

#### 2.3.3 Razionalità vs. onniscienza/chiaroveggenza

| | Razionalità | Onniscienza / chiaroveggenza |
|---|---|---|
| Ottimizza | il risultato **atteso** | il risultato **reale** |
| Fattori ignoti/imprevedibili | possono intercorrere e impedire di raggiungere il risultato ideale | per definizione non esistono: si conosce già tutto |

**Esempio (torta di compleanno)**: voglio che al compleanno di mio figlio ci sia la torta più bella e meno costosa. Conosco le offerte dei pasticceri della zona, i gusti di mio figlio, ho abbastanza denaro e so fare acquisti: sulla base di tutto ciò, scelgo la torta migliore che conosco. Due cose però potevano sfuggirmi: (a) la nonna, a mia insaputa, porta in regalo una torta identica (informazione che non potevo conoscere), e (b) esiste una nuova pasticceria con un'offerta migliore di cui non ero a conoscenza. In entrambi i casi il mio comportamento **resta razionale**, anche se il risultato non è quello ottimale in assoluto: la mia sequenza percettiva non includeva quelle informazioni, quindi non potevo tenerne conto. Un agente **onnisciente/chiaroveggente**, che sapesse tutto in anticipo, avrebbe invece ottenuto il risultato migliore in assoluto (es. non comprare nessuna torta sapendo che arriva quella della nonna).

Punto fondamentale: **razionale non significa "di successo" né "onnisciente"**. Significa fare la scelta migliore possibile *dato ciò che si sa*.

**Razionalità e apprendimento**: se un anno dopo, sapendo ormai che la nonna tende a fare la torta perfetta per il compleanno, io comprassi comunque la torta senza prima verificare, il mio comportamento **non sarebbe più razionale**, perché ora quella conoscenza fa parte della mia sequenza percettiva/esperienza pregressa. Questo mostra che **un agente razionale è tanto più efficace quanto più ha capacità di imparare dall'esperienza** e di modificare il proprio comportamento futuro di conseguenza.

#### 2.3.4 La percezione non è un atto passivo

**Esempio (attraversare la strada)**: è razionale che un robot attraversi la strada senza prima guardare a destra? **No.** Prima di eseguire un'azione, un agente deve valutare se ha raccolto informazioni sufficienti oppure se è necessario compiere ulteriori **atti percettivi** (es. guardare) prima di agire. Questo mostra che la **razionalità dipende dalla sequenza percettiva, ma può anche influenzarla**: un agente razionale può scegliere di percepire di più prima di decidere.

> ❓ **Domanda d'esame: quale aspirapolvere è più razionale? Sono definibili comportamenti ancora più razionali?**
> Non si può rispondere senza fissare prima una misura di prestazione esplicita (es. quella della tabella con bontà degli stati) e senza conoscere l'ambiente e le azioni disponibili. Rispetto a una misura che premia il numero di celle pulite nel tempo, un agente che aspira solo quando percepisce "sporco" ed evita mosse inutili è più razionale di uno che, ad esempio, spreca energia muovendosi anche quando la cella corrente è già pulita senza una strategia. Esistono comportamenti "ancora più razionali", ad esempio agenti che tengono conto anche del consumo energetico, del tempo impiegato, o che imparano il layout dell'ambiente per pianificare percorsi più efficienti: dipende sempre da **quali effetti desiderati** vengono inclusi nella misura di prestazione.

### 2.4 Task environment e PEAS

**Task environment**: il contesto in cui l'agente è inserito. Può essere **fisico** (reale o simulato, tipico per agenti robotici) oppure, ad esempio, **sociale**, comprendendo le relazioni con altri agenti (tipico per agenti software).

**PEAS** è l'acronimo che identifica i quattro elementi che definiscono formalmente un task environment, e va sempre specificato quando si progetta un agente:
- **P**erformance measure — la misura di prestazione rispetto a cui valutare il successo dell'agente,
- **E**nvironment — l'ambiente in cui l'agente opera,
- **A**ctuators — gli attuatori a disposizione dell'agente per agire,
- **S**ensors — i sensori a disposizione dell'agente per percepire.

Specificare il PEAS è il primo passo, sistematico e imprescindibile, nella progettazione di qualunque agente: obbliga a chiarire esplicitamente cosa l'agente deve ottenere, dove opera, come può agire e cosa può percepire.

### 2.5 Proprietà dell'ambiente (task environment)

Ogni ambiente può essere caratterizzato lungo sette dimensioni indipendenti. Questa classificazione è fondamentale perché **determina quali tecniche di progettazione dell'agente sono necessarie o sufficienti** (ambienti più "difficili" richiedono agenti più sofisticati).

| Proprietà | Valore 1 | Valore 2 |
|---|---|---|
| **Osservabilità** | **Completamente osservabile**: in ogni istante i sensori danno accesso a tutti gli aspetti dell'ambiente rilevanti per scegliere l'azione | **Parzialmente osservabile**: i sensori danno accesso solo a parte dell'informazione rilevante (per sensori imprecisi o incapaci di rilevare certi dati) |
| **Determinismo** | **Deterministico**: lo stato successivo è determinato univocamente dallo stato corrente e dall'azione eseguita | **Stocastico**: applicando più volte la stessa azione nello stesso stato si possono raggiungere stati diversi. Caso particolare: **strategico** se lo stocasticismo dipende solo dalle azioni di altri agenti (non dal caso puro) |
| **Episodicità** | **Episodico**: l'esperienza è divisa in episodi atomici indipendenti, ciascuno = una percezione seguita da una singola azione (es. classificazione di immagini) | **Sequenziale**: l'attività è composta da più passi collegati, ognuno dei quali influenza in generale i successivi |
| **Dinamicità** | **Statico**: l'ambiente non cambia mentre l'agente "pensa" (cioè mentre decide quale azione eseguire) | **Dinamico**: l'ambiente può cambiare mentre l'agente sta ancora decidendo |
| **Discretezza** | **Discreto**: stato, tempo, percezioni e azioni sono discreti (es. gli scacchi: stati, percezioni e azioni discreti) | **Continuo**: stato, tempo, percezioni o azioni sono continui (es. gli scacchi hanno tempo continuo, se cronometrati) |
| **Numero di agenti** | **Singolo agente**: viene modellata come agente una sola entità | **Multiagente**: vengono modellate come agenti più entità distinte |

**Note importanti (chiarimenti impliciti nelle slide):**

- **Connessione tra parzialmente osservabile e stocastico**: spesso un ambiente appare stocastico proprio perché è parzialmente osservabile — non percependo tutti gli aspetti rilevanti, l'agente non riesce a prevedere con certezza l'esito delle proprie azioni, anche se "in realtà" il mondo sottostante è deterministico. Esempio: una batteria la cui carica reale si consuma in modo continuo, ma l'agente percepisce solo tre stati discreti (bassa/media/alta). La stessa azione "passo", eseguita quando la carica percepita è "media", può risultare in "carica bassa" oppure "rimane media", perché l'agente non vede il livello esatto e continuo di carica residua.
- **Come decidere cosa modellare come agente (singolo/multiagente)**: il progettista deve decidere quali entità del mondo trattare come agenti e quali come parte dell'ambiente. Criterio: vanno modellate come agenti le entità il cui comportamento tenta di **massimizzare una propria misura di prestazione che dipende anche dal comportamento di altri agenti** (interazione strategica). Se un'entità si comporta in modo puramente meccanico/prevedibile senza obiettivi propri, può essere trattata come parte dell'ambiente.
- Il **caso più complesso e generale** (e più realistico per problemi reali) è un ambiente **parzialmente osservabile, stocastico, sequenziale, dinamico, continuo e multiagente**.

#### Esempi di caratterizzazione di ambienti (dalle slide)

| Ambiente | Osservabilità | Agenti | Determinismo | Episodicità | Dinamicità | Discretezza |
|---|---|---|---|---|---|---|
| **Parole crociate** | totale | singolo | deterministico | sequenziale | statico | discreto |
| **Guidare un taxi** | parziale | multiagente | stocastico | sequenziale | dinamico | continuo |
| **Tutor di inglese interattivo** | parziale | multiagente | stocastico | sequenziale | dinamico | discreto |
| **Analizzatore di immagini** | totale | singolo | deterministico | episodico | statico | continuo |

Questi esempi mostrano bene lo spettro di difficoltà: le parole crociate sono l'ambiente "più semplice" possibile (tutte le proprietà nella colonna "facile"), guidare un taxi è vicino al caso più complesso possibile (quasi tutte le proprietà nella colonna "difficile") — coerentemente col fatto che guidare in un ambiente reale è un problema molto più arduo da automatizzare rispetto a risolvere cruciverba.

#### Esempio guida: il termostato

- **Percepisce**: la temperatura della stanza.
- **Delibera**: decide quale azione eseguire.
- **Agisce**: accende/spegne il riscaldamento, oppure non fa nulla (comportamento predefinito).

È l'esempio più semplice possibile di ciclo percezione→delibera→azione: mostra il funzionamento essenziale di un agente anche senza nessuna sofisticazione interna.

#### Esempio guida: robot aspirapolvere (Roomba e simili)

- **Percepisce**: ostacoli (oggetti, scale) e livello della batteria.
- **Delibera**: decide quale azione eseguire.
- **Agisce**: si muove, si ferma, gira, oppure va alla stazione di ricarica (comportamento predefinito quando la batteria è scarica).

Da notare: sia il termostato sia il Roomba hanno un "comportamento predefinito" per i casi non altrimenti gestiti (non fare nulla / andare a ricaricarsi) — un modo semplice per garantire che l'agente abbia sempre un'azione definita anche in assenza di condizioni specifiche riconosciute.

### 2.6 Agente = architettura + programma

- **Architettura**: la specifica degli elementi strutturali e funzionali su cui il programma agente viene eseguito (l'hardware/piattaforma, es. un robot fisico o una macchina virtuale).
- **Programma**: la funzione che mette in relazione le percezioni con le azioni.

Distinzione importante tra due nozioni spesso confuse:
- **Funzione agente**: un'astrazione matematica che ha come input **l'intera sequenza percettiva** (la storia completa delle percezioni) e restituisce un'azione. È una descrizione ideale, esaustiva, di come l'agente *dovrebbe* comportarsi per ogni possibile storia di percezioni.
- **Programma agente**: l'implementazione concreta, che tipicamente ha come input solo la **percezione corrente** (eventualmente insieme a uno stato interno che riassume la storia passata, per non dover ricordare l'intera sequenza percettiva esplicitamente).

### 2.7 Tipologie di agente

Le slide presentano cinque tipologie di agente, in ordine di sofisticazione crescente. Questa è una delle tassonomie più importanti del modulo (corrisponde alla struttura del cap. 2 di Russell & Norvig).

#### 2.7.1 Agenti reattivi semplici

Basano la scelta dell'azione **solo sulla percezione corrente**, ignorando la storia passata. Il programma codifica direttamente delle **regole condizione-azione** ("se percepisco X, faccio Y"). È un agente scritto ad hoc per un problema specifico.

Esempio (aspirapolvere reattivo):
```
Aspirapolvere-reattivo(posizione, stato) return azione
{
   if (stato = sporco) then return aspira
   else if (posizione = A) then return destra
   else if (posizione = B) then return sinistra
}
```

Schema generale:
```
Agente-reattivo-semplice(percezione) return azione
{
   stato ← interpreta(percezione)
   regola ← individua-regola(stato, regole)
   azione ← regola-azione(regola)
   return azione
}
```
La percezione viene interpretata per identificare uno stato; lo stato individua la regola applicabile; la regola determina l'azione da eseguire. L'insieme delle regole definisce interamente il comportamento dell'agente.

**Limiti degli agenti reattivi semplici:**
- Funzionano correttamente solo in ambienti **completamente osservabili**.
- Esempio: se l'aspirapolvere non ha un sensore di posizione, e la cella corrente è pulita, non sa in che direzione muoversi per essere efficace (non sa dove si trova nel mondo). Questo può generare **loop infiniti** (es. [pulito] → destra → [pulito] → destra → ...) perché l'agente ripete sempre la stessa scelta in presenza della stessa percezione. Per rompere questi loop occorre introdurre comportamenti **casuali (random)**.
- L'azione deve essere determinabile dalla sola percezione corrente: se, ad esempio, l'aspirapolvere potesse leggere un solo sensore alla volta (o sporco/pulito, o posizione, ma non entrambi insieme), non saprebbe come comportarsi in modo affidabile.

#### 2.7.2 Agenti reattivi basati su modello

In caso di **osservabilità parziale**, un agente puramente reattivo non basta: serve un **modello del mondo**, cioè una rappresentazione interna di **come il mondo evolve** e di **quali effetti hanno le azioni**. L'agente mantiene uno **stato interno** che viene aggiornato combinando: (1) la percezione corrente, (2) lo stato interno precedente, (3) l'ultima azione eseguita, (4) il modello del mondo.

Schema:
```
Agente-reattivo-con-modello(percezione) return azione
{
   stato ← aggiorna-stato(stato, azione, percezione)
   regola ← individua-regola(stato, regole)
   azione ← regola-azione(regola)
}
```

**Esempio (batteria)**: il modello dice che "tre passi consumano una tacca di batteria". Se la sequenza percettiva ha mostrato "2 tacche" per tre volte consecutive dopo tre azioni "passo", il modello permette di **prevedere** che dopo il prossimo "passo" la batteria scenderà a 1 tacca, anche se il sensore, in un dato istante, non fornisce l'informazione precisa e continua sul livello di carica. Avere un modello permette quindi di **prevedere gli effetti delle azioni** e scegliere l'azione anche sulla base di questa previsione, superando il non-determinismo apparente dovuto all'osservabilità parziale (si ricollega alla nota del §2.5 su parziale osservabilità/stocasticità).

#### 2.7.3 Agenti basati su obiettivi (goal-driven)

L'agente sceglie l'azione da eseguire in base ai propri **obiettivi**: l'azione scelta deve avvicinarlo all'obiettivo o farglielo raggiungere. La decisione può riguardare solo il prossimo singolo passo, oppure può richiedere di guardare più avanti nel tempo, costruendo un **piano** di più passi.

Meccanismo tipico: il **ragionamento ipotetico** — l'agente "simula" mentalmente l'effetto delle azioni possibili per valutare se e quanto lo avvicinano all'obiettivo, prima di eseguirle realmente.

**Vantaggio chiave**: separando esplicitamente l'obiettivo dal meccanismo di ragionamento, basta **cambiare l'obiettivo** per ottenere comportamenti completamente diversi dallo stesso agente, senza riscrivere le regole di comportamento (a differenza dell'agente reattivo, dove il comportamento è "cablato" nelle regole condizione-azione).

#### 2.7.4 Agenti basati sull'utilità (utility-driven)

Alla nozione di obiettivo (raggiunto/non raggiunto, binario) si aggiunge una **misura di prestazione più fine**, calcolata da una **funzione di utilità**, che valuta quanto "buona" sia una scelta tenendo conto di più fattori contemporaneamente: costo, velocità, difficoltà attuativa, tempo, risorse utilizzate, ecc.

**Esempio**: per raggiungere una località possono esserci più percorsi alternativi (strade sterrate, percorso cittadino, strada veloce a pagamento). Il problema non è solo *trovare una soluzione* (un qualunque percorso che arrivi a destinazione) ma trovarne una che **massimizzi la soddisfazione** ("ci rende felici") secondo criteri come rapidità, costo, comodità.

**Distinzione obiettivo/utilità:**
- **Obiettivo (goal)**: uno stato particolare che si vuole raggiungere, tipicamente descritto in termini di proprietà da soddisfare (es. "essere arrivato a destinazione").
- **Utilità**: una funzione che, dato uno stato (o una sequenza di stati), restituisce una misura numerica di bontà.
- L'agente ha quindi un **duplice problema**: (1) raggiungere l'obiettivo, e (2) farlo massimizzando l'utilità. Da qui la distinzione tra **soluzioni** (qualunque sequenza di azioni che raggiunge il goal) e **buone soluzioni** (quelle che, tra le soluzioni possibili, massimizzano l'utilità).

#### 2.7.5 Agenti che apprendono

Aggiungono all'agente "classico" (che percepisce, decide, agisce) un ulteriore componente dedicato all'**apprendimento**, composto da tre elementi:
1. **Critico**: valuta il livello di prestazione dell'agente e decide se e quando attivare l'apprendimento (confrontando il comportamento con uno standard esterno di prestazione).
2. **Modulo di apprendimento**: modifica effettivamente la conoscenza/il comportamento dell'agente sulla base del feedback del critico.
3. **Generatore di problemi**: suggerisce/causa l'esecuzione di **azioni esplorative**, il cui scopo è esporre l'agente a nuove esperienze (anche non immediatamente ottimali) da cui poter imparare qualcosa di utile per il futuro.

Le slide precisano che non si fanno assunzioni su **quali segnali o tecniche specifiche** l'agente usi per apprendere: il concetto di "agente che apprende" è uno schema architetturale generale, indipendente dall'algoritmo di apprendimento concreto (che sarà oggetto di moduli successivi del corso, es. machine learning).

### 2.8 Tabella riassuntiva delle tipologie di agente

| Tipo di agente | Cosa usa per decidere | Punti di forza | Limiti |
|---|---|---|---|
| **Reattivo semplice** | Solo la percezione corrente + regole condizione-azione | Semplice, veloce, poco costoso da implementare | Funziona solo se l'ambiente è completamente osservabile; rischio di loop infiniti; nessuna "memoria" |
| **Reattivo basato su modello** | Percezione corrente + stato interno + modello di come evolve il mondo | Gestisce l'osservabilità parziale, "compensa" i limiti dei sensori con la conoscenza | Il modello va costruito e mantenuto correttamente; ancora nessun concetto esplicito di obiettivo |
| **Basato su obiettivi** | Percezione + modello + un obiettivo esplicito da raggiungere (eventuale pianificazione/ricerca) | Flessibile: basta cambiare l'obiettivo per cambiare comportamento; permette ragionamento ipotetico "what-if" | Non distingue tra soluzioni diverse che raggiungono comunque l'obiettivo (nessuna nozione di "quanto bene") |
| **Basato sull'utilità** | Come sopra + una funzione di utilità che valuta la qualità degli stati/soluzioni | Permette di scegliere la *migliore* tra più soluzioni possibili, bilanciando più criteri (costo, tempo, rischio...) | Richiede di saper definire e calcolare una funzione di utilità adeguata, spesso non banale |
| **Che apprende** | Tutto quanto sopra + un ciclo di apprendimento (critico, modulo di apprendimento, generatore di problemi) | Migliora nel tempo, si adatta a condizioni non previste in fase di progettazione | Maggiore complessità architetturale; richiede segnali di valutazione (feedback) adeguati |

---

## 3. Paradigmi di programmazione e agenti autonomi

### 3.1 Dall'approccio tradizionale (imperativo/a oggetti) all'approccio dichiarativo

Le slide confrontano due modi opposti di strutturare il software, per far capire perché il software di IA richiede spesso un cambio di paradigma rispetto alla programmazione tradizionale.

**Approccio tradizionale — paradigma imperativo / a oggetti (non-AI software):**
- Risolve **un singolo compito specifico**.
- È tipicamente strutturato come una **sequenza di passi** che descrivono esplicitamente **come (how)** ottenere il risultato.
- Esempio dalle slide: una funzione C che inserisce un elemento in una lista ordinata (`ins_ord`), scritta come una sequenza esplicita di operazioni sui puntatori — il programmatore ha già codificato *passo passo* l'algoritmo che produce il risultato.

**Approccio dichiarativo (AI software):**
- Separa una **descrizione dichiarativa** del problema (**cosa (what)** si vuole/si sa) da un **programma generale** (motore di inferenza/ricerca) che sa elaborare tale descrizione.
- Lo **stesso programma generale** può essere applicato a **descrizioni diverse** per risolvere **problemi diversi**, senza essere riscritto.
- Architettura tipica: una **base di conoscenza (Knowledge Base)** contiene la rappresentazione dichiarativa di un corpo di conoscenze applicabile a molteplici situazioni; le **percezioni** vengono via via integrate in questa conoscenza; un **modulo deliberativo** generale interroga (query) la base di conoscenza per decidere l'azione.

**Perché questo cambio di paradigma è importante per l'IA?** Perché nei problemi "intelligenti" tipicamente non conosciamo a priori la sequenza esatta di passi che risolve il problema (a differenza dell'inserimento ordinato in una lista, che ha un algoritmo noto e fisso): vogliamo invece che sia il sistema stesso, dato un obiettivo e una descrizione del mondo, a **costruire** la sequenza di passi giusta. Per questo, come si vede nell'esempio del mondo dei blocchi, "il programma dell'agente costruisce un programma" — cioè elabora la conoscenza (le mosse possibili) per generare esso stesso la soluzione, invece di eseguire una soluzione già scritta dal programmatore.

### 3.2 Esempio guida: il mondo dei blocchi (Blocks World)

Il **mondo dei blocchi** è un classico problema giocattolo (*toy problem*) dell'IA, usato per illustrare in modo semplice il funzionamento di un agente dichiarativo/deliberativo.

**Setup**: alcuni blocchi (etichettati A, B, C, D, E, F, G nelle slide) sono disposti impilati su un piano diviso in postazioni (1, 2, 3, 4). L'agente percepisce la configurazione (stato) **iniziale** dei blocchi.

**Passaggi concettuali:**
1. **Percezione**: l'agente percepisce la situazione iniziale. Di per sé, in questo momento, **non fa nulla**: la sola percezione non genera azione.
2. **Definizione del goal**: per agire, occorre prima descrivere un **obiettivo** (goal), cioè uno stato di cose che si vuole rendere vero (es. una certa configurazione finale desiderata dei blocchi, diversa da quella iniziale).
3. **Costruzione del piano**: l'agente deve costruire autonomamente la sequenza di passi/azioni (a₁, a₂, ..., aₖ) che porta dallo stato iniziale (I) allo stato goal (G): `I → a₁ → a₂ → ... → aₖ → G`.
4. **Conoscenza delle azioni**: per farlo, l'agente deve avere/usare conoscenza su quali azioni sono disponibili (es. "Prendi(blocco)", "Impila(blocco, blocco)", "Metti(blocco, posizione)"), su quando ciascuna azione è **applicabile** (precondizioni) e quali sono i suoi **effetti** sul mondo.
5. **Ragionamento**: l'agente deve ragionare per determinare quali azioni, tra tutte quelle applicabili, effettivamente avvicinano (o portano) al goal.

**Perché serve ricerca**: localmente, nello stato iniziale, potrebbero esserci molte mosse possibili (es. Prendi(B), Prendi(C), Prendi(E)), ma solo alcune di esse sono davvero utili per raggiungere lo stato finale desiderato. Il problema di **come scegliere** tra le mosse possibili è esattamente il problema della **ricerca nello spazio degli stati**, che verrà approfondito nei moduli successivi.

**Soluzione trovata dall'agente** (esempio dalle slide): una sequenza concreta come `Prendi(C), Metti(C,4), Prendi(B), Impila(B,D), Prendi(C), Impila(C,A), ...` ecc. Il punto concettuale fondamentale è che **il programma dell'agente costruisce un programma**: elabora la conoscenza sulle mosse possibili per generare autonomamente la sequenza di azioni risolutiva, che il progettista non aveva scritto esplicitamente in anticipo.

Domande aperte lasciate dalle slide (che anticipano temi futuri): possono esistere più soluzioni alternative allo stesso problema? Tra più soluzioni possibili, qual è la migliore? (Questo si ricollega alla distinzione soluzione/soluzione ottima e agli agenti basati sull'utilità.)

### 3.3 Dal problema giocattolo al problema reale

Il mondo dei blocchi è deliberatamente un **toy problem**: stati discreti, ambiente completamente osservabile, deterministico, un solo agente. Le slide chiedono esplicitamente: *cosa succede se ci spostiamo nel mondo reale?* — riprendendo l'esempio dell'attraversamento della strada, che è invece un ambiente **complesso, parzialmente prevedibile, parzialmente collaborativo**.

**Esempio: identificare un passaggio pedonale da un'immagine reale.** Quando una telecamera cattura un'immagine di strisce pedonali, non "vede" delle strisce come le vediamo noi: cattura solo **pixel**, cioè codifiche numeriche di colori con cui l'immagine viene approssimata digitalmente. Fattori che complicano ulteriormente il problema: prospettiva, colore, qualità dell'immagine, necessità di estrarre l'oggetto dal contesto, modi alternativi con cui la stessa scena può essere rappresentata.

**Punto concettuale chiave**: "vedere" (per un agente artificiale) non significa incamerare passivamente dei dati grezzi, ma **elaborare quei dati fino a trasformarli in informazioni**, secondo modelli che noi umani (e molti animali) sappiamo costruire autonomamente e quasi senza sforzo cosciente. Le slide notano anche un dettaglio sottile: "vediamo" le strisce pedonali (cioè le notiamo, le processiamo come rilevanti) **solo quando ci interessa attraversare** — la percezione utile è già guidata da un obiettivo/contesto, non è un processo neutro.

Questo esempio mostra la distanza enorme tra un toy problem come il mondo dei blocchi (dati già simbolici e puliti: "il blocco A è sopra B") e un problema reale (dati grezzi, numerici, ambigui, da interpretare) — ed è uno dei motivi per cui l'IA moderna dedica un'enorme quantità di sforzi alla percezione (visione artificiale, elaborazione del linguaggio, ecc.), argomenti trattati in moduli successivi.

### 3.4 Da automazione ad autonomia

- **Automazione**: ormai uno standard consolidato in moltissime attività. Richiede di programmare il dispositivo per compiere esplicitamente **ogni singolo passo**. È applicabile bene in domini fortemente **ripetitivi** e prevedibili (es. un robot di saldatura in una catena di montaggio industriale, che esegue sempre la stessa sequenza fissa di movimenti).
- **Autonomia**: un agente artificiale autonomo riceve **compiti ad alto livello** (goal), e l'utente/operatore demanda all'agente stesso il compito di trovare **come** risolverli concretamente — non gli vengono più specificati i singoli passi.

**Agente autonomo — caratteristiche:**
- In quanto agente, possiede capacità di azione.
- Essendo *autonomo*, in particolare:
  - riceve solo compiti ad alto livello (non istruzioni passo-passo),
  - ragiona ed esplora alternative (spesso in numero esponenziale, dato che a ogni istante possono esserci molte mosse possibili),
  - riconosce quando una linea di azione non è più percorribile (vicolo cieco),
  - riconosce se è già stato in una situazione già esplorata (evitando cicli/ripetizioni inutili),
  - semplificando: **prima ragiona e poi agisce**, cioè costruisce un piano (un "programma" per sé stesso) e poi lo esegue.

**Autonomia e controllabilità — un equivoco comune**: al di fuori della comunità di IA, gli agenti autonomi vengono talvolta percepiti come *"a self-conscious, uncontrollable entity whose autonomy emerges as a property extra-program"* — cioè come entità semi-coscienti e incontrollabili la cui autonomia "emerge" al di fuori/al di sopra del programma che le governa, quasi per magia, e che potrebbero prendere iniziative mai codificate.

Le slide **correggono esplicitamente** questo fraintendimento: in IA, gli agenti autonomi sono semplicemente **un modo di concepire i programmi**, in cui il **controllo** (la logica di alto livello, il modello del mondo e degli obiettivi) è chiaramente **separato** dai dettagli implementativi di basso livello. **Un agente fa sempre e soltanto ciò che è stato programmato a fare** — semplicemente, ciò che è stato programmato è "persegui questo obiettivo trovando tu stesso i passi necessari", non "esegui questi passi specifici". Non c'è nulla di misterioso o "emergente extra-programma": l'autonomia è essa stessa un costrutto di progettazione, non un'evasione dal programma.

> ❓ **Domanda d'esame: un agente autonomo può fare cose che non erano previste dal suo programma?**
> No, nel senso tecnico usato in IA. Un agente autonomo esegue sempre il proprio programma; la differenza rispetto a un sistema automatizzato tradizionale è che il programma stesso è scritto per **ragionare e generare piani** in risposta a obiettivi di alto livello, invece di eseguire una sequenza di passi fissata a priori dal programmatore. Le azioni "nuove" che l'agente compie sono il risultato del ragionamento interno (esplorazione di alternative, pianificazione), non un'evasione dal codice: rimangono sempre "ciò che il programma, dato l'input, calcola di fare". La percezione popolare di un'autonomia "incontrollabile ed emergente" è quindi un fraintendimento da correggere.

### 3.5 Gradi di autonomia: tre esempi concreti a confronto

Le slide usano tre sistemi reali per mostrare che **autonomia non è un concetto binario**, ma una questione di **grado**, che dipende dalla complessità dell'ambiente in cui l'agente opera.

| Sistema | Ambiente | Sensori | Azioni | Grado di autonomia |
|---|---|---|---|---|
| **Metropolitana automatica** | "Semplice": una rotaia fissa, un punto di partenza e uno di arrivo definiti | velocità, accelerazione, posizione, stato porte | accelera / decelera | Bassa: l'azione successiva è calcolata in modo **deterministico** dato lo stato; percorso fisso, nessuna vera decisione strategica |
| **Rover su Marte** | Ancora relativamente "semplice": una piana più o meno regolare, qualche roccia, ma **niente altri agenti né fenomeni atmosferici complessi** da gestire | distanza, contatto, telecamera, velocità, accelerazione, posizione | accelera/decelera, gira | Media/parziale: introduce la nozione di **"goal programmabile"** — un operatore umano assegna solo la destinazione, non i singoli movimenti. Necessaria per via del ritardo di comunicazione radio (~14 minuti in media): il rover deve poter decidere da solo come muoversi verso il goal senza attendere istruzioni in tempo reale |
| **Auto senza guidatore** | Complesso: strada affollata di altri agenti (auto, pedoni, animali), condizioni atmosferiche variabili (pioggia), giorno/notte, comportamento altrui imprevedibile | distanza, contatto, telecamera, velocità, accelerazione, posizione | accelera/decelera, gira | Alta: il goal (destinazione) è fornito dall'operatore, ma l'agente deve gestire in autonomia un ambiente **multiagente e fortemente imprevedibile** |

Tutti e tre condividono lo stesso **ciclo agente** di base:
```
Agent loop:
1) Leggi i sensori
2) Applica la funzione di controllo alle letture (+ eventualmente il goal / la prossima tappa) e calcola la prossima azione (accelerazione/decelerazione, sterzata...)
3) Applica l'azione calcolata
```
Ciò che cambia drasticamente tra i tre casi non è la struttura del ciclo, ma la **complessità dell'ambiente** (numero di altri agenti, prevedibilità, dinamicità) e di conseguenza quanto la "funzione di controllo" al passo 2 debba essere sofisticata: da un calcolo deterministico semplice (metro) fino a un vero e proprio ragionamento su un ambiente multiagente incerto (auto autonoma).

### 3.6 Ragionare basta?

**No.** Il ragionamento da solo non è sufficiente per un agente reale, perché tipicamente si opera:
- in presenza di **incertezza**,
- in un mondo **non completamente conosciuto**,
- in presenza di **altri agenti** (persone o altri robot), i cui comportamenti non sono del tutto prevedibili o controllabili.

Per questo occorre **combinare** tre ingredienti insieme, in un ciclo continuo: **azioni** (che modificano concretamente il mondo), **percezioni** (che informano sullo stato del mondo, anche dopo che l'agente ha agito), e **ragionamento** (che decide cosa fare sulla base di percezioni e conoscenza). Nessuno dei tre, da solo, è sufficiente: il ragionamento senza percezione aggiornata lavorerebbe su informazioni obsolete; la percezione senza ragionamento non produrrebbe decisioni; senza azione, nulla di quanto deciso avrebbe effetto sul mondo.

**Esempio applicativo reale — miniere automatizzate**: aziende come Rio Tinto Group (Australia), la miniera di Bingham Canyon (Utah), o EEP Elektro-Elektronik Pranjic (azienda tedesca che automatizza miniere in Cina) utilizzano camion autonomi (es. Komatsu driverless trucks) per attività come trivellazione e brillamento autonomi, controllo di flotte di veicoli, trasporto autonomo del materiale (*autonomous haulage*), evitamento di ostacoli e navigazione. È un esempio concreto di dominio industriale reale in cui l'autonomia (nel senso tecnico appena definito) è già impiegata su larga scala.

### 3.7 Approfondimento facoltativo: sistemi multiagente (MAS)

*(Contrassegnato "FACOLTATIVO" nelle slide — riportato per completezza.)*

- Un **sistema multiagente (MAS)** è costituito da un insieme di agenti che operano in uno stesso ambiente, potendo **competere o collaborare** nell'uso delle risorse condivise e nel perseguimento dei propri obiettivi (individuali o comuni).
- Per interagire efficacemente, agenti anche implementati in modo indipendente ed eterogeneo devono condividere: (1) un'**ontologia** del dominio del discorso (per attribuire lo stesso significato ai termini usati), (2) un **linguaggio di comunicazione** comune, (3) un **protocollo di interazione** condiviso (uno schema che coordina lo scambio di messaggi tra due o più agenti).
- **FIPA** (Foundation for Intelligent Physical Agents) ha standardizzato, a inizio anni 2000, una semantica formale per gli **atti comunicativi** (speech acts, es. `Request`, `Agree`, `Confirm`, `Cancel`, `Inform`, ecc.) e diversi protocolli di interazione standard (es. Contract Net, Brokering, Query Interaction Protocol).
- Esempio di atto comunicativo (`request`): l'agente *i* chiede all'agente *j* di consegnare una scatola (`box017`) in una certa posizione; *j* può rispondere con un `agree`, specificando eventualmente condizioni (es. bassa priorità).
- Strumenti software citati per l'implementazione di MAS: **JADE**, **Jason**, **CartAgO**, **JaCaMo**.

---

## Riepilogo e punti chiave

- **IA** = intelligenza non naturale, ottenuta con procedimenti tecnici. Nasce ufficialmente nel 1956 (Dartmouth Conference, John McCarthy), ma affonda le radici nei lavori di Turing (Macchina di Turing 1936, Test di Turing 1950).
- **Automazione ≠ intelligenza**: eseguire automaticamente un programma non basta; serve capacità di adattarsi, decidere, eventualmente imparare.
- **Test di Turing**: valuta solo il comportamento osservabile (indistinguibilità umano/macchina); non garantisce comprensione reale (vedi esempio Valeria/Rossella: stesso output, comprensione diversa).
- **Stanza cinese (Searle)**: manipolare simboli sintatticamente secondo regole (come fa un programma) non implica comprensione semantica/intenzionalità — critica filosofica al comportamentismo del Test di Turing.
- **Strong AI** (riprodurre davvero l'intelligenza/il pensiero umano) vs. **Weak AI** (costruire sistemi che risolvono task "intelligenti" in modo task-oriented, senza doverne replicare i meccanismi interni umani); il corso adotta l'ottica "agire razionalmente" (weak AI).
- Le **quattro scuole** di definizione dell'IA nascono dall'incrocio di due assi: pensiero/comportamento × fedeltà umana/razionalità.
- **Agente** = astrazione che percepisce l'ambiente tramite sensori e agisce tramite attuatori; agente e ambiente sono un binomio inscindibile; la funzione deliberativa ("?") decide l'azione in base a ciò che è stato percepito.
- **Sequenza percettiva** = storia completa delle percezioni ricevute; la scelta dell'azione può dipendere dall'intera sequenza o solo dalla percezione corrente.
- **Razionalità**: un agente razionale sceglie sempre l'azione che massimizza la **misura di prestazione attesa**, data la sequenza percettiva e la conoscenza dell'ambiente disponibili — dipende da 4 fattori: azioni disponibili, performance measure, conoscenza dell'ambiente, sequenza percettiva.
- **Razionale ≠ onnisciente, razionale ≠ "di successo"**: la razionalità si valuta rispetto a ciò che si poteva ragionevolmente sapere, non rispetto al risultato ideale con informazione completa. Un agente razionale migliora se impara dall'esperienza. La percezione stessa è parte della decisione razionale (es. guardare prima di attraversare).
- **PEAS** (Performance, Environment, Actuators, Sensors) = i quattro elementi che definiscono un task environment; primo passo obbligato nella progettazione di ogni agente.
- Le **7 proprietà dell'ambiente**: osservabilità (completa/parziale), determinismo (deterministico/stocastico), episodicità (episodico/sequenziale), dinamicità (statico/dinamico), discretezza (discreto/continuo), numero di agenti (singolo/multiagente). Il caso più complesso: parzialmente osservabile + stocastico + sequenziale + dinamico + continuo + multiagente.
- **Agente = architettura + programma**; distinzione tra **funzione agente** (input: intera sequenza percettiva, astrazione ideale) e **programma agente** (input: percezione corrente + eventuale stato interno, implementazione reale).
- **Cinque tipi di agente**, crescenti in sofisticazione: reattivo semplice → reattivo basato su modello → basato su obiettivi → basato sull'utilità → che apprende. Ognuno risolve i limiti del precedente (osservabilità parziale, scelta tra soluzioni alternative, miglioramento nel tempo).
- **Paradigma dichiarativo** (tipico del software di IA): separa la descrizione *cosa si sa/si vuole* (knowledge base) da un motore generale di ragionamento/ricerca che genera esso stesso la soluzione, a differenza del paradigma imperativo che codifica esplicitamente *come* risolvere un singolo problema specifico.
- **Mondo dei blocchi**: esempio classico di toy problem per illustrare come un agente, dati uno stato iniziale, un goal e la conoscenza delle azioni disponibili, debba esso stesso costruire (tramite ricerca/ragionamento) la sequenza di passi risolutiva — "un programma che costruisce un programma".
- **Automazione vs. autonomia**: l'automazione richiede di specificare ogni passo (adatta a domini ripetitivi); l'autonomia consiste nel ricevere solo obiettivi di alto livello e nel dedurre da sé i passi necessari, tramite ragionamento ed esplorazione di alternative. L'autonomia **non** significa comportamento incontrollabile o "extra-programma": un agente autonomo esegue sempre e solo il proprio programma, che è però progettato per pianificare, non per eseguire passi fissi.
- L'autonomia è **graduale**, non binaria: dipende dalla complessità dell'ambiente (esempi: metropolitana automatica → rover marziano → auto a guida autonoma, con complessità e imprevedibilità crescenti).
- Il ragionamento da solo non basta in presenza di incertezza, mondo parzialmente conosciuto e altri agenti: serve sempre combinare **azioni + percezioni + ragionamento** in un ciclo continuo.
