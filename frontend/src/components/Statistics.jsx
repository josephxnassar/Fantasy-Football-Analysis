import { Suspense, lazy, useState } from 'react';
import { LoadingMessage, SubTabNav } from './common';
import './Statistics.css';

const PlayerSearch = lazy(() => import('./PlayerSearch'));
const Charts = lazy(() => import('./Charts'));

const TABS = [
  { id: 'charts', label: 'Charts' },
  { id: 'search', label: 'Player Search' },
];

function Statistics({ onPlayerClick }) {
  const [activeSubTab, setActiveSubTab] = useState('charts');
  const ActiveSubTab = activeSubTab === 'search' ? PlayerSearch : Charts;

  return (
    <div className="statistics-container">
      <div className="statistics-header">
        <SubTabNav tabs={TABS} activeTab={activeSubTab} onTabChange={setActiveSubTab} />
      </div>

      <div className="statistics-content">
        <Suspense fallback={<LoadingMessage message="Loading statistics..." />}>
          <ActiveSubTab onPlayerClick={onPlayerClick} />
        </Suspense>
      </div>
    </div>
  );
}

export default Statistics;
