/**
 * File overview: Application entry point that mounts the React app into the browser root.
 */

import { StrictMode } from 'react';
import ReactDOM from 'react-dom/client';
import App from './app/App.jsx';
import { ErrorBoundary } from './shared/ui';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary onReset={() => window.location.reload()}>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);
