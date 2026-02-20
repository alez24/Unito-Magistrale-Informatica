import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import HomePage from './components/HomePage';
import UniverseDashboard from './components/UniverseDashboard';
import EntityDetails from './components/EntityDetails';
import './styles/design-system.css';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<HomeWrapper />} />
                <Route path="/universe" element={<UniverseDashboard />} />
                <Route path="/entity" element={<EntityDetails />} />
            </Routes>
        </Router>
    );
}

function HomeWrapper() {
    const navigate = useNavigate();

    const handleSelectUniverse = (universe) => {
        navigate(`/universe?uri=${encodeURIComponent(universe.uri)}`);
    };

    return <HomePage onSelectUniverse={handleSelectUniverse} />;
}

export default App;
