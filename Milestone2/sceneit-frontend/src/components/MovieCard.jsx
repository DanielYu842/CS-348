import React from 'react';
import './MovieCard.css';
import { useNavigate } from 'react-router-dom';

const MovieCard = ({ movie }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    if (movie?.movie_id) {
      navigate(`/movie/${movie.movie_id}`);
    }
  };

  return (
    <div className="movie-card" onClick={handleClick}>
      {movie?.image ? (
        <img src={movie.image} alt={movie?.title || 'Movie'} />
      ) : (
        <div className="movie-no-image"></div>
      )}
      <div className="movie-title">{movie?.title || 'Untitled'}</div>
    </div>
  );
};

export default MovieCard;