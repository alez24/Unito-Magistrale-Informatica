const GRAPHDB_ENDPOINT = 'http://localhost:3001/sparql';

// Esegue una query SPARQL tramite proxy e restituisce JSON.
export async function executeQuery(query) {
    const response = await fetch(GRAPHDB_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/sparql-query',
            'Accept': 'application/sparql-results+json'
        },
        body: query
    });

    if (!response.ok) throw new Error('Query failed');
    return await response.json();
}

// Recupera lista di tutti gli universi narrativi con statistiche.
export async function getUniverses() {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?universe ?name (SAMPLE(?desc) AS ?description)
           (COUNT(DISTINCT ?character) AS ?numCharacters) 
           (COUNT(DISTINCT ?location) AS ?numLocations)
           (COUNT(DISTINCT ?work) AS ?numWorks)
    WHERE {
      ?universe a ontology:NarrativeUniverse ;
                rdfs:label ?name .
      OPTIONAL { ?universe ontology:description ?desc }
      OPTIONAL { 
        ?character a ontology:Character ;
                   ontology:belongsToUniverse ?universe 
      }
      OPTIONAL { 
        ?location a ontology:Location ;
                  ontology:belongsToUniverse ?universe 
      }
      OPTIONAL {
        ?work a ontology:NarrativeWork ;
              ontology:belongsToUniverse ?universe
      }
    }
    GROUP BY ?universe ?name
    ORDER BY ?name
  `;

    return executeQuery(query);
}

// Recupera personaggi per un dato universo.
export async function getCharactersByUniverse(universeUri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT DISTINCT ?character ?name ?type ?description
    WHERE {
      ?character a ontology:Character ;
                 rdfs:label ?name ;
                 ontology:belongsToUniverse <${universeUri}> .
      
      ?character rdf:type ?type .
      FILTER(STRSTARTS(STR(?type), STR(ontology:)))
      
      OPTIONAL { ?character ontology:description ?description }
    }
    ORDER BY ?name
  `;

    return executeQuery(query);
}

// Recupera opere narrative per un dato universo.
export async function getWorksByUniverse(universeUri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?work ?title ?type ?year ?runtime ?pages
    WHERE {
        ?work a ontology:NarrativeWork ;
              ontology:belongsToUniverse <${universeUri}> ;
              rdfs:label ?title .

        BIND(
            IF(EXISTS { ?work a ontology:Book }, "Book",
               IF(EXISTS { ?work a ontology:Movie }, "Movie",
                  IF(EXISTS { ?work a ontology:TelevisionSeries }, "TVSeries",
                     "NarrativeWork"
                  )
               )
            ) AS ?type
        )

        OPTIONAL { ?work ontology:publicationYear ?year }
        OPTIONAL { ?work ontology:runtime ?runtime }
        OPTIONAL { ?work ontology:numberOfPages ?pages }
    }
    ORDER BY ?title
    `;

    return executeQuery(query);
}

// Recupera luoghi per un dato universo.
export async function getLocationsByUniverse(universeUri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?location ?name ?type ?function ?danger
    WHERE {
        ?location a ontology:Location ;
                  ontology:belongsToUniverse <${universeUri}> ;
                  rdfs:label ?name .

        OPTIONAL { 
            ?location rdf:type ?typeRaw .
            FILTER(STRSTARTS(STR(?typeRaw), STR(ontology:)))
            BIND(STRAFTER(STR(?typeRaw), "#") AS ?type)
        }

        OPTIONAL { ?location ontology:hasNarrativeFunction ?function }
        OPTIONAL { ?location ontology:dangerLevel ?danger }
    }
    ORDER BY ?name
    `;

    return executeQuery(query);
}

// Recupera informazioni dettagliate e relazioni per un'entità.
export async function getEntityDetails(uri) {
    const baseQuery = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?type ?label (COALESCE(?desc, ?comment) AS ?description)
    WHERE {
        <${uri}> rdfs:label ?label .
        OPTIONAL { <${uri}> ontology:description ?desc }
        OPTIONAL { <${uri}> rdfs:comment ?comment }
        OPTIONAL {
            <${uri}> rdf:type ?typeRaw .
            FILTER(STRSTARTS(STR(?typeRaw), STR(ontology:)))
        }
        OPTIONAL {
            <${uri}> rdf:type/rdfs:subClassOf* ?typeSub .
            FILTER(STRSTARTS(STR(?typeSub), STR(ontology:)))
        }
        BIND(
            COALESCE(
              STRAFTER(STR(?typeRaw), "#"),
              STRAFTER(STR(?typeSub), "#"),
              "Unknown"
            ) AS ?type
        )
    }
    `;

    const base = await executeQuery(baseQuery);
    const info = base.results.bindings[0];

    const type = info.type.value.split('#').pop();

    let relations = {};

    if (type === 'Character') {
        relations = await getCharacterRelations(uri);
    } else if (type === 'Location') {
        relations = await getLocationRelations(uri);
    } else if (type === 'NarrativeWork') {
        relations = await getWorkRelations(uri);
    } else if (type === 'Object') {
        relations = await getObjectRelations(uri);
    }

    return {
        uri,
        type,
        label: info.label.value,
        description: info.description?.value || '',
        ...relations
    };
}

// Recupera relazioni per un personaggio (alleati, nemici, ecc.).
export async function getCharacterRelations(uri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?ally ?enemy ?mentor ?student ?object ?ability ?work ?org
    WHERE {
        OPTIONAL { <${uri}> ontology:alliedWith ?ally }
        OPTIONAL { <${uri}> ontology:enemyOf ?enemy }
        OPTIONAL { <${uri}> ontology:mentors ?student }
        OPTIONAL { ?mentor ontology:mentors <${uri}> }
        OPTIONAL { <${uri}> ontology:possesses ?object }
        OPTIONAL { <${uri}> ontology:hasAbility ?ability }
        OPTIONAL { <${uri}> ontology:appearsIn ?work }
        OPTIONAL { <${uri}> ontology:memberOf ?org }
    }
    `;

    const data = await executeQuery(query);

    const extract = field =>
        [...new Set(data.results.bindings
            .filter(b => b[field])
            .map(b => b[field].value))];

    return {
        allies: extract('ally'),
        enemies: extract('enemy'),
        mentors: extract('mentor'),
        students: extract('student'),
        objects: extract('object'),
        abilities: extract('ability'),
        works: extract('work'),
        organizations: extract('org')
    };
}

// Recupera relazioni per un luogo (opere, organizzazioni, ecc.).
export async function getLocationRelations(uri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?work ?org ?parent ?child ?function ?danger
    WHERE {
        OPTIONAL { ?work ontology:setIn <${uri}> }
        OPTIONAL { <${uri}> ontology:ospita ?org }
        OPTIONAL { <${uri}> ontology:partOf ?parent }
        OPTIONAL { ?child ontology:partOf <${uri}> }
        OPTIONAL { <${uri}> ontology:hasNarrativeFunction ?function }
        OPTIONAL { <${uri}> ontology:dangerLevel ?danger }
    }
    `;

    const data = await executeQuery(query);

    const extract = field =>
        [...new Set(data.results.bindings
            .filter(b => b[field])
            .map(b => b[field].value))];

    return {
        works: extract('work'),
        organizations: extract('org'),
        parentLocations: extract('parent'),
        childLocations: extract('child'),
        narrativeFunction: data.results.bindings[0]?.function?.value || null,
        dangerLevel: data.results.bindings[0]?.danger?.value || null
    };
}
// Recupera relazioni per un oggetto (proprietari, abilità, ecc.).
export async function getObjectRelations(uri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?owner ?ability ?ptype ?destroyable
    WHERE {
        OPTIONAL { ?owner ontology:possesses <${uri}> }
        OPTIONAL { <${uri}> ontology:grantsAbility ?ability }
        OPTIONAL { <${uri}> ontology:hasPowerTypeEnum ?ptype }
        OPTIONAL { <${uri}> ontology:canBeDestroyed ?destroyable }
    }
    `;

    const data = await executeQuery(query);

    const extract = field =>
        [...new Set(data.results.bindings
            .filter(b => b[field])
            .map(b => b[field].value))];

    return {
        owners: extract('owner'),
        abilities: extract('ability'),
        powerType: extract('ptype')[0] || null,
        canBeDestroyed: extract('destroyable')[0] || null
    };
}
// Recupera relazioni per un'opera narrativa (personaggi, luoghi, ecc.).
export async function getWorkRelations(uri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?character ?main ?location ?prequel ?sequel ?adapt
    WHERE {
        OPTIONAL { <${uri}> ontology:features ?character }
        OPTIONAL { <${uri}> ontology:hasMainProtagonist ?main }
        OPTIONAL { <${uri}> ontology:setIn ?location }
        OPTIONAL { <${uri}> ontology:prequelOf ?sequel }
        OPTIONAL { ?prequel ontology:prequelOf <${uri}> }
        OPTIONAL { <${uri}> ontology:adaptationOf ?adapt }
    }
    `;

    const data = await executeQuery(query);

    const extract = field =>
        [...new Set(data.results.bindings
            .filter(b => b[field])
            .map(b => b[field].value))];

    return {
        characters: extract('character'),
        mainProtagonist: extract('main')[0] || null,
        locations: extract('location'),
        prequels: extract('prequel'),
        sequels: extract('sequel'),
        adaptations: extract('adapt')
    };
}


// Recupera dettagli base e conteggi per un universo.
export async function getUniverseDetails(uri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?name
           (COUNT(DISTINCT ?character) AS ?numCharacters)
           (COUNT(DISTINCT ?location) AS ?numLocations)
           (COUNT(DISTINCT ?work) AS ?numWorks)
    WHERE {
        <${uri}> a ontology:NarrativeUniverse ;
                 rdfs:label ?name .

        OPTIONAL { ?character a ontology:Character ; ontology:belongsToUniverse <${uri}> }
        OPTIONAL { ?location a ontology:Location ; ontology:belongsToUniverse <${uri}> }
        OPTIONAL { ?work a ontology:NarrativeWork ; ontology:belongsToUniverse <${uri}> }
    }
    GROUP BY ?name
    `;

    return executeQuery(query);
}
// Recupera film da locale + Wikidata per universo Harry Potter.
export async function getMoviesFromWikidata(universeUri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    
    SELECT ?film ?title (MIN(?year) AS ?releaseYear) (SAMPLE(?directorName) AS ?director) (SAMPLE(?runtime) AS ?duration) ?source
    WHERE {
      {
        ?film a ontology:Movie ;
              rdfs:label ?title ;
              ontology:belongsToUniverse <${universeUri}> .
        
        OPTIONAL { ?film ontology:publicationYear ?year }
        OPTIONAL { ?film ontology:runtime ?runtime }
        
        BIND("Locale" AS ?source)
        BIND("" AS ?directorName)
      }
      UNION
      {
        SERVICE <https://query.wikidata.org/sparql> {
          VALUES ?wikidataFilm {
            wd:Q102244
            wd:Q102448
            wd:Q102225
            wd:Q102235
            wd:Q161687
            wd:Q161678
            wd:Q232009
          }
          
          ?wikidataFilm rdfs:label ?title ;
                        wdt:P577 ?releaseDate ;
                        wdt:P57 ?directorEntity .
          
          OPTIONAL { ?wikidataFilm wdt:P2047 ?runtime }
          
          ?directorEntity rdfs:label ?directorName .
          
          FILTER(LANG(?title) = "en")
          FILTER(LANG(?directorName) = "en")
          
          BIND(YEAR(?releaseDate) AS ?year)
          BIND(?wikidataFilm AS ?film)
          BIND("Wikidata" AS ?source)
        }
      }
    }
    GROUP BY ?film ?title ?source
    ORDER BY ?releaseYear
    `;

    return executeQuery(query);
}
// Recupera film da locale + Wikidata per universo LOTR.
export async function getLotrMoviesFromWikidata(universeUri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    
    SELECT ?film ?title (MIN(?year) AS ?releaseYear) (SAMPLE(?directorName) AS ?director) (SAMPLE(?runtime) AS ?duration) ?source
    WHERE {
      {
        ?film a ontology:Movie ;
              rdfs:label ?title ;
              ontology:belongsToUniverse <${universeUri}> .
        OPTIONAL { ?film ontology:publicationYear ?year }
        OPTIONAL { ?film ontology:runtime ?runtime }
        BIND("Locale" AS ?source)
        BIND("" AS ?directorName)
      }
      UNION
      {
        SERVICE <https://query.wikidata.org/sparql> {
          VALUES ?wikidataFilm {
            wd:Q164963
            wd:Q131074
            wd:Q80379
            wd:Q719915
            wd:Q919649
          }
          ?wikidataFilm rdfs:label ?title ;
                        wdt:P577 ?releaseDate ;
                        wdt:P57 ?directorEntity .
          OPTIONAL { ?wikidataFilm wdt:P2047 ?runtime }
          OPTIONAL { ?directorEntity rdfs:label ?directorName FILTER(LANG(?directorName)="en") }
          FILTER(LANG(?title) = "en")
          BIND(YEAR(?releaseDate) AS ?year)
          BIND(?wikidataFilm AS ?film)
          BIND("Wikidata" AS ?source)
        }
      }
    }
    GROUP BY ?film ?title ?source
    ORDER BY ?releaseYear
    `;
    return executeQuery(query);
}
// Recupera film da locale + Wikidata per universo Percy Jackson.
export async function getPercyJacksonMoviesFromWikidata(universeUri) {
    const query = `
    PREFIX ontology: <http://www.narrative-universes.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    
    SELECT ?film ?title (MIN(?year) AS ?releaseYear) (SAMPLE(?directorName) AS ?director) (SAMPLE(?runtime) AS ?duration) ?source
    WHERE {
      {
        ?film a ontology:Movie ;
              rdfs:label ?title ;
              ontology:belongsToUniverse <${universeUri}> .
        OPTIONAL { ?film ontology:publicationYear ?year }
        OPTIONAL { ?film ontology:runtime ?runtime }
        BIND("Locale" AS ?source)
        BIND("" AS ?directorName)
      }
      UNION
      {
        SERVICE <https://query.wikidata.org/sparql> {
          VALUES ?wikidataFilm {
            wd:Q2984104
          }
          ?wikidataFilm rdfs:label ?title ;
                        wdt:P577 ?releaseDate ;
                        wdt:P57 ?directorEntity .
          OPTIONAL { ?wikidataFilm wdt:P2047 ?runtime }
          OPTIONAL { ?directorEntity rdfs:label ?directorName FILTER(LANG(?directorName)="en") }
          FILTER(LANG(?title) = "en")
          BIND(YEAR(?releaseDate) AS ?year)
          BIND(?wikidataFilm AS ?film)
          BIND("Wikidata" AS ?source)
        }
      }
    }
    GROUP BY ?film ?title ?source
    ORDER BY ?releaseYear
    `;
    return executeQuery(query);
}
