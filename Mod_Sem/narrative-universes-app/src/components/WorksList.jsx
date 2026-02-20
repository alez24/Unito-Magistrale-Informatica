import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getWorksByUniverse } from '../services/sparqlService';
import '../styles/WorksList.css';

/**
 * WorksList - Lista delle opere narrative di un universo
 * Mostra libri, film e serie TV con filtri per tipo
 */
export default function WorksList({ universeUri }) {
    // Stato per le opere caricate
    const [works, setWorks] = useState([]);
    // Stato di caricamento
    const [loading, setLoading] = useState(true);
    // Filtro attivo (all, Book, Movie, TVSeries)
    const [filter, setFilter] = useState('all');

    const navigate = useNavigate();

    // Carica le opere al mount o al cambio di universo
    useEffect(() => {
        async function loadWorks() {
            try {
                const data = await getWorksByUniverse(universeUri);
                // Trasforma i risultati SPARQL in oggetti piu semplici
                const results = data.results.bindings.map(b => ({
                    uri: b.work.value,
                    title: b.title.value,
                    type: (() => {
                        const t = b.type?.value || 'NarrativeWork';
                        // Normalizza TelevisionSeries in TVSeries
                        return t === 'TelevisionSeries' ? 'TVSeries' : t;
                    })(),
                    year: b.year?.value || null,
                    runtime: b.runtime?.value || null,
                    pages: b.pages?.value || null
                }));
                setWorks(results);
            } catch (err) {
                console.error('Error loading works:', err);
            } finally {
                setLoading(false);
            }
        }

        loadWorks();
    }, [universeUri]);

    // Stato di caricamento
    if (loading) {
        return (
            <div className="loading-state">
                <div className="spinner"></div>
                <p>Caricamento opere...</p>
            </div>
        );
    }

    // Applica il filtro selezionato
    const filtered = works.filter(w => {
        if (filter === 'all') return true;
        return w.type === filter;
    });

    // Conteggi per i bottoni filtro
    const typeCounts = {
        all: works.length,
        Book: works.filter(w => w.type === 'Book').length,
        Movie: works.filter(w => w.type === 'Movie').length,
        TVSeries: works.filter(w => w.type === 'TVSeries').length
    };

    return (
        <div className="works-list">
            {/* Bottoni filtro per tipo di opera */}
            <div className="filters">
                <button className={filter === 'all' ? 'active' : ''} onClick={() => setFilter('all')}>
                    Tutte ({typeCounts.all})
                </button>

                {typeCounts.Book > 0 && (
                    <button className={filter === 'Book' ? 'active' : ''} onClick={() => setFilter('Book')}>
                        Libri ({typeCounts.Book})
                    </button>
                )}

                {typeCounts.Movie > 0 && (
                    <button className={filter === 'Movie' ? 'active' : ''} onClick={() => setFilter('Movie')}>
                        Film ({typeCounts.Movie})
                    </button>
                )}

                <button className={filter === 'TVSeries' ? 'active' : ''} onClick={() => setFilter('TVSeries')}>
                    Serie TV ({typeCounts.TVSeries})
                </button>
            </div>

            {/* Griglia delle card delle opere */}
            <div className="cards-grid">
                {filtered.length === 0 ? (
                    <div className="empty-state">Nessuna opera trovata</div>
                ) : (
                    filtered.map(work => (
                        <div
                            key={work.uri}
                            className="work-card"
                            onClick={() =>
                                navigate(`/entity?uri=${encodeURIComponent(work.uri)}`)
                            }
                        >
                            <h3 className="work-title">{work.title}</h3>
                            <span className="work-type">{work.type}</span>

                            {/* Info aggiuntive: anno, durata, pagine */}
                            <div className="work-info">
                                {work.year && <p><strong>Anno:</strong> {work.year}</p>}
                                {work.runtime && <p><strong>Durata:</strong> {work.runtime} min</p>}
                                {work.pages && <p><strong>Pagine:</strong> {work.pages}</p>}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}