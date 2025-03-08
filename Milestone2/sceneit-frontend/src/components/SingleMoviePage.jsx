import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_ENDPOINT } from '../config';
import './SingleMoviePage.css';

const SingleMoviePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMovie = async () => {
      try {
        console.log(`Fetching movie with ID: ${id}`);
        const response = await fetch(`${API_ENDPOINT}/movies/${id}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received movie data:', data);
        setMovie(data);
      } catch (error) {
        console.error('Fetch error:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMovie();
  }, [id]);

  const handleBackClick = () => {
    navigate('/'); // Navigate back to the home/explore page
  };

  if (loading) {
    return <div className="single-movie-page">Loading...</div>;
  }

  if (error) {
    return (
      <div className="single-movie-page">
        <header className="header">
          <h1 className="logo">SceneIt</h1>
        </header>
        <div className="content">
          <h1>Error</h1>
          <p>{error}</p>
          <button className="back-button" onClick={handleBackClick}>Back to Explore</button>
        </div>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="single-movie-page">
        <header className="header">
          <h1 className="logo">SceneIt</h1>
        </header>
        <div className="content">
          <p>No movie data available</p>
          <button className="back-button" onClick={handleBackClick}>Back to Explore</button>
        </div>
      </div>
    );
  }

  return (
    <div className="single-movie-page">
      <header className="header">
        <h1 className="logo">SceneIt</h1>
      </header>
      <div className="content">
        <button className="back-button" onClick={handleBackClick}>Back to Explore</button>
        <div className="movie-details">
          <h1>{movie?.title ?? 'Untitled'}</h1>
          <div className="movie-meta">
            <span className="rating">{movie?.rating ?? 'Not rated'}</span>
            <span className="runtime">{movie?.runtime_in_minutes ?? 'N/A'} min</span>
            <span className="release-date">In Theaters: {movie?.in_theaters_date ?? 'Unknown'}</span>
          </div>
          <p className="description">{movie?.info ?? 'No description available'}</p>
          
          <div className="critics-audience">
            <h2>Critics & Audience</h2>
            <p>{movie?.critics_consensus ?? 'No consensus available'}</p>
            <p>
              <strong>Tomatometer:</strong> 
              <span className="rating">{movie?.tomatometer_rating ?? 'N/A'}%</span> 
              ({movie?.tomatometer_status ?? 'N/A'}) - {movie?.tomatometer_count ?? '0'} reviews
            </p>
            <p>
              <strong>Audience:</strong> 
              <span className="rating">{movie?.audience_rating ?? 'N/A'}%</span> - 
              {(movie?.audience_count)?.toLocaleString() ?? '0'} ratings
            </p>
          </div>
          
          <div className="details">
            <h2>Details</h2>
            <p><strong>Genres:</strong> {movie?.genres?.join(', ') ?? 'No genres listed'}</p>
            <p><strong>Directors:</strong> {movie?.directors?.join(', ') ?? 'No directors listed'}</p>
            <p><strong>Writers:</strong> {movie?.writers?.join(', ') ?? 'No writers listed'}</p>
            <p><strong>Studios:</strong> {movie?.studios?.join(', ') ?? 'No studios listed'}</p>
          </div>
          
          <div className="cast">
            <h2>Cast</h2>
            <ul>
              {movie?.actors?.map((actor, index) => (
                <li key={index}>{actor}</li>
              )) ?? <li>No actors listed</li>}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SingleMoviePage;