import React from 'react';
import { getStatDefinition } from '../statDefinitions';
import './PlayerDetailsModal.css';

export default function PlayerDetailsModal({ playerDetails, loading, onClose }) {
  if (!playerDetails && !loading) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        {loading ? (
          <div className="loading">Loading player details...</div>
        ) : (
          <>
            <h2>{playerDetails.name}</h2>
            <div className="player-details">
              <div className="details-grid">
                <div className="detail-item">
                  <span className="label">Position:</span>
                  <span className="value">{playerDetails.position}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Team:</span>
                  <span className="value">{playerDetails.team || 'N/A'}</span>
                </div>
              </div>

              <div className="stats-section">
                <h3>Stats</h3>
                <div className="stats-grid">
                  {Object.entries(playerDetails.stats).map(([key, value]) => (
                    <div key={key} className="stat-item" title={getStatDefinition(key)}>
                      <span className="stat-label">{key}:</span>
                      <span className="stat-value">
                        {typeof value === 'number' ? value.toFixed(2) : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
