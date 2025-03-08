import React from 'react';
import './MovieCard.css';

const MovieCard = ({ movie, onClick }) => {
  return (
    <div className="movie-card" onClick={onClick || (() => {})}>
      {movie.image ? (
        <img src={movie.image} alt={movie.title || 'Movie'} />
      ) : (
        <div className="movie-no-image"></div>
      )}
      <div className="movie-title">{movie.title || 'Untitled'}</div>
    </div>
  );
};

export default MovieCard;