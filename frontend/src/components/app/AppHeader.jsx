// Header section for specific tab

import AppHeaderPreview from './AppHeaderPreview';
import { APP_FUNCTIONAL_DESCRIPTION, HEADER_PROOF_POINTS } from '../../appContent';

export default function AppHeader({ activeTab, activeTabLabel, onHome }) {
  return (
    <header className="app-header">
      <div className="app-header-inner">
        <div className="app-header-copy">
          <button className="app-home-button" onClick={onHome} title="Home">Home</button>
          <h1 className="app-header-title">Fantasy Football Analysis</h1>
          <p className="app-header-tagline">{APP_FUNCTIONAL_DESCRIPTION}</p>
          <ul className="app-header-proof-list">{HEADER_PROOF_POINTS.map((point) => (<li key={point}>{point}</li>))}</ul>
        </div>
        <AppHeaderPreview activeTab={activeTab} activeTabLabel={activeTabLabel} />
      </div>
    </header>
  );
}
