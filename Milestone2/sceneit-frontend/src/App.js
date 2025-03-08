import './App.css';
import { API_ENDPOINT } from "./config";
import { useEffect, useState } from 'react';
import Explore from './components/Explore';
import MasterTable from './components/MasterTable';
import Search from './components/Search';

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeScreen, setActiveScreen] = useState('explore');

  useEffect(() => {
    console.log('Fetching from:', API_ENDPOINT);
    
    fetch(API_ENDPOINT)
      .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Received data:', data);
        setData(data);
      })
      .catch(error => {
        console.error('Fetch error:', error);
        setError(error.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div className="App">
      <nav className="navigation">
        <button 
          onClick={() => setActiveScreen('explore')}
          className={activeScreen === 'explore' ? 'active' : ''}
        >
          Explore
        </button>
        <button 
          onClick={() => setActiveScreen('masterTable')}
          className={activeScreen === 'masterTable' ? 'active' : ''}
        >
          Master Table
        </button>
        <button 
          onClick={() => setActiveScreen('Search')}
          className={activeScreen === 'search' ? 'active' : ''}
        >
          Search
        </button>
      </nav>

      {activeScreen === 'explore' && <Explore />}
      {activeScreen === 'masterTable' && <MasterTable />}
      {activeScreen === 'Search' && <Search />}
    </div> 
  );
}

export default App;