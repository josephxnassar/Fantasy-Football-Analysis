/* Reusable sub-navigation component for tab switching within content sections. */

import './SubTabNav.css';

function SubTabNav({ tabs, activeTab, onTabChange, variant = 'default', className }) {
  const navClassName = [
    'sub-tab-nav',
    variant !== 'default' ? `sub-tab-nav--${variant}` : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={navClassName}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={`sub-tab-nav__button ${activeTab === tab.id ? 'is-active' : ''}`}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export default SubTabNav;
