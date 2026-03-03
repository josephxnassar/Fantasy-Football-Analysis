/* Landing page component — hero + feature cards entry point. */

import './LandingPage.css';

const FEATURES = [
  {
    id: 'statistics',
    icon: '📊',
    title: 'Player Statistics',
    description:
      'Search any player and dive into season totals, weekly breakdowns, advanced metrics, and position rankings — all color-coded at a glance.',
  },
  {
    id: 'schedules',
    icon: '📅',
    title: 'Team Schedules',
    description:
      'Browse every NFL team\'s full-season schedule by conference and division. Switch seasons to compare past and upcoming matchups.',
  },
  {
    id: 'depth-charts',
    icon: '📋',
    title: 'Depth Charts',
    description:
      'See current positional depth for every roster. Quickly spot starters, backups, and handcuff targets across the league.',
  },
];

export default function LandingPage({ onNavigate }) {
  return (
    <div className="landing">
      <section className="landing-hero">
        <h1 className="landing-title">Fantasy Football Analysis</h1>
        <p className="landing-tagline">
          Your one-stop hub for smarter fantasy decisions
        </p>
      </section>

      <section className="landing-features">
        {FEATURES.map((feature) => (
          <button
            key={feature.id}
            className="feature-card"
            onClick={() => onNavigate(feature.id)}
          >
            <span className="feature-icon">{feature.icon}</span>
            <h2 className="feature-title">{feature.title}</h2>
            <p className="feature-description">{feature.description}</p>
            <span className="feature-cta">Explore →</span>
          </button>
        ))}
      </section>
    </div>
  );
}
