export default function PlayerRatings({
  rating,
  dynastyRating,
  position,
  posRankRedraft,
  posRankDynasty,
  overallRankRedraft,
  overallRankDynasty,
  isEligible = true,
}) {
  if (!isEligible) {
    return (
      <div className="ratings-section">
        <h3>Player Ratings</h3>
        <div className="ratings-grid">
          <div className="rating-card">
            <div className="rating-label">Status</div>
            <div className="rating-value">Retired/Inactive</div>
          </div>
        </div>
      </div>
    );
  }

  if (!rating && !dynastyRating) return null;

  return (
    <div className="ratings-section">
      <h3>Player Ratings</h3>
      <div className="ratings-grid">
        {rating && (
          <div className="rating-card">
            <div className="rating-label">Redraft Rating</div>
            <div className="rating-value">{rating.toFixed(2)}</div>
            {posRankRedraft && overallRankRedraft && (
              <div className="percentile-info">
                <div>Position: #{posRankRedraft} in {position}s</div>
                <div>Overall: #{overallRankRedraft} overall</div>
              </div>
            )}
          </div>
        )}
        {dynastyRating && (
          <div className="rating-card">
            <div className="rating-label">Dynasty Rating</div>
            <div className="rating-value">{dynastyRating.toFixed(2)}</div>
            {posRankDynasty && overallRankDynasty && (
              <div className="percentile-info">
                <div>Position: #{posRankDynasty} in {position}s</div>
                <div>Overall: #{overallRankDynasty} overall</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
