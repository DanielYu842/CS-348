import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './WriteReview.css';

const WriteReview = () => {
  const { id } = useParams();
  const [userId, setUserId] = useState(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [rating, setRating] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const authData = JSON.parse(localStorage.getItem('authUser'));
    if (authData?.user.user_id) {
      setUserId(authData.user.user_id);
    } else {
      setError('You must be logged in to write a review.');
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setLoading(true);

    const numericRating = parseFloat(rating);
    if (isNaN(numericRating) || numericRating < 0 || numericRating > 100) {
      setError('Rating must be a number between 0 and 100.');
      setLoading(false);
      return;
    }

    const reviewData = {
      movie_id: parseInt(id),
      user_id: parseInt(userId),
      title,
      content,
      rating: numericRating,
    };

    try {
      const response = await fetch('http://localhost:8000/reviews/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reviewData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to submit review');
      }

      setSuccessMessage(`Review submitted successfully!`);
      setTitle('');
      setContent('');
      setRating('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reviews-container">
      <h2>Write a Review</h2>

      {error && <p className="error">{error}</p>}
      {successMessage && <p className="success-message">{successMessage}</p>}

      <form className="review-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Review Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="review-input"
          required
        />
        <textarea
          placeholder="Write your review..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="review-input"
          rows={5}
          required
        />
        <input
          type="number"
          placeholder="Rating (0-100)"
          value={rating}
          onChange={(e) => setRating(e.target.value)}
          className="review-input"
          min={0}
          max={100}
          required
        />
        <button type="submit" className="review-submit-button" disabled={loading || !userId}>
          {loading ? 'Submitting...' : 'Submit Review'}
        </button>
      </form>
    </div>
  );
};

export default WriteReview;