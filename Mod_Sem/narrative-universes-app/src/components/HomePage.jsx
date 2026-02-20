import { useState, useEffect } from 'react';
import { getUniverses } from '../services/sparqlService';
import '../styles/HomePage.css';

/**
 * HomePage - Pagina principale dell'applicazione
 * Mostra la lista degli universi narrativi disponibili
 */
export default function HomePage({ onSelectUniverse }) {
    // Stato per memorizzare gli universi caricati
    const [universes, setUniverses] = useState([]);
    // Stato per gestire il caricamento
    const [loading, setLoading] = useState(true);
    // Stato per eventuali errori
    const [error, setError] = useState(null);

    // Funzione per recuperare gli universi dal servizio SPARQL
    async function fetchUniverses() {
        setError(null);
        setLoading(true);
        try {
            const data = await getUniverses();
            // Trasforma i risultati SPARQL in oggetti più semplici
            const results = data.results.bindings.map(b => ({
                uri: b.universe.value,
                name: b.name.value,
                description: b.description?.value || '',
                characters: parseInt(b.numCharacters.value),
                locations: parseInt(b.numLocations.value),
                works: parseInt(b.numWorks.value)
            }));
            setUniverses(results);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    // Carica gli universi al mount del componente
    useEffect(() => {
        fetchUniverses();
    }, []);

    // Stato di caricamento
    if (loading) {
        return (
            <div className="loading">
                <div className="spinner"></div>
                <p>Caricamento universi narrativi...</p>
            </div>
        );
    }

    // Stato di errore
    if (error) {
        return (
            <div className="error">
                <h2>Errore</h2>
                <p>{error}</p>
                <p className="error-hint">
                    Assicurati che GraphDB e il proxy server siano attivi
                </p>
                <button className="back-button" onClick={fetchUniverses}>Riprova</button>
            </div>
        );
    }

    // Mapping universo -> sigla per le icone
    const universeEmojis = {
        "Universo di Harry Potter": "HP",
        "Universo di Percy Jackson": "PJ",
        "Universo della Terra di Mezzo": "LOTR"
    };

    return (
        <div className="home-page">
            {/* Header con titolo e descrizione */}
            <header className="hero">
                <h1 className="hero-title">Esplora gli Universi Narrativi</h1>
                <p className="hero-subtitle">
                    Scegli un universo e scopri personaggi, luoghi, oggetti e opere che lo compongono
                </p>
            </header>

            {/* Griglia delle card degli universi */}
            <div className="universes-grid">
                {universes.map(universe => (
                    <div key={universe.uri} className="universe-card">
                        {/* Icona/sigla dell'universo */}
                        <div className="universe-icon">
                            {universeEmojis[universe.name] || "NU"}
                        </div>

                        <h2 className="universe-name">{universe.name}</h2>

                        {universe.description && (
                            <p className="universe-description">
                                {universe.description}
                            </p>
                        )}

                        {/* Statistiche: numero di personaggi, luoghi, opere */}
                        <div className="universe-stats">
                            <div className="stat">
                                <span className="stat-number">{universe.characters}</span>
                                <span className="stat-label">Personaggi</span>
                            </div>

                            <div className="stat">
                                <span className="stat-number">{universe.locations}</span>
                                <span className="stat-label">Luoghi</span>
                            </div>

                            <div className="stat">
                                <span className="stat-number">{universe.works}</span>
                                <span className="stat-label">Opere</span>
                            </div>
                        </div>

                        {/* Bottone per esplorare l'universo */}
                        <button
                            className="explore-button"
                            onClick={() => onSelectUniverse(universe)}
                        >
                            Esplora Universo →
                        </button>
                    </div>
                ))}
            </div>

            {/* Footer con crediti */}
            <footer className="home-footer">
                <a 
                    href="https://informatica.i-learn.unito.it/course/view.php?id=3571" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="footer-course-link"
                >
                    Progetto d'esame – Modellazione Concettuale per il Web Semantico aa.2025/2026
                </a>
                <p className="footer-authors">di Alessandro Olivero (matricola: 915069) e Giovanni Grillo (matricola: 989819)</p>
                
                <div className="footer-bottom-icon">
                    <a
                        className="github-link"
                        href="https://github.com/GiovanniGrillo"
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label="GitHub"
                        title="GitHub"
                    >
                        <svg className="github-icon" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
                            <path fill="currentColor" d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.46-1.17-1.12-1.49-1.12-1.49-.91-.63.07-.62.07-.62 1 .07 1.53 1.04 1.53 1.04.9 1.53 2.36 1.09 2.94.83.09-.66.35-1.1.64-1.35-2.22-.25-4.56-1.11-4.56-4.95 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02A9.56 9.56 0 0 1 12 7.58c.85 0 1.7.12 2.5.35 1.9-1.29 2.74-1.02 2.74-1.02.55 1.38.21 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.85-2.34 4.7-4.57 4.95.36.31.69.92.69 1.86v2.76c0 .26.18.58.69.48A10 10 0 0 0 12 2z"/>
                        </svg>
                    </a>
                </div>
            </footer>
        </div>
    );
}
