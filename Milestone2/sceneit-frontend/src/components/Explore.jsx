// components/Explore.jsx
import React, { useState, useEffect } from 'react';
import './Explore.css';
import { API_ENDPOINT } from '../config';
import MovieCard from './MovieCard'; 
import UserCard from './UserCard'; 

const Explore = () => {
  const [topReviewedMovies, setTopReviewedMovies] = useState([]);
  const [worstMovies, setWorstMovies] = useState([]);
  const [bestMovies, setBestMovies] = useState([]);
  const [topLikedUsers, setTopLikedUsers] = useState([]);
  const [loading, setLoading] = useState({
    topReviewed: true,
    worst: true,
    best: true,
    users: true
  });

  // Fetch data for all sections
  useEffect(() => {
    const fetchData = async (endpoint, setter, loadingKey) => {
      try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        setter(data?.["results"] || data);
      } catch (error) {
        console.error(`Error fetching ${loadingKey}:`, error);
        setter([]);
      } finally {
        setLoading(prev => ({ ...prev, [loadingKey]: false }));
      }
    };

    fetchData(`${API_ENDPOINT}/movies_top_reviewed`, setTopReviewedMovies, 'topReviewed');
    fetchData(`${API_ENDPOINT}/movies_top?best=false`, setWorstMovies, 'worst');
    fetchData(`${API_ENDPOINT}/movies_top?best=true`, setBestMovies, 'best');
    fetchData(`${API_ENDPOINT}/users/top_likes`, setTopLikedUsers, 'users');
  }, []);

  const renderRow = (title, items, loadingKey, isUsers = false) => (
    <div className="section">
      <h2>{title}</h2>
      {loading[loadingKey] ? (
        <p>Loading {title.toLowerCase()}...</p>
      ) : (
        <div className="movie-row">
          {items?.map((item) => (
            item.username ? (
              <UserCard 
                key={item.id || item.movie_id || item.user_id} 
                user={item}
              />
            ) : (
              <MovieCard 
                key={item.id || item.movie_id || item.user_id} 
                movie={item}
              />
            )
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="explore">
      <header className="header">
        <h1 className="logo">SceneIt</h1>
      </header>

      <div className="content">
        {renderRow('Top Reviewed Movies', topReviewedMovies, 'topReviewed')}
        {renderRow('Worst Rated Movies', worstMovies, 'worst')}
        {renderRow('Best Rated Movies', bestMovies, 'best')}
        {renderRow('Top Liked Users', topLikedUsers, 'users', true)}
      </div>
    </div>
  );
};

export default Explore;