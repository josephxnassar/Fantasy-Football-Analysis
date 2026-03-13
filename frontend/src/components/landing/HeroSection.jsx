// Hero banner at the top of the landing page.

import './HeroSection.css';
import { APP_FUNCTIONAL_DESCRIPTION, HEADER_PROOF_POINTS } from '../../appContent';

export default function HeroSection() {
  return (
    <section className="landing-hero">
      <div className="landing-hero-inner">
        <div className="landing-hero-copy">
          <h1 className="landing-title">Fantasy Football Analysis</h1>
          <p className="landing-tagline">
            {APP_FUNCTIONAL_DESCRIPTION}
          </p>

          <ul className="landing-proof-list">
            {HEADER_PROOF_POINTS.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>
        </div>

        <aside className="landing-hero-visual" aria-hidden="true">
          <div className="hero-visual-card">
            <p className="hero-visual-label">Coverage Snapshot</p>
            <svg className="hero-visual-graphic" viewBox="0 0 420 230">
              <rect className="hero-field-bg" x="14" y="34" width="392" height="172" rx="14" />
              <line className="hero-field-midline" x1="210" y1="34" x2="210" y2="206" />
              <line className="hero-field-line" x1="70" y1="34" x2="70" y2="206" />
              <line className="hero-field-line" x1="126" y1="34" x2="126" y2="206" />
              <line className="hero-field-line" x1="294" y1="34" x2="294" y2="206" />
              <line className="hero-field-line" x1="350" y1="34" x2="350" y2="206" />

              <polyline className="hero-route-a" points="84,160 138,130 188,142 244,108 304,118" />
              <polyline className="hero-route-b" points="332,76 286,102 246,88 194,112 142,98" />

              <circle className="hero-token-a" cx="86" cy="160" r="9" />
              <circle className="hero-token-b" cx="332" cy="76" r="9" />
              <circle className="hero-token-c" cx="246" cy="108" r="6" />

              <rect className="hero-mini-card" x="264" y="148" width="124" height="46" rx="8" />
              <text className="hero-mini-label" x="276" y="167">Weekly + Season</text>
              <text className="hero-mini-value" x="276" y="184">Split Ready</text>
            </svg>

            <div className="hero-visual-footer">
              <span>Player Stats</span>
              <span>Schedules</span>
              <span>Depth Charts</span>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
