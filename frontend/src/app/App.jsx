import { Suspense, lazy, useState } from 'react';
import './App.css';
import './shell/Shell.css';
import AppHeader from './shell/AppHeader';
import TabErrorFallback from './shell/TabErrorFallback';
import { ErrorBoundary, LoadingMessage } from '../shared/ui';
import HomePage from '../features/home/HomePage';
import PlayerDetailsModal from '../features/statistics/player-details/PlayerDetailsModal';
import { usePlayerDetails } from '../features/statistics/player-details/usePlayerDetails';

const Statistics = lazy(() => import('../features/statistics/Statistics'));
const Schedules = lazy(() => import('../features/teams/Schedules'));
const DepthCharts = lazy(() => import('../features/teams/DepthCharts'));

const DEFAULT_TAB = 'statistics';
const TAB_COMPONENTS = {
  statistics: Statistics,
  schedules: Schedules,
  'depth-charts': DepthCharts,
};
const NAV_TABS = [
  { id: 'statistics', label: 'Statistics' },
  { id: 'schedules', label: 'Schedules' },
  { id: 'depth-charts', label: 'Depth Charts' },
];

function App() {
  const [activeTab, setActiveTab] = useState(null);
  const {
    playerDetails,
    loadingDetails,
    detailsError,
    availableSeasons,
    currentSeason,
    handlePlayerClick,
    handlePlayerSeasonClick,
    handleSeasonChange,
    closeDetails,
  } = usePlayerDetails();
  const ActiveTabComponent = TAB_COMPONENTS[activeTab] || Statistics;
  const defaultTabLabel = NAV_TABS.find((tab) => tab.id === DEFAULT_TAB)?.label || 'Statistics';
  const activeTabLabel = NAV_TABS.find((tab) => tab.id === activeTab)?.label || defaultTabLabel;
  const playerModal = (
    <PlayerDetailsModal
      playerDetails={playerDetails}
      loading={loadingDetails}
      error={detailsError}
      onClose={closeDetails}
      availableSeasons={availableSeasons}
      currentSeason={currentSeason}
      onSeasonChange={handleSeasonChange}
    />
  );
  const goHome = () => setActiveTab(null);

  if (!activeTab)
    return (
      <>
        <HomePage onNavigate={setActiveTab} onPlayerClick={handlePlayerClick} />
        {playerModal}
      </>
    );

  return (
    <div className="App">
      <AppHeader activeTab={activeTab} activeTabLabel={activeTabLabel} onHome={goHome} />

      <nav className="app-nav">
        <div className="nav-container">
          {NAV_TABS.map(({ id, label }) => (
            <button key={id} className={`nav-button ${activeTab === id ? 'active' : ''}`} onClick={() => setActiveTab(id)}>
              {label}
            </button>
          ))}
        </div>
      </nav>

      <main>
        <ErrorBoundary
          resetKey={activeTab}
          onReset={() => setActiveTab(DEFAULT_TAB)}
          fallbackRender={({ resetErrorBoundary }) => (
            <TabErrorFallback
              onGoToDefault={() => {
                setActiveTab(DEFAULT_TAB);
                resetErrorBoundary();
              }}
              onRetry={resetErrorBoundary}
            />
          )}
        >
          <Suspense fallback={<LoadingMessage message="Loading section..." />}>
            <ActiveTabComponent onPlayerClick={handlePlayerClick} onPlayerSeasonClick={handlePlayerSeasonClick} />
          </Suspense>
        </ErrorBoundary>
      </main>

      {playerModal}
    </div>
  );
}

export default App;
