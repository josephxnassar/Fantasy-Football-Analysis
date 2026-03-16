import PlayerSearch from '../player-search/PlayerSearch';
import AtAGlance from './AtAGlance';
import DataSources from './DataSources';
import FeatureCards from './FeatureCards';
import HeroSection from './HeroSection';
import './LandingPage.css';

export default function LandingPage({ onNavigate, onPlayerClick }) {
  return (
    <div className="landing">
      <HeroSection />
      <PlayerSearch onPlayerClick={onPlayerClick} heading="Quick Player Search" maxResults={6} variant="landing"/>
      <FeatureCards onNavigate={onNavigate} />
      <AtAGlance />
      <DataSources />
      <footer className="landing-footer">
        <p>Built for fantasy analysis — not affiliated with the NFL or any team.</p>
      </footer>
    </div>
  );
}
