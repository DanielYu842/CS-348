import './App.css';
import { API_ENDPOINT } from "./config";
import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import Explore from './components/Explore';
import MasterTable from './components/MasterTable';
import Search from './components/Search';
import Signup from './components/Signup';
import Login from './components/Login';
import SingleMoviePage from './components/SingleMoviePage';
import AddMovie from './components/AddMovie';
import UpdateMovie from './components/UpdateMovie';
import MovieReviews from './components/MovieReviews';
import WriteReview from './components/WriteReview';

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeScreen, setActiveScreen] = useState('explore');
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('authToken'));

  useEffect(() => {
    console.log('Fetching from:', API_ENDPOINT);
    
    fetch(API_ENDPOINT)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setData(data);
      })
      .catch(error => {
        setError(error.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
    setActiveScreen('explore');
  };

  const handleLogout = () => {
    localStorage.removeItem('authUser');
    setActiveScreen('explore');
    setIsAuthenticated(false);
  };

  const MainContent = () => {
    return (
      <div className="App">
        <nav className="navigation">
          <Link to="/">
            <button 
              onClick={() => setActiveScreen('explore')}
              className={activeScreen === 'explore' ? 'active' : ''}
            >
              Explore
            </button>
          </Link>
          {/* <Link to="/">
            <button 
              onClick={() => setActiveScreen('moviereviews')}
              className={activeScreen === 'moviereviews' ? 'active' : ''}
            >
              Reviews
            </button>
          </Link> */}
          <Link to="/">
            <button 
              onClick={() => setActiveScreen('masterTable')}
              className={activeScreen === 'masterTable' ? 'active' : ''}
            >
              Master Table
            </button>
          </Link>
          <Link to="/">
            <button 
              onClick={() => setActiveScreen('search')}
              className={activeScreen === 'search' ? 'active' : ''}
            >
              Search
            </button>
          </Link>
          {isAuthenticated && (
            <Link to="/">
              <button 
                onClick={() => setActiveScreen('addmovie')}
                className={activeScreen === 'addmovie' ? 'active' : ''}
              >
                Add Movie
              </button>
            </Link>
          )}
          {isAuthenticated && (
            <Link to="/">
              <button 
                onClick={() => setActiveScreen('updatemovie')}
                className={activeScreen === 'updatemovie' ? 'active' : ''}
              >
                Update Movie
              </button>
            </Link>
          )}
          {!isAuthenticated && (
            <Link to="/">
              <button 
                onClick={() => setActiveScreen('login')}
                className={activeScreen === 'login' ? 'active' : ''}
              >
                Log In
              </button>
            </Link>
          )}
          {!isAuthenticated && (
            <Link to="/">
              <button 
                onClick={() => setActiveScreen('signup')}
                className={activeScreen === 'signup' ? 'active' : ''}
              >
                Sign Up
              </button>
            </Link>
          )}
          {isAuthenticated && <button onClick={handleLogout}>Logout</button>}
        </nav>

        {activeScreen === 'explore' && <Explore />}
        {/* {activeScreen === 'moviereviews' && <MovieReviews />} */}
        {activeScreen === 'masterTable' && <MasterTable />}
        {activeScreen === 'addmovie' && <AddMovie />}
        {activeScreen === 'updatemovie' && <UpdateMovie />}
        {activeScreen === 'search' && <Search />}
        {activeScreen === 'login' && <Login onLogin={handleLogin} onSignup={() => setActiveScreen('signup')} />}
        {activeScreen === 'signup' && <Signup onSignup={() => setActiveScreen('login')} />}
      </div>
    );
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainContent />} />
        <Route 
          path="/movie/:id" 
          element={<SingleMoviePage isAuthenticated={isAuthenticated}/>}
        />
        <Route 
          path="/write-review/:id" 
          element={<WriteReview />} 
        />
        <Route 
          path="/view-reviews/:id" 
          element={<MovieReviews />} 
        />
      </Routes>
    </Router>
  );
}

export default App;