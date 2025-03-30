import React, { useState, useEffect } from 'react';
import './Search.css';
import { API_ENDPOINT } from '../config';
import MovieCard from './MovieCard';

const Search = () => {
  const [searchParams, setSearchParams] = useState({
    title: '',
    genres: '',
    writers: '',
    actors: '',
    studios: '',
    directors: '',
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
      [field]: value.join(','),
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    const queryParams = new URLSearchParams();

    if (searchParams.title) queryParams.append('title', searchParams.title);
    if (searchParams.genres) {
      const genres = searchParams.genres.split(',').map(g => g.trim()).filter(g => g);
      genres.forEach(genre => queryParams.append('genres', genre));
    }
    if (searchParams.writers) {
      const writers = searchParams.writers.split(',').map(w => w.trim()).filter(w => w);
      writers.forEach(writer => queryParams.append('writers', writer));
    }
    if (searchParams.actors) {
      const actors = searchParams.actors.split(',').map(a => a.trim()).filter(a => a);
      actors.forEach(actor => queryParams.append('actors', actor));
    }
    if (searchParams.studios) {
      const studios = searchParams.studios.split(',').map(s => s.trim()).filter(s => s);
      studios.forEach(studio => queryParams.append('studios', studio));
    }
    if (searchParams.directors) {
      const directors = searchParams.directors.split(',').map(d => d.trim()).filter(d => d);
      directors.forEach(director => queryParams.append('directors', director));
    }
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
        <h1 className="logo">SceneIt</h1>
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
              <label>Genres:</label>
              <input
                type="text"
                name="genres"
                value={searchParams.genres}
                onChange={handleInputChange}
                placeholder="e.g.,Drama,Action"
              />
            </div>
          </div>

          {/* Row 2: Writers and Actors */}
          <div className="form-row">
            <div className="form-group">
              <label>Writers:</label>
              <input
                type="text"
                name="writers"
                value={searchParams.writers}
                onChange={handleInputChange}
                placeholder="e.g.,Writer1,Writer2"
              />
            </div>
            <div className="form-group">
              <label>Actors:</label>
              <input
                type="text"
                name="actors"
                value={searchParams.actors}
                onChange={handleInputChange}
                placeholder="e.g.,Actor1,Actor2"
              />
            </div>
          </div>

          {/* Row 3: Studios and Directors */}
          <div className="form-row">
            <div className="form-group">
              <label>Studios:</label>
              <input
                type="text"
                name="studios"
                value={searchParams.studios}
                onChange={handleInputChange}
                placeholder="e.g.,Studio1,Studio2"
              />
            </div>
            <div className="form-group">
              <label>Directors:</label>
              <input
                type="text"
                name="directors"
                value={searchParams.directors}
                onChange={handleInputChange}
                placeholder="e.g.,Director1,Director2"
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