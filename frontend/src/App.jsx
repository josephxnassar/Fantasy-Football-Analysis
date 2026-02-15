import { useState } from 'react';
import './App.css';
import Statistics from './components/Statistics';
import Schedules from './components/Schedules';
import DepthCharts from './components/DepthCharts';

function App() {
  const [activeTab, setActiveTab] = useState('statistics');

  const renderTab = () => {
    switch (activeTab) {
      case 'statistics': return <Statistics />;
      case 'schedules': return <Schedules />;
      case 'depth-charts': return <DepthCharts />;
      default: return <Statistics />;
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Fantasy Football Analysis</h1>
        <p>Your one-stop hub for smarter fantasy decisions</p>
      </header>

      <nav className="app-nav">
        <div className="nav-container">
          <button
            className={`nav-button ${activeTab === 'statistics' ? 'active' : ''}`}
            onClick={() => setActiveTab('statistics')}
          >
            Statistics
          </button>
          <button
            className={`nav-button ${activeTab === 'schedules' ? 'active' : ''}`}
            onClick={() => setActiveTab('schedules')}
          >
            Schedules
          </button>
          <button
            className={`nav-button ${activeTab === 'depth-charts' ? 'active' : ''}`}
            onClick={() => setActiveTab('depth-charts')}
          >
            Depth Charts
          </button>
        </div>
      </nav>

      <main>
        {renderTab()}
      </main>
    </div>
  );
}

export default App;
