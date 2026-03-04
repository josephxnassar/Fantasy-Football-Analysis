import { Suspense, lazy, useState } from 'react';
import { LoadingMessage, SubTabNav } from './common';
import './Statistics.css';

const PlayerSearch = lazy(() => import('./PlayerSearch'));
const Charts = lazy(() => import('./Charts'));
const Rankings = lazy(() => import('./Rankings'));

const TABS = [
  { id: 'rankings', label: 'Rankings' },
  { id: 'charts', label: 'Charts' },
  { id: 'search', label: 'Player Search' },
];

const TAB_COMPONENTS = {
  charts: Charts,
  rankings: Rankings,
  search: PlayerSearch,
};

function Statistics({ onPlayerClick }) {
  const [activeSubTab, setActiveSubTab] = useState('rankings');
  const ActiveSubTab = TAB_COMPONENTS[activeSubTab] || Rankings;

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
