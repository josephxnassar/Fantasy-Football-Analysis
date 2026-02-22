import { Suspense, lazy, useState } from 'react';
import './App.css';
import { ErrorBoundary, LoadingMessage } from './components/common';

const Statistics = lazy(() => import('./components/Statistics'));
const Schedules = lazy(() => import('./components/Schedules'));
const DepthCharts = lazy(() => import('./components/DepthCharts'));

function App() {
  const [activeTab, setActiveTab] = useState('statistics');

  // Resolve the currently selected top-level tab to its view component.
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
        <ErrorBoundary
          resetKey={activeTab}
          onReset={() => setActiveTab('statistics')}
          fallbackRender={({ resetErrorBoundary }) => (
            <div className="tab-error-fallback">
              <h2>This section crashed.</h2>
              <p>Try opening another tab or reset this section.</p>
              <div className="tab-error-actions">
                <button
                  className="tab-error-btn secondary"
                  onClick={() => {
                    setActiveTab('statistics');
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
            {renderTab()}
          </Suspense>
        </ErrorBoundary>
      </main>
    </div>
  );
}

export default App;
