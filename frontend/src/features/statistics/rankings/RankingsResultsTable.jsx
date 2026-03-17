export default function RankingsResultsTable({rankedPlayers, selectedSeason, onPlayerClick, onPlayerSeasonClick}) {
  const handlePlayerResultClick = (playerName) => {
    const seasonNumber = Number(selectedSeason);
    if (onPlayerSeasonClick && Number.isFinite(seasonNumber)) {
      onPlayerSeasonClick(playerName, seasonNumber);
      return;
    }
    onPlayerClick?.(playerName);
  };

  return (
    <div className="rankings-panel rankings-panel--results">
      <h2>Results</h2>
      {rankedPlayers.length === 0 ? (<p className="rankings-empty">No players qualify for the current settings.</p>) : (
        <div className="rankings-table-wrapper">
          <table className="rankings-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Team</th>
                <th>Pos</th>
                <th>Age</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {rankedPlayers.map((player) => {
                const scoreValue = player.score * 100;
                return (
                  <tr key={`${player.name}-${player.rank}`}>
                    <td>{player.rank}</td>
                    <td>
                      <button type="button" className="ranking-player-button" onClick={() => handlePlayerResultClick(player.name)}>{player.name}</button>
                    </td>
                    <td>{player.team || '-'}</td>
                    <td>{player.position || '-'}</td>
                    <td>{player.age ?? '-'}</td>
                    <td className={scoreValue >= 0 ? 'score-positive' : 'score-negative'}>
                      {scoreValue > 0 ? '+' : ''}
                      {scoreValue.toFixed(1)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
