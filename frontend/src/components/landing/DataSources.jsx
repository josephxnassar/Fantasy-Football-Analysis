/* Attribution links for the data sources powering the app */

import './DataSources.css';

const DATA_SOURCES = [
  { name: 'Pro Football Reference', url: 'https://www.pro-football-reference.com/', description: 'Advanced passing, rushing, and receiving metrics plus snap counts' },
  { name: 'Next Gen Stats', url: 'https://nextgenstats.nfl.com/', description: 'Tracking-based metrics — completion probability, separation, rush yards before contact' },
];

export default function DataSources() {
  return (
    <section className="landing-section">
      <h2 className="section-heading">Data Sources</h2>
      <p className="section-subtitle">
        Player stats, rosters, and opportunity data sourced from the{' '}
        <a href="https://github.com/nflverse" target="_blank" rel="noopener noreferrer">
          nflverse
        </a>
        {' '}project via{' '}
        <a href="https://github.com/nflverse/nfl_data_py" target="_blank" rel="noopener noreferrer">
          nflreadpy
        </a>
      </p>
      <div className="landing-sources-grid">
        {DATA_SOURCES.map((src) => (
          <div key={src.name} className="source-card">
            <a href={src.url} target="_blank" rel="noopener noreferrer" className="source-name">
              {src.name}
            </a>
            <p className="source-desc">{src.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
