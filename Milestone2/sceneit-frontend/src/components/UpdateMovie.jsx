import React, { useState } from 'react';
import './UpdateMovie.css';

const UpdateMovie = ({ onMovieUpdated }) => {
  const [movieId, setMovieId] = useState('');
  const [movieData, setMovieData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchMovieDetails = async () => {
    if (!movieId) return;
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`http://localhost:8000/movies/${movieId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch movie details');
      }

      setMovieData(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`http://localhost:8000/movies/${movieId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(movieData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to update movie');
      }

      alert('Movie updated successfully!');
      onMovieUpdated();
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="update-movie-page">
      <div className="update-movie-container">
        <h1 className="logo">Update a Movie</h1>
        <input
          type="text"
          placeholder="Enter Movie ID"
          value={movieId}
          onChange={(e) => setMovieId(e.target.value)}
          className="movie-input"
        />
        <button onClick={fetchMovieDetails} className="movie-button">Fetch Movie Details</button>
        {error && <p className="error-message">{error}</p>}
        {loading && <p className="loading-message">Loading...</p>}
        {movieData && (
          <div className="scrollable-form">
            <form className="update-movie-form" onSubmit={handleSubmit}>
              {Object.keys(movieData).map((key) => (
                <input
                  key={key}
                  type="text"
                  placeholder={key.replace('_', ' ').toUpperCase()}
                  value={Array.isArray(movieData[key]) ? movieData[key].join(', ') : movieData[key]}
                  onChange={(e) => {
                    setMovieData((prevData) => ({
                      ...prevData,
                      [key]: Array.isArray(prevData[key])
                        ? e.target.value.split(',').map(item => item.trim())
                        : isNaN(prevData[key]) ? e.target.value : Number(e.target.value),
                    }));
                  }}
                  className="movie-input"
                />
              ))}
              <button type="submit" className="movie-button" disabled={loading}>{loading ? 'Updating Movie...' : 'Update Movie'}</button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default UpdateMovie;