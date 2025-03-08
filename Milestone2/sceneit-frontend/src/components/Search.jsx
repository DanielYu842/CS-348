import React, { useState, useEffect } from 'react';
import './Search.css';
import { API_ENDPOINT } from '../config';
import MovieCard from './MovieCard';

const Search = () => {
  const [searchParams, setSearchParams] = useState({
    title: '',
    genres: [],
    writers: [],
    actors: [],
    studios: [],
    directors: [],
    year: '',
    rating: '',
  });
  const [searchResults, setSearchResults] = useState([]);


  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams((prev) => ({
      ...prev,
      [name]: value,
    }));
  };


  const handleArrayInputChange = (e, field) => {
    const value = e.target.value
      .split(',')
      .map((item) => item.trim())
      .filter((item) => item !== '');
    setSearchParams((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    const queryParams = new URLSearchParams();

    if (searchParams.title) queryParams.append('title', searchParams.title);
    if (searchParams.genres.length > 0) queryParams.append('genres', searchParams.genres.join(','));
    if (searchParams.writers.length > 0) queryParams.append('writers', searchParams.writers.join(','));
    if (searchParams.actors.length > 0) queryParams.append('actors', searchParams.actors.join(','));
    if (searchParams.studios.length > 0) queryParams.append('studios', searchParams.studios.join(','));
    if (searchParams.directors.length > 0) queryParams.append('directors', searchParams.directors.join(','));
    if (searchParams.year) queryParams.append('year', searchParams.year);
    if (searchParams.rating) queryParams.append('rating', searchParams.rating);

    try {
      const response = await fetch(`${API_ENDPOINT}/movies/search?${queryParams.toString()}`);
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Error fetching movies:', error);
      setSearchResults([]);
    }
  };

  return (
    <div className="explore">
      <header className="header">
        <h1 className="logo">Sceneit</h1>
      </header>

      <div className="content">
        <h2>Search Movies</h2>
        <form onSubmit={handleSearch} className="search-form">
          {/* Row 1: Title and Genres */}
          <div className="form-row">
            <div className="form-group">
              <label>Title:</label>
              <input
                type="text"
                name="title"
                value={searchParams.title}
                onChange={handleInputChange}
                placeholder="Enter movie title"
              />
            </div>
            <div className="form-group">
              <label>Genres (comma-separated):</label>
              <input
                type="text"
                name="genres"
                value={searchParams.genres.join(', ')}
                onChange={(e) => handleArrayInputChange(e, 'genres')}
                placeholder="e.g., Drama, Action"
              />
            </div>
          </div>

          {/* Row 2: Writers and Actors */}
          <div className="form-row">
            <div className="form-group">
              <label>Writers (comma-separated):</label>
              <input
                type="text"
                name="writers"
                value={searchParams.writers.join(', ')}
                onChange={(e) => handleArrayInputChange(e, 'writers')}
                placeholder="e.g., Writer1, Writer2"
              />
            </div>
            <div className="form-group">
              <label>Actors (comma-separated):</label>
              <input
                type="text"
                name="actors"
                value={searchParams.actors.join(', ')}
                onChange={(e) => handleArrayInputChange(e, 'actors')}
                placeholder="e.g., Actor1, Actor2"
              />
            </div>
          </div>

          {/* Row 3: Studios and Directors */}
          <div className="form-row">
            <div className="form-group">
              <label>Studios (comma-separated):</label>
              <input
                type="text"
                name="studios"
                value={searchParams.studios.join(', ')}
                onChange={(e) => handleArrayInputChange(e, 'studios')}
                placeholder="e.g., Studio1, Studio2"
              />
            </div>
            <div className="form-group">
              <label>Directors (comma-separated):</label>
              <input
                type="text"
                name="directors"
                value={searchParams.directors.join(', ')}
                onChange={(e) => handleArrayInputChange(e, 'directors')}
                placeholder="e.g., Director1, Director2"
              />
            </div>
          </div>

          {/* Row 4: Year and Rating */}
          <div className="form-row">
            <div className="form-group">
              <label>Year:</label>
              <input
                type="number"
                name="year"
                value={searchParams.year}
                onChange={handleInputChange}
                placeholder="Enter year"
              />
            </div>
            <div className="form-group">
              <label>Rating:</label>
              <input
                type="text"
                name="rating"
                value={searchParams.rating}
                onChange={handleInputChange}
                placeholder="e.g., PG"
              />
            </div>
          </div>

          <button type="submit" className="search-button">Search</button>
        </form>

        <div className="movie-grid">
          {searchResults?.['results']?.length > 0 ? (
            searchResults?.['results'].map((movie) => (
              <MovieCard key={movie?.['movie_id']} movie={movie} />
            ))
          ) : (
            <p>No movies found. Try a different search.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Search;