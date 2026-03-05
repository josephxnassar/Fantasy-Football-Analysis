/* Shared depth chart table component used by both DepthChartModal and PlayerDetailsModal. Renders a POS / Starter / 2nd / 3rd / 4th table with optional player highlighting. */

import './DepthChartTable.css';

function DepthChartTable({ entries, variant = 'full', highlightName = null }) {
  const tableClass = variant === 'mini' ? 'depth-chart-mini-table' : 'depth-chart-table';

  // Build consistent cell class list for state styling (starter/empty/highlight).
  const cellClass = (name, extra = '') => {
    const classes = ['player-cell'];
    if (extra) classes.push(extra);
    if (!name) classes.push('empty');
    if (highlightName && name === highlightName) classes.push('highlight');
    return classes.join(' ');
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
            <td className={cellClass(entry.starter, 'starter')}>{entry.starter || '—'}</td>
            <td className={cellClass(entry.second)}>{entry.second || '—'}</td>
            <td className={cellClass(entry.third)}>{entry.third || '—'}</td>
            <td className={cellClass(entry.fourth)}>{entry.fourth || '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default DepthChartTable;
