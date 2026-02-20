import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { getEntityDetails } from '../services/sparqlService';
import '../styles/EntityDetails.css';

/**
 * EntityDetails - Pagina di dettaglio per un'entita (personaggio, luogo, opera, oggetto)
 * Mostra tutte le proprieta e relazioni dell'entita selezionata
 */
export default function EntityDetails() {
    // Recupera l'URI dell'entita dai parametri URL
    const [params] = useSearchParams();
    const uri = params.get('uri');
    const navigate = useNavigate();

    // Stato dell'entita caricata
    const [entity, setEntity] = useState(null);
    // Gestione errori
    const [error, setError] = useState(null);

    // Funzione per caricare i dettagli dell'entita
    const fetchEntity = useCallback(async () => {
        try {
            const data = await getEntityDetails(uri);
            setEntity(data);
            setError(null);
        } catch (e) {
            setError(e.message || 'Errore nel caricamento dei dettagli');
        }
    }, [uri]);

    // Effetto per caricare l'entita (con piccolo delay per evitare race conditions)
    useEffect(() => {
        const id = setTimeout(() => {
            fetchEntity();
        }, 0);
        return () => clearTimeout(id);
    }, [fetchEntity]);

    // Stato di caricamento
    if (!entity && !error) return (
        <div className="loading-state">
            <div className="spinner"></div>
            <p>Caricamento dettagli...</p>
        </div>
    );

    // Stato di errore
    if (error) {
        return (
            <div className="error">
                <h2>Errore</h2>
                <p>{error}</p>
                <p className="error-hint">
                    Assicurati che GraphDB e il proxy server siano attivi
                </p>
                <button className="back-button" onClick={fetchEntity}>Riprova</button>
            </div>
        );
    }

    /**
     * Renderizza una lista di entita correlate come link cliccabili
     * @param {string} title - Titolo della sezione
     * @param {string[]} items - Array di URI delle entita correlate
     */
    const renderList = (title, items) => {
        if (!items || items.length === 0) return null;
        return (
            <div className="section">
                <h3>{title}</h3>
                <ul>
                    {items.map(i => (
                        <li
                            key={i}
                            className="clickable"
                            onClick={() => navigate(`/entity?uri=${encodeURIComponent(i)}`)}
                        >
                            {/* Estrae il nome dall'URI (dopo il #) */}
                            {i.split('#').pop()}
                        </li>
                    ))}
                </ul>
            </div>
        );
    };

    return (
        <>
            {/* Header con bottone indietro */}
            <header className="header">
                <button className="back-button" onClick={() => navigate(-1)}>
                    <span className="back-icon" aria-hidden="true" />
                    <span className="sr-only">Torna indietro</span>
                </button>
            </header>

            <div className="entity-details">
                <h1>{entity.label}</h1>
                
                {/* Badge del tipo di entita con traduzione italiana */}
                {(() => {
                    const typeLabels = {
                        Character: "Personaggio",
                        Location: "Luogo",
                        NarrativeWork: "Opera Narrativa",
                        Object: "Oggetto",
                        Organization: "Organizzazione",
                        School: "Scuola",
                        SafePlace: "Luogo Sicuro",
                        DangerZone: "Zona Pericolosa",
                        LiminalSpace: "Spazio di Confine",
                        Ability: "Abilita",
                        MagicalAbility: "Abilita Magica",
                        HumanCharacter: "Personaggio",
                        NonHumanCharacter: "Non Umano",
                        HybridCharacter: "Ibrido",
                        Book: "Libro",
                        Movie: "Film",
                        TelevisionSeries: "Serie TV"
                    };
                    return (
                        <span className="type">{typeLabels[entity.type] || entity.type}</span>
                    );
                })()}

                {/* Descrizione dell'entita */}
                {entity.description && (
                    <p className="description">{entity.description}</p>
                )}

                {/* Sezioni relazioni: alleati, nemici, mentori, ecc. */}
                {renderList("Alleati", entity.allies)}
                {renderList("Nemici", entity.enemies)}
                {renderList("Mentori", entity.mentors)}
                {renderList("Allievi", entity.students)}
                {renderList("Oggetti posseduti", entity.objects)}
                {renderList("Abilita", entity.abilities)}
                {renderList("Opere", entity.works)}
                {renderList("Organizzazioni", entity.organizations)}
                {renderList("Luoghi ambientazione", entity.locations)}
                {renderList("Prequel", entity.prequels)}
                {renderList("Sequel", entity.sequels)}
                {renderList("Adattamenti", entity.adaptations)}

                {/* Sezioni specifiche per gli oggetti */}
                {entity.type === 'Object' && renderList("Posseduto da", entity.owners)}
                {entity.type === 'Object' && renderList("Abilita conferite", entity.abilities)}

                {/* Attributi speciali degli oggetti (tipo potere, distruttibilita) */}
                {entity.type === 'Object' && (
                    ((entity.powerType && entity.powerType.length > 0) ||
                     (entity.canBeDestroyed === 'true' || entity.canBeDestroyed === 'false')) && (
                        <div className="section">
                            <h3>Attributi</h3>
                            {entity.powerType && (
                                <p>Tipo di potere: {entity.powerType.split('#').pop()}</p>
                            )}
                            {(entity.canBeDestroyed === 'true' || entity.canBeDestroyed === 'false') && (
                                <p>Puo essere distrutto: {entity.canBeDestroyed === 'true' ? 'Si' : 'No'}</p>
                            )}
                        </div>
                    )
                )}

                {/* Funzione narrativa del luogo/personaggio */}
                {entity.narrativeFunction && (
                    <div className="section">
                        <h3>Funzione narrativa</h3>
                        <p>{entity.narrativeFunction}</p>
                    </div>
                )}

                {/* Livello di pericolo per zone pericolose */}
                {entity.dangerLevel && (
                    <div className="section">
                        <h3>Livello di pericolo</h3>
                        <p>{entity.dangerLevel}</p>
                    </div>
                )}
            </div>
        </>
    );
}