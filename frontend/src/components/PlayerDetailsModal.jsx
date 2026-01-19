import { useState, useEffect } from 'react';
import { getStatDefinition, isKeyStat, groupStatsByCategory } from '../statDefinitions';
import { formatStatValue } from '../utils/helpers';
import './PlayerDetailsModal.css';

export default function PlayerDetailsModal({ 
  playerDetails, 
  loading, 
  onClose, 
  availableSeasons = [],
  onSeasonChange,
  currentSeason,
  grade = null
}) {
  if (!playerDetails && !loading) return null;

  const rating = playerDetails?.stats?.Rating;

  const renderStatCategories = (details) => {
    const groupedStats = groupStatsByCategory(details.stats, details.position);
    
    return Object.entries(groupedStats).map(([category, stats]) => {
      const filteredStats = Object.entries(stats).filter(([key]) => key !== 'Rating');
      
      if (filteredStats.length === 0 || category === 'Core') return null;
      
      return (
        <div key={category} className="stat-category">
          <h4 className="category-title">{category}</h4>
          <div className="stats-grid">
            {filteredStats.map(([key, value]) => (
              <div 
                key={key} 
                className={`stat-item ${isKeyStat(key, details.position) ? 'key-stat' : ''}`}
                title={getStatDefinition(key)}
              >
                <span className="stat-label">{key}</span>
                <span className="stat-value">{formatStatValue(value)}</span>
              </div>
            ))}
          </div>
        </div>
      );
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        {loading ? (
          <div className="loading">Loading player details...</div>
        ) : (
          <>
            <div className="player-header">
              <h2>{playerDetails.name}</h2>
              {grade && <div className="grade-badge">{grade}</div>}
            </div>
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
                {rating && (
                  <div className="detail-item rating-item">
                    <span className="label">Rating:</span>
                    <span className="value rating-value">{rating.toFixed(2)}</span>
                  </div>
                )}
              </div>

              {/* Year Selector */}
              {availableSeasons.length > 0 && (
                <div className="year-selector">
                  <span className="year-label">View Stats:</span>
                  <div className="year-buttons">
                    <button
                      className={`year-button ${currentSeason === null ? 'active' : ''}`}
                      onClick={() => onSeasonChange(null)}
                    >
                      Average
                    </button>
                    {availableSeasons.map(season => (
                      <button
                        key={season}
                        className={`year-button ${currentSeason === season ? 'active' : ''}`}
                        onClick={() => onSeasonChange(season)}
                      >
                        {season}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="stats-section">
                <h3>Statistics {currentSeason ? `(${currentSeason} Season)` : '(Career Average)'}</h3>
                {renderStatCategories(playerDetails)}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
