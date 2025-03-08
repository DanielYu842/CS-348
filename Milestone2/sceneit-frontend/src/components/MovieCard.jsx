import React from 'react';
import './MovieCard.css';
import { useNavigate } from 'react-router-dom';

const MovieCard = ({ movie }) => {
  const navigate = useNavigate();
  return (
    <div className="movie-card" onClick={()=> {navigate(`/movie/${movie.movie_id}`)}} >
      {movie?.image ? (
        <img src={movie.image} alt={movie.title || 'Movie'} />
      ) : (
        <div className="movie-no-image"></div>
      )}
      <div className="movie-title">{movie?.title || 'Untitled'}</div>
    </div>
  );
};

export default MovieCard;