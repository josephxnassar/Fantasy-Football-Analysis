import React from 'react';
import { getStatDefinition, isKeyStat, groupStatsByCategory } from '../statDefinitions';
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
                <h3>Statistics</h3>
                {(() => {
                  const groupedStats = groupStatsByCategory(playerDetails.stats);
                  return Object.entries(groupedStats).map(([category, stats]) => (
                    <div key={category} className="stat-category">
                      <h4 className="category-title">{category}</h4>
                      <div className="stats-grid">
                        {Object.entries(stats).map(([key, value]) => (
                          <div 
                            key={key} 
                            className={`stat-item ${isKeyStat(key, playerDetails.position) ? 'key-stat' : ''}`}
                            title={getStatDefinition(key)}
                          >
                            <span className="stat-label">{key}</span>
                            <span className="stat-value">
                              {typeof value === 'number' 
                                ? (Number.isInteger(value) ? value : value.toFixed(2))
                                : value}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ));
                })()}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
