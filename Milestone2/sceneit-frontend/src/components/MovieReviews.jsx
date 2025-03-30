import React, { useState, useEffect } from 'react';
import './MovieReviews.css';
import { useParams } from 'react-router-dom';

const MovieReviews = () => {
  const { id } = useParams(); // movie_id from URL
  const movieId = id;
  const [reviews, setReviews] = useState([]);
  const [movieTitle, setMovieTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchMovieTitle = async () => {
    try {
      const res = await fetch(`http://localhost:8000/movies/${movieId}`);
      const data = await res.json();
      if (res.ok) {
        setMovieTitle(data.title);
      } else {
        setMovieTitle('(Unknown Title)');
      }
    } catch (err) {
      console.error('Error fetching movie title:', err);
      setMovieTitle('(Unknown Title)');
    }
  };

  const fetchReviews = async () => {
    if (!movieId) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`http://localhost:8000/reviews/search?movie_id=${movieId}`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch reviews');
      }

      setReviews(data.reviews);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovieTitle();
    fetchReviews();
  }, [movieId]);

  return (
    <div className="reviews-container">
      <h2>Movie Reviews of {movieTitle}</h2>

      {loading && <p>Loading reviews...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && reviews.length === 0 && <p>No reviews found for this movie.</p>}
      {!loading && reviews.length > 0 && (
        <table className="reviews-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Title</th>
              <th>Review</th>
              <th>Rating</th>
              <th>Likes</th>
              <th>Created At</th>
            </tr>
          </thead>
          <tbody>
            {reviews.map((review) => (
              <tr key={review.review_id}>
                <td>{review.username}</td>
                <td>{review.email}</td>
                <td>{review.title}</td>
                <td>{review.content}</td>
                <td>{review.rating}</td>
                <td>{review.likes_count}</td>
                <td>{new Date(review.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default MovieReviews;