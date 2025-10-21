import './upperMenu.css';


function UpperMenu({ currentMenu, setCurrentMenu, items }) {
  return (
    <div className="upper-menu">
      {Object.entries(items).map(([key, meta]) => (
        <button
          key={key}
          className={`menu-button ${currentMenu === key ? 'active' : ''}`}
          onClick={() => setCurrentMenu(key)}
        >
          {meta.label ?? key}
        </button>
      ))}
    </div>
  );
}

export default UpperMenu;