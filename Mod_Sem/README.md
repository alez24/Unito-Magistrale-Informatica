# Ontologia degli Universi Narrativi Crossmediali

## Progetto d'esame – Modellazione Concettuale per il Web Semantico

Questo progetto consiste nello sviluppo di un'ontologia OWL per la modellazione di **universi narrativi di finzione crossmediali**, ovvero mondi narrativi che si sviluppano attraverso più media (libri, film, serie TV, videogiochi, teatro).

Gli universi utilizzati come casi di studio principali sono:
- Harry Potter (HP)
- Percy Jackson (PJ)
- Il Signore degli Anelli (LOTR)

L'ontologia è progettata per essere **generale e riusabile**, permettendo il confronto strutturale tra universi narrativi diversi.

---

## Scopo dell'ontologia

L'ontologia permette di:
- descrivere universi narrativi, opere e media;
- modellare personaggi, luoghi, oggetti e organizzazioni;
- rappresentare ruoli narrativi (es. protagonista, mentore, antagonista);
- supportare analisi comparative e interrogazioni cross-universo;
- abilitare inferenze automatiche tramite reasoning OWL.

Il focus è sugli **elementi strutturali comuni** agli universi narrativi, non sulle singole trame.

---

## Requisiti software

Per visualizzare e modificare l'ontologia è necessario:
- **Protégé** (versione 5.x o superiore)

---

## Struttura del repository

- `02_ontologia/`: file OWL e TTL dell'ontologia
- `03_query/`: query SPARQL di esempio esportate da GraphDB
- `04_relazione/`: relazione LaTeX del progetto
- `narrative-universes-app/`: demo web per esplorare gli universi

---

## Avvio rapido demo web

Prerequisiti:
- GraphDB in locale con repository `narrative-universes`
- Node.js 20+

Passi:
1. Avvio proxy GraphDB:
   - `cd narrative-universes-app/server && npm i && npm start`
2. Avvio applicazione web:
   - `cd narrative-universes-app && npm i && npm run dev`
3. Aprire il browser su l’URL mostrato da Vite

---

## Autori

- Giovanni Grillo  
- Alessandro Olivero  

## Corso

Modellazione Concettuale per il Web Semantico  
Anno Accademico 2025/2026
