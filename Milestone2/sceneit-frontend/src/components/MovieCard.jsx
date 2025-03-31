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

  const imageBaseUrl = 'https://picsum.photos/seed/';
  const imageWidth = 200;
  const imageHeight = 300;
  const imageSeed = movie?.movie_id ? movie.movie_id + 10 : 'default';
  const imageUrl = `${imageBaseUrl}${imageSeed}/${imageWidth}/${imageHeight}`;

  return (
    <div className="movie-card" onClick={handleClick} title={movie?.title || 'Untitled'}>
      <img
        src={imageUrl}
        alt={movie?.title || 'Movie Poster Placeholder'}
        onError={(e) => {
          e.target.style.display = 'none';
        }}
      />
      <div className="movie-title">{movie?.title || 'Untitled'}</div>
    </div>
  );
};

export default MovieCard;
