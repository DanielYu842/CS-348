
import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_ENDPOINT } from '../config';
import './SingleMoviePage.css';
// Removed WriteReview import as it's not used directly here

const SingleMoviePage = ({ isAuthenticated }) => {
    const { id: movieId } = useParams();
    const navigate = useNavigate();
    const [movie, setMovie] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isLiked, setIsLiked] = useState(false);
    const [likeLoading, setLikeLoading] = useState(false);

    const authUser = JSON.parse(localStorage.getItem('authUser')) || {};
    const loggedInUserId = authUser?.user?.user_id;

    const fetchMovie = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch(`${API_ENDPOINT}/movies/${movieId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setMovie(data);
        } catch (err) {
            console.error('Fetch movie error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [movieId]);

    const checkIfLiked = useCallback(async () => {
        if (!loggedInUserId || !movieId) return;
        try {
            const response = await fetch(`${API_ENDPOINT}/users/${loggedInUserId}/liked_movies/${movieId}`);
            if (!response.ok) {
                 // If 404, it means user/movie not found, treat as not liked
                if (response.status === 404) {
                    setIsLiked(false);
                    return;
                }
                throw new Error('Failed to check like status');
            }
            const data = await response.json();
            setIsLiked(data.is_liked);
        } catch (err) {
            console.error('Check like status error:', err);
            // Don't set main page error, just assume not liked if check fails
            setIsLiked(false);
        }
    }, [loggedInUserId, movieId]);

    useEffect(() => {
        fetchMovie();
        checkIfLiked();
    }, [fetchMovie, checkIfLiked]);

    const handleBackClick = () => {
        navigate('/');
    };

    const handleWriteReviewClick = () => {
        navigate(`/write-review/${movieId}`);
    };

    const handleViewReviewClick = () => {
        navigate(`/view-reviews/${movieId}`);
    };

    const handleLikeUnlikeClick = async () => {
        if (!loggedInUserId) {
            setError("Please log in to like movies.");
            return;
        }
        setLikeLoading(true);
        setError(null);

        const url = isLiked
            ? `${API_ENDPOINT}/unlike_movie?user_id=${loggedInUserId}&movie_id=${movieId}`
            : `${API_ENDPOINT}/like_movie?user_id=${loggedInUserId}&movie_id=${movieId}`;

        const method = isLiked ? 'DELETE' : 'POST';

        try {
            const response = await fetch(url, { method });
            if (!response.ok) {
                 const data = await response.json().catch(() => ({}));
                throw new Error(data.detail || `Failed to ${isLiked ? 'unlike' : 'like'} movie`);
            }
            // Toggle liked state on success
            setIsLiked(!isLiked);
        } catch (err) {
            console.error('Like/Unlike error:', err);
            setError(err.message);
        } finally {
            setLikeLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'Unknown';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric'
            });
        } catch (e) { return 'Invalid date'; }
    };

    // Placeholder image logic (same as MovieCard)
    const imageBaseUrl = 'https://picsum.photos/seed/';
    const imageWidth = 300; // Larger image for single page
    const imageHeight = 450;
    const imageSeed = movie?.movie_id ? movie.movie_id + 10 : 'movie_default';
    const imageUrl = `${imageBaseUrl}${imageSeed}/${imageWidth}/${imageHeight}`;


    if (loading) {
        return <div className="single-movie-page loading">Loading Movie Details...</div>;
    }

    if (error && !movie) { // Show error prominently only if movie failed to load
        return (
            <div className="single-movie-page error-page">
                <header className="header">
                    <h1 className="logo">SceneIt</h1>
                </header>
                <div className="content error-content">
                    <h1>Error Loading Movie</h1>
                    <p>{error}</p>
                    <button className="action-button back-button" onClick={handleBackClick}>Back to Explore</button>
                </div>
            </div>
        );
    }

     if (!movie) { // Handles case where loading finished but movie is still null (shouldn't happen if error handling is right)
        return (
             <div className="single-movie-page error-page">
                <header className="header">
                    <h1 className="logo">SceneIt</h1>
                </header>
                <div className="content error-content">
                    <h1>Movie Not Found</h1>
                    <p>The requested movie could not be loaded.</p>
                     <button className="action-button back-button" onClick={handleBackClick}>Back to Explore</button>
                 </div>
             </div>
        );
     }


    return (
        <div className="single-movie-page">
            {/* Header can be removed if using global nav */}
            {/* <header className="header">
                <h1 className="logo">SceneIt</h1>
            </header> */}
            <div className="content">
                 {error && <p className="inline-error">{error}</p>} {/* Show minor errors inline */}

                <div className="action-bar">
                    <button className="action-button back-button" onClick={handleBackClick} title="Go back to movie list">
                        ← Back
                    </button>
                    <button className="action-button reviews-button" onClick={handleViewReviewClick} title="See user reviews">
                        View Reviews
                    </button>
                    {isAuthenticated && (
                        <button className="action-button write-review-button" onClick={handleWriteReviewClick} title="Write your own review">
                            Write Review
                        </button>
                    )}
                     {isAuthenticated && (
                        <button
                            className={`action-button like-button ${isLiked ? 'liked' : ''}`}
                            onClick={handleLikeUnlikeClick}
                            disabled={likeLoading}
                            title={isLiked ? 'Unlike this movie' : 'Like this movie'}
                        >
                            {likeLoading ? '...' : (isLiked ? '❤️ Liked' : '🤍 Like Movie')}
                        </button>
                    )}
                </div>

                <div className="movie-layout">
                    <div className="movie-poster">
                         <img
                            src={imageUrl}
                            alt={`${movie.title} Poster Placeholder`}
                            onError={(e) => { e.target.style.display = 'none'; }}
                         />
                         {/* Optional: Add a div that shows if image onError */}
                         {/* <div className="poster-placeholder">No Image</div> */}
                    </div>
                    <div className="movie-details">
                        <h1>{movie.title}</h1>
                        <div className="movie-meta">
                            <span className="meta-item rating-tag">{movie.rating || 'NR'}</span>
                            <span className="meta-item">{movie.runtime_in_minutes || 'N/A'} min</span>
                            <span className="meta-item">Released: {formatDate(movie.in_theaters_date)}</span>
                        </div>
                        <p className="description">{movie.info || 'No description available.'}</p>

                        <div className="section critics-audience">
                            <h2>Critics & Audience</h2>
                            {movie.critics_consensus && <p className="consensus">"{movie.critics_consensus}"</p>}
                            <div className="scores">
                                <p>
                                    <span className="score-label">Tomatometer:</span>
                                    <span className="score-value">{movie.tomatometer_rating ?? 'N/A'}%</span>
                                    <span className="score-details">({movie.tomatometer_status || 'N/A'}) - {movie.tomatometer_count ?? 0} reviews</span>
                                </p>
                                <p>
                                     <span className="score-label">Audience Score:</span>
                                    <span className="score-value">{movie.audience_rating ?? 'N/A'}%</span>
                                    <span className="score-details">{movie.audience_count?.toLocaleString() ?? 0} ratings</span>
                                </p>
                            </div>
                        </div>

                        <div className="section details">
                            <h2>Details</h2>
                            <p><strong>Genres:</strong> {movie.genres?.join(', ') || 'N/A'}</p>
                            <p><strong>Directors:</strong> {movie.directors?.join(', ') || 'N/A'}</p>
                            <p><strong>Writers:</strong> {movie.writers?.join(', ') || 'N/A'}</p>
                            <p><strong>Studios:</strong> {movie.studios?.join(', ') || 'N/A'}</p>
                            <p><strong>Streaming:</strong> {formatDate(movie.on_streaming_date)}</p>
                        </div>
                    </div>
                 </div>


                <div className="section cast">
                    <h2>Cast</h2>
                    <ul className="cast-list">
                        {movie.actors && movie.actors.length > 0 ? (
                            movie.actors.map((actor, index) => (
                                <li key={index}>{actor}</li>
                            ))
                        ) : (
                            <li>No cast information available.</li>
                        )}
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default SingleMoviePage;