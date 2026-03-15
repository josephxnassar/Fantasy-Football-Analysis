// Aims to stop UI crash from crashing whole app.

import React from 'react';
import './ErrorBoundary.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    // Local error state controls fallback rendering for this subtree only.
    this.state = { hasError: false, error: null };
    this.handleReset = this.handleReset.bind(this);
  }

  // Called when child throws during render. Returns new state.
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  // Runs after error is caught.
  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  // Runs after updates. Clears the error state.
  componentDidUpdate(prevProps) {
    if (this.state.hasError && prevProps.resetKey !== this.props.resetKey)
      this.setState({ hasError: false, error: null });
  }

  // Manually clears error state.
  handleReset() {
    this.setState({ hasError: false, error: null });
    if (typeof this.props.onReset === 'function')
      this.props.onReset();
  }

  // If there's an error w/ fallBackRender, show custom fallback UI. If error with no fallBackRender, show built-in fallback UI. If no error, show normal content.
  render() {
    if (this.state.hasError) {
      if (typeof this.props.fallbackRender === 'function')
        return this.props.fallbackRender({error: this.state.error, resetErrorBoundary: this.handleReset});
      else
        return (
          <div className="error-boundary">
            <h2 className="error-boundary-title">Something went wrong.</h2>
            <p className="error-boundary-message">Try refreshing the page or reset this section.</p>
            <button className="error-boundary-button" onClick={this.handleReset}>Reset</button>
          </div>
        );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
