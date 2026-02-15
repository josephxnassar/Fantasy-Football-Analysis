import { useState } from 'react';
import Rankings from './Rankings';
import PlayerSearch from './PlayerSearch';
import Charts from './Charts';
import { SubTabNav } from './common';
import './Statistics.css';

const TABS = [
  { id: 'rankings', label: 'Rankings' },
  { id: 'charts', label: 'Charts' },
  { id: 'search', label: 'Player Search' },
];

function Statistics() {
  const [activeSubTab, setActiveSubTab] = useState('rankings');

  const renderContent = () => {
    switch (activeSubTab) {
      case 'rankings': return <Rankings />;
      case 'search': return <PlayerSearch />;
      case 'charts': return <Charts />;
      default: return <Rankings />;
    }
  };

  return (
    <div className="statistics-container">
      <SubTabNav tabs={TABS} activeTab={activeSubTab} onTabChange={setActiveSubTab} />

      <div className="statistics-content">
        {renderContent()}
      </div>
    </div>
  );
}

export default Statistics;
