// Navigation cards for the three main app sections.

import './FeatureCards.css';

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

export default function FeatureCards({ onNavigate }) {
  return (
    <section className="landing-section">
      <h2 className="section-heading">Explore</h2>
      <div className="landing-features">
        {FEATURES.map((feature) => (
          <button
            key={feature.id}
            className="feature-card"
            onClick={() => onNavigate(feature.id)}
          >
            <span className="feature-icon">{feature.icon}</span>
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-description">{feature.description}</p>
            <span className="feature-cta">Explore →</span>
          </button>
        ))}
      </div>
    </section>
  );
}
