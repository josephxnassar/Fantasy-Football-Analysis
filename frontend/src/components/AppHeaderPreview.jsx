/* Static section previews shown in the main app header. */

export default function AppHeaderPreview({ activeTab, activeTabLabel }) {
  return (
    <aside className="app-header-panel" aria-hidden="true">
      <p className="app-header-panel-kicker">{activeTabLabel} Preview</p>

      {activeTab === 'schedules' ? (
        <div className="app-preview app-preview--schedule">
          <div className="app-preview-schedule-grid">
            <div className="app-preview-schedule-item">
              <span className="week">Wk 8</span>
              <span className="opp away">@ KC</span>
            </div>
            <div className="app-preview-schedule-item">
              <span className="week">Wk 9</span>
              <span className="opp home">vs BUF</span>
            </div>
            <div className="app-preview-schedule-item">
              <span className="week">Wk 10</span>
              <span className="opp away">@ DEN</span>
            </div>
            <div className="app-preview-schedule-item">
              <span className="week">Wk 11</span>
              <span className="opp home">vs MIA</span>
            </div>
          </div>
        </div>
      ) : null}

      {activeTab === 'depth-charts' ? (
        <div className="app-preview app-preview--depth">
          <div className="app-preview-depth-header">
            <span>Pos</span>
            <span>Starter</span>
            <span>2nd</span>
          </div>
          <div className="app-preview-depth-row">
            <span className="pos">WR</span>
            <span>Starter</span>
            <span>Backup</span>
          </div>
          <div className="app-preview-depth-row">
            <span className="pos">RB</span>
            <span>Lead</span>
            <span>Rot.</span>
          </div>
          <div className="app-preview-depth-row">
            <span className="pos">TE</span>
            <span>TE1</span>
            <span>TE2</span>
          </div>
        </div>
      ) : null}

      {activeTab === 'statistics' ? (
        <div className="app-preview app-preview--statistics">
          <div className="app-preview-player-top">
            <img src="/vacant-player.svg" alt="" className="app-preview-avatar" />
            <div className="app-preview-player-meta">
              <p className="name">Player Name</p>
              <p className="meta">Team • Position • Season</p>
            </div>
          </div>
          <div className="app-preview-stat-list">
            <div className="app-preview-stat-row good">
              <span>Targets</span>
              <strong>11</strong>
            </div>
            <div className="app-preview-stat-row medium">
              <span>Snap %</span>
              <strong>86%</strong>
            </div>
            <div className="app-preview-stat-row poor">
              <span>Drop %</span>
              <strong>6.2%</strong>
            </div>
          </div>
        </div>
      ) : null}
    </aside>
  );
}
