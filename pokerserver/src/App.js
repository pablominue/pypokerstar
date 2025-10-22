import logo from './logo.svg';
import './App.css';
import Range from './components/range.jsx';
import Screen from './components/screen.jsx';
import UpperMenu from './components/upperMenu.jsx';
import Statistics from './components/statistics.jsx';

import { useState, useEffect } from "react";

function WindowManager({ currentMenu, items }) {
  const Component = items[currentMenu]?.component ?? null;
  return Component ? <Component /> : null;
}
function App() {
  const [currentMenu, setCurrentMenu] = useState('preflop');
  // const [currentMenu, setCurrentMenu] = useState('statistics'); // <-- uncomment to open stats by default

  const ITEMS = {
    preflop: { component: Range, label: 'Preflop' },
    statistics: { component: Statistics, label: 'Statistics' }, // <-- use real component
    // add other entries here...
  };

  return (
    <div>
      <UpperMenu currentMenu={currentMenu} setCurrentMenu={setCurrentMenu} items={ITEMS} />
      <Screen>
        <WindowManager currentMenu={currentMenu} items={ITEMS} />
        </Screen>
    </div>
  );
}

export default App;