/* Reusable error and loading state messages */

export function LoadingMessage({ message = 'Loading...' }) {
  return <div className="loading">{message}</div>;
}

export function ErrorMessage({ message = 'An error occurred' }) {
  return <div className="error">Error: {message}</div>;
}

export function EmptyStateMessage({ message = 'No data available' }) {
  return <div className="empty-state">{message}</div>;
}
