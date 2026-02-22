import { Suspense, lazy, useState } from 'react';
import { LoadingMessage, SubTabNav } from './common';
import './Statistics.css';

const PlayerSearch = lazy(() => import('./PlayerSearch'));
const Charts = lazy(() => import('./Charts'));

const TABS = [
  { id: 'charts', label: 'Charts' },
  { id: 'search', label: 'Player Search' },
];

function Statistics() {
  const [activeSubTab, setActiveSubTab] = useState('charts');

  // Render the active statistics sub-tab content.
  const renderContent = () => {
    switch (activeSubTab) {
      case 'search': return <PlayerSearch />;
      case 'charts': return <Charts />;
      default: return <Charts />;
    }
  };

  return (
    <div className="statistics-container">
      <SubTabNav tabs={TABS} activeTab={activeSubTab} onTabChange={setActiveSubTab} />

      <div className="statistics-content">
        <Suspense fallback={<LoadingMessage message="Loading statistics..." />}>
          {renderContent()}
        </Suspense>
      </div>
    </div>
  );
}

export default Statistics;
