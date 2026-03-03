/* Landing page component — composes sub-components into an info hub. */

import { usePlayerDetails } from '../hooks/usePlayerDetails';
import PlayerDetailsModal from './PlayerDetailsModal';
import { HeroSection, QuickSearch, FeatureCards, AtAGlance, DataSources } from './landing';
import './LandingPage.css';

export default function LandingPage({ onNavigate }) {
  const {
    playerDetails,
    loadingDetails,
    availableSeasons,
    currentSeason,
    handlePlayerClick,
    handleSeasonChange,
    closeDetails,
  } = usePlayerDetails();

  return (
    <div className="landing">
      <HeroSection />
      <QuickSearch onPlayerClick={handlePlayerClick} />
      <FeatureCards onNavigate={onNavigate} />
      <AtAGlance />
      <DataSources />

      <footer className="landing-footer">
        <p>Built for fantasy analysis — not affiliated with the NFL or any team.</p>
      </footer>

      {(playerDetails || loadingDetails) && (
        <PlayerDetailsModal
          playerDetails={playerDetails}
          loading={loadingDetails}
          onClose={closeDetails}
          availableSeasons={availableSeasons}
          currentSeason={currentSeason}
          onSeasonChange={handleSeasonChange}
        />
      )}
    </div>
  );
}
