import './DepthChartTable.css';

function DepthChartTable({ entries, variant = 'full', highlightName = null, onPlayerClick }) {
  const tableClass = variant === 'mini' ? 'depth-chart-mini-table' : 'depth-chart-table';

  const cellClass = (name, extra = '') => {
    const classes = ['player-cell'];
    if (extra) classes.push(extra);
    if (!name) classes.push('empty');
    if (highlightName && name === highlightName) classes.push('highlight');
    return classes.join(' ');
  };
  const renderPlayerName = (name) => {
    if (!name) return '—';
    if (!onPlayerClick) return name;
    else
      return (
        <button type="button" className="depth-chart-player-link" onClick={() => onPlayerClick(name)}>
          {name}
        </button>
      );
  };

  return (
    <table className={tableClass}>
      <thead>
        <tr>
          <th>POS</th>
          <th>Starter</th>
          <th>2nd</th>
          <th>3rd</th>
          <th>4th</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((entry, idx) => (
          <tr key={`${entry.position}-${idx}`}>
            <td className="position-cell">{entry.position}</td>
            <td className={cellClass(entry.starter, 'starter')}>{renderPlayerName(entry.starter)}</td>
            <td className={cellClass(entry.second)}>{renderPlayerName(entry.second)}</td>
            <td className={cellClass(entry.third)}>{renderPlayerName(entry.third)}</td>
            <td className={cellClass(entry.fourth)}>{renderPlayerName(entry.fourth)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default DepthChartTable;
