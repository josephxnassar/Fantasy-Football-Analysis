import './StateMessages.css';

export function LoadingMessage({ message = 'Loading...' }) {
  return <div className="state-message state-message--loading">{message}</div>;
}

export function ErrorMessage({ message = 'An error occurred' }) {
  return <div className="state-message state-message--error">Error: {message}</div>;
}

export function EmptyStateMessage({ message = 'No data available' }) {
  return <div className="state-message state-message--empty">{message}</div>;
}
