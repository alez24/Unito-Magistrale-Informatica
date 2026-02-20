import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { getUniverseDetails, getMoviesFromWikidata, getLotrMoviesFromWikidata, getPercyJacksonMoviesFromWikidata } from '../services/sparqlService';
import CharactersList from './CharactersList';
import LocationsList from './LocationsList';
import WorksList from './WorksList';
import '../styles/UniverseDashboard.css';

/**
 * UniverseDashboard - Dashboard principale di un universo narrativo
 * Gestisce la navigazione a tab tra personaggi, luoghi, opere e dati esterni
 */
export default function UniverseDashboard() {
  // Recupera l'URI dell'universo dai parametri URL
  const [params] = useSearchParams();
  const uri = params.get("uri");
  const navigate = useNavigate();

  // Stato dell'universo selezionato
  const [universe, setUniverse] = useState(null);
  // Tab attualmente attiva
  const [activeTab, setActiveTab] = useState('characters');
  // Gestione errori
  const [error, setError] = useState(null);

  // Dati film da Wikidata (caricati su richiesta)
  const [wikidataMovies, setWikidataMovies] = useState(null);
  const [loadingWikidata, setLoadingWikidata] = useState(false);

  // Carica i dettagli dell'universo
  const fetchUniverse = useCallback(async () => {
    try {
      const data = await getUniverseDetails(uri);
      const b = data.results.bindings[0];
      setUniverse({
        uri,
        name: b.name.value,
        characters: parseInt(b.numCharacters.value),
        locations: parseInt(b.numLocations.value),
        works: parseInt(b.numWorks.value),
      });
      setError(null);
    } catch (e) {
      setError(e.message || "Errore nel caricamento dell'universo");
    }
  }, [uri]);

  // Carica i film da Wikidata in base all'universo
  const loadWikidataInfo = async () => {
    setLoadingWikidata(true);
    try {
      let movies;
      // Seleziona la query appropriata in base all'universo
      if (universe.uri.endsWith('#HarryPotterUniverse')) {
        movies = await getMoviesFromWikidata(universe.uri);
      } else if (universe.uri.endsWith('#MiddleEarthUniverse')) {
        movies = await getLotrMoviesFromWikidata(universe.uri);
      } else if (universe.uri.endsWith('#PercyJacksonUniverse')) {
        movies = await getPercyJacksonMoviesFromWikidata(universe.uri);
      } else {
        movies = await getMoviesFromWikidata(universe.uri);
      }
      setWikidataMovies(movies.results.bindings);
    } catch (err) {
      console.error('Errore caricamento Wikidata:', err);
    } finally {
      setLoadingWikidata(false);
    }
  };

  // Effetto per caricare l'universo al cambio di URI
  useEffect(() => {
    fetchUniverse();
  }, [fetchUniverse]);

  // Stato di caricamento iniziale
  if (!universe && !error) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Caricamento universo...</p>
      </div>
    );
  }

  // Stato di errore
  if (error) {
    return (
      <div className="error">
        <h2>Errore</h2>
        <p>{error}</p>
        <button className="back-button" onClick={fetchUniverse}>Riprova</button>
      </div>
    );
  }

  // Definizione delle tab disponibili
  const tabs = [
    { id: 'characters', label: 'Personaggi', count: universe.characters },
    { id: 'locations', label: 'Luoghi', count: universe.locations },
    { id: 'works', label: 'Opere', count: universe.works },
    { id: 'wikidata', label: 'Dati Esterni', count: null },
  ];

  return (
    <div className="dashboard">
      {/* Header con info universo */}
      <div className="dashboard-header">
        <div className="universe-info">
          {/* Bottone per tornare alla home */}
          <button className="home-button" onClick={() => navigate('/')}>
            <span className="home-icon" aria-hidden="true" />
            <span className="sr-only">Torna alla home</span>
          </button>
          <h1 className="universe-title">{universe.name}</h1>
          {/* Meta-info con conteggi */}
          <div className="universe-meta">
            <span className="meta-item">{universe.characters} Personaggi</span>
            <span className="meta-separator">•</span>
            <span className="meta-item">{universe.locations} Luoghi</span>
            <span className="meta-separator">•</span>
            <span className="meta-item">{universe.works} Opere</span>
          </div>
        </div>
      </div>

      {/* Barra delle tab */}
      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
            {tab.count !== null && <span className="tab-count">{tab.count}</span>}
          </button>
        ))}
      </div>

      {/* Contenuto della tab attiva */}
      <div className="tab-content">
        {activeTab === 'characters' && <CharactersList universeUri={universe.uri} />}
        {activeTab === 'locations' && <LocationsList universeUri={universe.uri} />}
        {activeTab === 'works' && <WorksList universeUri={universe.uri} />}

        {/* Tab Wikidata: carica dati esterni su richiesta */}
        {activeTab === 'wikidata' && (
          <div className="wikidata-content">
            {!wikidataMovies && !loadingWikidata ? (
              <div className="external-info-section">
                <h3>Dati Esterni da Wikidata</h3>
                <p>Carica informazioni sui film dell'universo</p>
                <button className="fetch-external-btn" onClick={loadWikidataInfo}>
                  Carica dati da Wikidata
                </button>
              </div>
            ) : loadingWikidata ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Caricamento dati da Wikidata...</p>
              </div>
            ) : (
              <section className="wikidata-section">
                <h3>Film dell'universo</h3>
                <ul className="external-list">
                  {wikidataMovies?.map((movie, idx) => (
                    <li key={idx} className="external-item">
                      <div className="external-title">{movie.title?.value}</div>
                      <div className="external-meta">
                        <span className="source-badge">{movie.source?.value || 'N/A'}</span>
                        {movie.releaseYear && <span>Anno {movie.releaseYear.value}</span>}
                        {movie.duration && (
                          <span>{Math.round(parseFloat(movie.duration.value))} min</span>
                        )}
                        {movie.director?.value && <span>{movie.director.value}</span>}
                      </div>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
