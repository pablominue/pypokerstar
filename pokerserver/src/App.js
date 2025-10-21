import logo from './logo.svg';
import './App.css';
import Range from './components/range.jsx';
import Screen from './components/screen.jsx';
import UpperMenu from './components/upperMenu.jsx';

import { useState, useEffect } from "react";

function WindowManager({ currentMenu, items }) {
  const Component = items[currentMenu]?.component ?? null;
  return Component ? <Component /> : null;
}
function App() {
  const [currentMenu, setCurrentMenu] = useState('preflop');

  const ITEMS = {
    preflop: { component: Range, label: 'Preflop' },
    statistics: { component: () => <div>Statistics Component</div>, label: 'Statistics' },
    // add other entries here: exampleKey: { component: OtherComp, label: 'Other' }
  };

  return (
    <div className="App">
      <header className="App-header">
        <UpperMenu currentMenu={currentMenu} setCurrentMenu={setCurrentMenu} items={ITEMS} />
        <Screen>
          <WindowManager currentMenu={currentMenu} items={ITEMS} />
        </Screen>
      </header>
    </div>
  );
}

export default App;