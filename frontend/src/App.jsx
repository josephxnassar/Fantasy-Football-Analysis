import React from 'react';
import './App.css';
import Rankings from './components/Rankings';

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <h1>Fantasy Football Analysis</h1>
        <p>Your one-stop hub for smarter fantasy decisions</p>
      </header>
      <main>
        <Rankings />
      </main>
    </div>
  );
}

export default App;
