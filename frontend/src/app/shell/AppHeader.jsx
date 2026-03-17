// Header section for specific tab

import '../brand/brand.css';
import AppHeaderPreview from './AppHeaderPreview';
import { APP_FUNCTIONAL_DESCRIPTION, HEADER_PROOF_POINTS } from '../brand/content';

export default function AppHeader({ activeTab, activeTabLabel, onHome }) {
  return (
    <header className="brand-hero brand-hero--shell">
      <div className="brand-hero-inner">
        <div className="brand-hero-copy">
          <button className="app-home-button" onClick={onHome} title="Home">Home</button>
          <h1 className="brand-title">Fantasy Football Analysis</h1>
          <p className="brand-tagline">{APP_FUNCTIONAL_DESCRIPTION}</p>
          <ul className="brand-proof-list">{HEADER_PROOF_POINTS.map((point) => (<li key={point}>{point}</li>))}</ul>
        </div>
        <AppHeaderPreview activeTab={activeTab} activeTabLabel={activeTabLabel}/>
      </div>
    </header>
  );
}
