// components/Explore.jsx
import React, { useState } from 'react';
import './Explore.css';

const movieData = [
  {
    id: 1,
    title: "The Shawshank Redemption",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "Two imprisoned men bond over a number of years...",
    rating: "9.3/10",
    genre: "Drama"
  },

  {
    id: 2,
    title: "The Godfather",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "The aging patriarch of an organized crime dynasty...",
    rating: "9.2/10",
    genre: "Crime"
  },
  {
    id: 2,
    title: "The Godfather",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "The aging patriarch of an organized crime dynasty...",
    rating: "9.2/10",
    genre: "Crime"
  },
  {
    id: 2,
    title: "The Godfather",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "The aging patriarch of an organized crime dynasty...",
    rating: "9.2/10",
    genre: "Crime"
  },
  {
    id: 2,
    title: "The Godfather",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "The aging patriarch of an organized crime dynasty...",
    rating: "9.2/10",
    genre: "Crime"
  },
  {
    id: 2,
    title: "The Godfather",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "The aging patriarch of an organized crime dynasty...",
    rating: "9.2/10",
    genre: "Crime"
  },
  {
    id: 2,
    title: "The Godfather",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "The aging patriarch of an organized crime dynasty...",
    rating: "9.2/10",
    genre: "Crime"
  },
  {
    id: 2,
    title: "The Godfather",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "The aging patriarch of an organized crime dynasty...",
    rating: "9.2/10",
    genre: "Crime"
  },
  {
    id: 2,
    title: "The Godfather",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "The aging patriarch of an organized crime dynasty...",
    rating: "9.2/10",
    genre: "Crime"
  },
  {
    id: 2,
    title: "The Godfather",
    image: "https://images.squarespace-cdn.com/content/v1/63bb3e8a824d7e2f7eedf0d3/6dabf093-d7ea-4c67-ae7d-a88b5230cbf7/Scoop+3.jpeg",
    description: "The aging patriarch of an organized crime dynasty...",
    rating: "9.2/10",
    genre: "Crime"
  },
];

const Explore = () => {
  const [selectedMovie, setSelectedMovie] = useState(null);

  const handleMovieClick = (movie) => {
    setSelectedMovie(movie);
  };

  const closeModal = () => {
    setSelectedMovie(null);
  };

  return (
    <div className="explore">
      <header className="header">
        <h1 className="logo">SceneIt</h1>
      </header>

      <div className="content">
        <h2>Popular Movies</h2>
        <div className="movie-row">
          {movieData.map((movie) => (
            <div 
              key={movie.id} 
              className="movie-card"
              onClick={() => handleMovieClick(movie)}
            >
              <img src={movie.image} alt={movie.title} />
              <div className="movie-title">{movie.title}</div>
            </div>
          ))}
        </div>
      </div>

      {selectedMovie && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="close-button" onClick={closeModal}>×</button>
            <img src={selectedMovie.image} alt={selectedMovie.title} className="modal-image" />
            <div className="modal-info">
              <h2>{selectedMovie.title}</h2>
              <p className="rating">{selectedMovie.rating}</p>
              <p className="genre">{selectedMovie.genre}</p>
              <p className="description">{selectedMovie.description}</p>
              <button className="play-button">Play</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Explore;