import React, { useState } from 'react';
import './App.css';
import Rankings from './components/Rankings';
import PlayerSearch from './components/PlayerSearch';

function App() {
  const [activeTab, setActiveTab] = useState('rankings');

  return (
    <div className="App">
      <header className="app-header">
        <h1>Fantasy Football Analysis</h1>
        <p>Your one-stop hub for smarter fantasy decisions</p>
      </header>

      <nav className="app-nav">
        <div className="nav-container">
          <button
            className={`nav-button ${activeTab === 'rankings' ? 'active' : ''}`}
            onClick={() => setActiveTab('rankings')}
          >
            Rankings
          </button>
          <button
            className={`nav-button ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            Player Search
          </button>
        </div>
      </nav>

      <main>
        {activeTab === 'rankings' ? <Rankings /> : <PlayerSearch />}
      </main>
    </div>
  );
}

export default App;
