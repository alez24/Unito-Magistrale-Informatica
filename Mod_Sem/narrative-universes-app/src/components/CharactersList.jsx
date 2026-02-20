import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCharactersByUniverse } from '../services/sparqlService';
import '../styles/CharactersList.css';

/**
 * CharactersList - Lista dei personaggi di un universo narrativo
 * Mostra i personaggi con filtri per ruolo (Protagonista, Alleato, Antagonista, Mentore)
 */
export default function CharactersList({ universeUri }) {
    // Stato per i personaggi caricati
    const [characters, setCharacters] = useState([]);
    // Stato di caricamento
    const [loading, setLoading] = useState(true);
    // Filtro attivo (all, Protagonista, Alleato, Antagonista, Mentore)
    const [filter, setFilter] = useState('all');

    const navigate = useNavigate();

    /**
     * Pulisce e traduce i ruoli dei personaggi
     * Rimuove i tipi generici e traduce in italiano
     */
    function cleanRoles(types) {
        // Tipi da escludere dalla visualizzazione
        const blacklist = ["Character", "HUMANCHARACTER", "HumanCharacter"];
        // Mapping tipo -> etichetta italiana
        const rename = {
            Protagonist: "Protagonista",
            Alleato: "Alleato",
            Antagonist: "Antagonista",
            Mentor: "Mentore",
            NonHumanCharacter: "Non Umano",
            NONHUMANCHARACTER: "Non Umano",
            HybridCharacter: "Ibrido"
        };

        return types
            .filter(t => !blacklist.includes(t))
            .map(t => rename[t] || t);
    }

    // Carica i personaggi al mount o al cambio di universo
    useEffect(() => {
        async function loadCharacters() {
            try {
                const data = await getCharactersByUniverse(universeUri);
                const raw = data.results.bindings;

                // Raggruppa per URI (un personaggio puo avere piu tipi)
                const grouped = {};

                raw.forEach(b => {
                    const uri = b.character.value;

                    if (!grouped[uri]) {
                        grouped[uri] = {
                            uri,
                            name: b.name.value,
                            description: b.description?.value || "",
                            types: new Set()
                        };
                    }

                    // Estrai il ruolo dall'URI (dopo il #)
                    const role = b.type?.value?.split('#').pop() || "Character";
                    grouped[uri].types.add(role);
                });

                // Converte in array e pulisce i ruoli
                const finalCharacters = Object.values(grouped).map(c => ({
                    ...c,
                    types: cleanRoles(Array.from(c.types))
                }));

                setCharacters(finalCharacters);
            } catch (error) {
                console.error('Error loading characters:', error);
            } finally {
                setLoading(false);
            }
        }

        loadCharacters();
    }, [universeUri]);

    // Stato di caricamento
    if (loading) {
        return (
            <div className="loading-state">
                <div className="spinner"></div>
                <p>Caricamento personaggi...</p>
            </div>
        );
    }

    // Applica il filtro selezionato
    const filteredCharacters =
        filter === 'all'
            ? characters
            : characters.filter(c => c.types.includes(filter));

    // Conteggi per i bottoni filtro
    const typeCounts = {
        all: characters.length,
        Protagonista: characters.filter(c => c.types.includes('Protagonista')).length,
        Alleato: characters.filter(c => c.types.includes('Alleato')).length,
        Antagonista: characters.filter(c => c.types.includes('Antagonista')).length,
        Mentore: characters.filter(c => c.types.includes('Mentore')).length
    };

    return (
        <div className="characters-list">
            {/* Bottoni filtro per ruolo narrativo */}
            <div className="filters">
                <button
                    className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                    onClick={() => setFilter('all')}
                >
                    Tutti ({typeCounts.all})
                </button>

                {typeCounts.Protagonista > 0 && (
                    <button
                        className={`filter-btn ${filter === 'Protagonista' ? 'active' : ''}`}
                        onClick={() => setFilter('Protagonista')}
                    >
                        Protagonisti ({typeCounts.Protagonista})
                    </button>
                )}

                {typeCounts.Alleato > 0 && (
                    <button
                        className={`filter-btn ${filter === 'Alleato' ? 'active' : ''}`}
                        onClick={() => setFilter('Alleato')}
                    >
                        Alleati ({typeCounts.Alleato})
                    </button>
                )}

                {typeCounts.Antagonista > 0 && (
                    <button
                        className={`filter-btn ${filter === 'Antagonista' ? 'active' : ''}`}
                        onClick={() => setFilter('Antagonista')}
                    >
                        Antagonisti ({typeCounts.Antagonista})
                    </button>
                )}

                {typeCounts.Mentore > 0 && (
                    <button
                        className={`filter-btn ${filter === 'Mentore' ? 'active' : ''}`}
                        onClick={() => setFilter('Mentore')}
                    >
                        Mentori ({typeCounts.Mentore})
                    </button>
                )}
            </div>

            {/* Griglia delle card dei personaggi */}
            <div className="cards-grid">
                {filteredCharacters.length === 0 ? (
                    <div className="empty-state">
                        <p>Nessun personaggio trovato</p>
                    </div>
                ) : (
                    filteredCharacters.map(character => (
                        <div
                            key={character.uri}
                            className="character-card"
                            onClick={() =>
                                navigate(`/entity?uri=${encodeURIComponent(character.uri)}`)
                            }
                        >
                            <div className="character-header">
                                <h3 className="character-name">{character.name}</h3>

                                {/* Tag dei ruoli del personaggio */}
                                <div className="character-tags">
                                    {character.types.map(role => (
                                        <span key={role} className="tag">{role}</span>
                                    ))}
                                </div>
                            </div>

                            {/* Descrizione del personaggio se presente */}
                            {character.description && (
                                <p className="character-description">{character.description}</p>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
