// --- START OF FILE MovieReviews.jsx ---

import React, { useState, useEffect } from 'react';
import './MovieReviews.css';
import { useParams, Link } from 'react-router-dom';

const MovieReviews = () => {
    const { id: movieId } = useParams();
    const [reviews, setReviews] = useState([]);
    const [movieTitle, setMovieTitle] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const authUser = JSON.parse(localStorage.getItem('authUser')) || {};
    const loggedInUserId = authUser?.user?.user_id;

    const fetchMovieTitle = async () => {
        try {
            const res = await fetch(`http://localhost:8000/movies/${movieId}`);
            if (!res.ok) throw new Error('Failed to fetch movie details');
            const data = await res.json();
            setMovieTitle(data.title);
        } catch (err) {
            console.error('Error fetching movie title:', err);
            setMovieTitle('(Unknown Movie)');
            setError(prev => prev + ' Failed to load movie title.');
        }
    };

    const fetchReviews = async () => {
        if (!movieId) return;
        setLoading(true);
        setError('');
        try {
            const response = await fetch(`http://localhost:8000/reviews/search?movie_id=${movieId}`);
            if (!response.ok) {
                const data = await response.json().catch(() => ({}));
                throw new Error(data.detail || 'Failed to fetch reviews');
            }
            const data = await response.json();

            // Fetch full details for each review to get like counts accurately
            const reviewDetailPromises = data.reviews.map(reviewStub =>
                fetch(`http://localhost:8000/reviews/${reviewStub.review_id}`)
                    .then(res => res.ok ? res.json() : Promise.reject(`Failed review ${reviewStub.review_id}`))
            );

            const detailedResults = await Promise.allSettled(reviewDetailPromises);
            const successfulReviews = detailedResults
                .filter(result => result.status === 'fulfilled')
                .map(result => result.value.review); // Extract the main review object

            setReviews(successfulReviews || []);

        } catch (error) {
            console.error('Error fetching reviews:', error);
            setError(error.message || 'An error occurred loading reviews.');
            setReviews([]);
        } finally {
            setLoading(false);
        }
    };


    useEffect(() => {
        fetchMovieTitle();
        fetchReviews();
    }, [movieId]);

    const handleLike = async (reviewId) => {
        if (!loggedInUserId) {
            setError('You must be logged in to like reviews.');
            return;
        }
        try {
            const response = await fetch(`http://localhost:8000/likes/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ review_id: reviewId, user_id: loggedInUserId }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to like review');
            }

            setReviews(prevReviews =>
                prevReviews.map(review =>
                    review.review_id === reviewId
                        ? { ...review, like_count: (review.like_count || 0) + 1 }
                        : review
                )
            );
            setError(''); // Clear error on success
        } catch (error) {
            console.error('Error liking review:', error);
            setError(error.message); // Show specific error from backend if possible
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric'
            });
        } catch (e) { return ''; }
    };

    return (
        <div className="movie-reviews-page">
            <h1 className="reviews-page-title">
                Reviews for <span className="movie-highlight">{movieTitle}</span>
            </h1>

            {loading && <p className="loading-message">Loading reviews...</p>}
            {error && <p className="error-message">{error}</p>}

            {!loading && reviews.length === 0 && !error && (
                <p className="no-reviews-message">Be the first to review this movie!</p>
            )}

            {!loading && reviews.length > 0 && (
                <div className="reviews-list">
                    {reviews.map((review) => (
                        <div key={review.review_id} className="review-card">
                            <div className="review-card-header">
                                <div className="user-info">
                                    <span className="user-icon" role="img" aria-label="User">👤</span>
                                    <Link to={`/profile/${review.user_id}`} className="username-link">
                                        {review.username}
                                    </Link>
                                    {/* <span className="user-email">({review.email})</span> */}
                                </div>
                                <div className="rating-info">
                                    <span className="rating-icon" role="img" aria-label="Star">⭐</span>
                                    {review.rating ? `${review.rating}/100` : 'No Rating'}
                                </div>
                            </div>
                            <h3 className="review-title">{review.title}</h3>
                            <p className="review-content">{review.content}</p>
                            <div className="review-card-footer">
                                <span className="review-date">
                                    <span role="img" aria-label="Calendar" className="footer-icon">📅</span>
                                    {formatDate(review.created_at)}
                                </span>
                                <div className="review-actions">
                                    <span className="like-count">
                                        <span role="img" aria-label="Thumbs Up" className="footer-icon">👍</span>
                                        {review.like_count || 0} Likes
                                    </span>
                                    {loggedInUserId && loggedInUserId !== review.user_id && (
                                        <button
                                            onClick={() => handleLike(review.review_id)}
                                            className="like-button"
                                            title="Like this review"
                                        >
                                            Like
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default MovieReviews;