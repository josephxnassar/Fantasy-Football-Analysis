export default function TabErrorFallback({ onGoToDefault, onRetry }) {
  return (
    <div className="tab-error-fallback">
      <h2>This section crashed.</h2>
      <p>Try opening another tab or reset this section.</p>
      <div className="tab-error-actions">
        <button
          className="tab-error-btn secondary"
          onClick={onGoToDefault}
        >
          Go To Statistics
        </button>
        <button
          className="tab-error-btn primary"
          onClick={onRetry}
        >
          Retry Tab
        </button>
      </div>
    </div>
  );
}
