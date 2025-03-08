import './App.css';
import { API_ENDPOINT } from "./config";
import { useEffect, useState } from 'react';

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

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
      <h1>CS348 Project</h1>
      
      <div>
        <h2>API Endpoint:</h2>
        <p>{API_ENDPOINT}</p>
      </div>

      <div>
        <h2>Status:</h2>
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      </div>

      <div>
        <h2>Response Data:</h2>
        {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
        {!loading && !error && !data && <p>No data received</p>}
      </div>
    </div>
  );
}

export default App;