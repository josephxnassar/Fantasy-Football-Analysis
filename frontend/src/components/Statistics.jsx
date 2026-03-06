import { Suspense, lazy, useState } from 'react';
import { LoadingMessage, SubTabNav } from './common';
import './Statistics.css';

const PlayerSearch = lazy(() => import('./PlayerSearch'));
const Charts = lazy(() => import('./Charts'));
const Rankings = lazy(() => import('./Rankings'));
const PlayerComparison = lazy(() => import('./PlayerComparison'));

const TABS = [
  { id: 'charts', label: 'Charts' },
  { id: 'rankings', label: 'Rankings' },
  { id: 'comparison', label: 'Player Comparison' },
  { id: 'search', label: 'Player Search' },
];

const TAB_COMPONENTS = {
  charts: Charts,
  comparison: PlayerComparison,
  rankings: Rankings,
  search: PlayerSearch,
};

function Statistics({ onPlayerClick, onPlayerSeasonClick }) {
  const [activeSubTab, setActiveSubTab] = useState('charts');
  const ActiveSubTab = TAB_COMPONENTS[activeSubTab] || Rankings;

  return (
    <div className="statistics-container">
      <div className="statistics-header">
        <SubTabNav
          tabs={TABS}
          activeTab={activeSubTab}
          onTabChange={setActiveSubTab}
          variant="statistics"
        />
      </div>

      <div className="statistics-content">
        <Suspense fallback={<LoadingMessage message="Loading statistics..." />}>
          <ActiveSubTab onPlayerClick={onPlayerClick} onPlayerSeasonClick={onPlayerSeasonClick} />
        </Suspense>
      </div>
    </div>
  );
}

export default Statistics;
