import { Suspense, lazy, useState } from 'react';
import './App.css';
import AppHeaderPreview from './components/AppHeaderPreview';
import { ErrorBoundary, LoadingMessage } from './components/common';
import LandingPage from './components/LandingPage';
import PlayerDetailsModal from './components/PlayerDetailsModal';
import { usePlayerDetails } from './hooks/usePlayerDetails';
import { APP_FUNCTIONAL_DESCRIPTION, HEADER_PROOF_POINTS, NAV_TABS } from './utils/appContent';

const Statistics = lazy(() => import('./components/Statistics'));
const Schedules = lazy(() => import('./components/Schedules'));
const DepthCharts = lazy(() => import('./components/DepthCharts'));

const DEFAULT_TAB = 'statistics';
const TAB_COMPONENTS = {
  statistics: Statistics,
  schedules: Schedules,
  'depth-charts': DepthCharts,
};

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
  const activeTabLabel = NAV_TABS.find((tab) => tab.id === activeTab)?.label || 'Statistics';
  const showPlayerModal = playerDetails || loadingDetails || detailsError;
  const playerModal = showPlayerModal ? (
    <PlayerDetailsModal
      playerDetails={playerDetails}
      loading={loadingDetails}
      error={detailsError}
      onClose={closeDetails}
      availableSeasons={availableSeasons}
      currentSeason={currentSeason}
      onSeasonChange={handleSeasonChange}
    />
  ) : null;
  const goHome = () => setActiveTab(null);

  if (!activeTab) {
    return (
      <>
        <LandingPage onNavigate={setActiveTab} onPlayerClick={handlePlayerClick} />
        {playerModal}
      </>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="app-header-inner">
          <div className="app-header-copy">
            <button
              className="app-home-button"
              onClick={goHome}
              title="Home"
            >
              Home
            </button>

            <h1
              className="app-header-title"
              onClick={goHome}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && goHome()}
            >
              Fantasy Football Analysis
            </h1>
            <p className="app-header-tagline">
              {APP_FUNCTIONAL_DESCRIPTION}
            </p>

            <ul className="app-header-proof-list">
              {HEADER_PROOF_POINTS.map((point) => (
                <li key={point}>{point}</li>
              ))}
            </ul>
          </div>

          <AppHeaderPreview activeTab={activeTab} activeTabLabel={activeTabLabel} />
        </div>
      </header>

      <nav className="app-nav">
        <div className="nav-container">
          {NAV_TABS.map(({ id, label }) => (
            <button
              key={id}
              className={`nav-button ${activeTab === id ? 'active' : ''}`}
              onClick={() => setActiveTab(id)}
            >
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
            <div className="tab-error-fallback">
              <h2>This section crashed.</h2>
              <p>Try opening another tab or reset this section.</p>
              <div className="tab-error-actions">
                <button
                  className="tab-error-btn secondary"
                  onClick={() => {
                    setActiveTab(DEFAULT_TAB);
                    resetErrorBoundary();
                  }}
                >
                  Go To Statistics
                </button>
                <button
                  className="tab-error-btn primary"
                  onClick={resetErrorBoundary}
                >
                  Retry Tab
                </button>
              </div>
            </div>
          )}
        >
          <Suspense fallback={<LoadingMessage message="Loading section..." />}>
            <ActiveTabComponent
              onPlayerClick={handlePlayerClick}
              onPlayerSeasonClick={handlePlayerSeasonClick}
            />
          </Suspense>
        </ErrorBoundary>
      </main>

      {playerModal}
    </div>
  );
}

export default App;
