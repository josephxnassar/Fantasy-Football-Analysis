/* Reusable sub-navigation component for tab switching within content sections. Uses shared .sub-nav styles from index.css. */

function SubTabNav({ tabs, activeTab, onTabChange }) {
  return (
    <div className="sub-nav">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={`sub-nav-button ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export default SubTabNav;
