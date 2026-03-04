/* Landing page component — composes sub-components into an info hub. */

import PlayerSearch from './PlayerSearch';
import { HeroSection, FeatureCards, AtAGlance, DataSources } from './landing';
import './LandingPage.css';

export default function LandingPage({ onNavigate, onPlayerClick }) {
  return (
    <div className="landing">
      <HeroSection />
      <PlayerSearch
        onPlayerClick={onPlayerClick}
        className="landing-search"
        heading="Quick Player Search"
        maxResults={6}
      />
      <FeatureCards onNavigate={onNavigate} />
      <AtAGlance />
      <DataSources />

      <footer className="landing-footer">
        <p>Built for fantasy analysis — not affiliated with the NFL or any team.</p>
      </footer>
    </div>
  );
}
