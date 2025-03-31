import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_ENDPOINT } from '../config';
import './SingleMoviePage.css';

const SingleMoviePage = ({ isAuthenticated }) => {
    const { id: movieId } = useParams();
    const navigate = useNavigate();
    const [movie, setMovie] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isLiked, setIsLiked] = useState(false);
    const [likeLoading, setLikeLoading] = useState(false);

    const authUser = React.useMemo(() => JSON.parse(localStorage.getItem('authUser')) || {}, []);
    const loggedInUserId = authUser?.user?.user_id;

    const fetchMovie = useCallback(async () => {
        try {
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
        }
    }, [movieId]);

    const checkIfLiked = useCallback(async () => {
        if (!loggedInUserId || !movieId) {
            setIsLiked(false);
            return;
        }
        try {
            const response = await fetch(`${API_ENDPOINT}/users/${loggedInUserId}/liked_movies/${movieId}`);
            if (!response.ok) {
                if (response.status === 404) {
                    setIsLiked(false);
                    return;
                }
                const data = await response.json().catch(() => ({}));
                throw new Error(data.detail || `Failed to check like status: ${response.status}`);
            }
            const data = await response.json();
            setIsLiked(data.is_liked);
        } catch (err) {
            console.error('Check like status error:', err);
            setIsLiked(false);
        }
    }, [loggedInUserId, movieId]);

    useEffect(() => {
         let isMounted = true;
         const loadData = async () => {
             setLoading(true);
             await fetchMovie();
             if (isMounted) {
                 await checkIfLiked();
                 setLoading(false);
             }
         };
         loadData();
         return () => { isMounted = false; };
    }, [fetchMovie, checkIfLiked]);

    const handleBackClick = () => {
        navigate(-1);
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

        const endpoint = isLiked ? 'unlike_movie' : 'like_movie';
        const url = `${API_ENDPOINT}/${endpoint}?user_id=${loggedInUserId}&movie_id=${movieId}`;
        const method = isLiked ? 'DELETE' : 'POST';

        try {
            const response = await fetch(url, { method });
            const responseData = await response.json().catch(e => ({ detail: response.statusText || `HTTP error ${response.status}` }));

            if (!response.ok) {
                throw new Error(responseData.detail || `Failed to ${isLiked ? 'unlike' : 'like'} movie. Status: ${response.status}`);
            }
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
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return 'Invalid date';
            if (!dateString.includes('T') && dateString.length <= 10) {
                const utcDate = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
                return utcDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
            }
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
        } catch (e) { return 'Invalid date'; }
    };

    const imageBaseUrl = 'https://picsum.photos/seed/';
    const imageWidth = 300;
    const imageHeight = 450;
    const imageSeed = movie?.movie_id ? movie.movie_id + 10 : 'movie_default';
    const imageUrl = `${imageBaseUrl}${imageSeed}/${imageWidth}/${imageHeight}`;

    if (loading) {
        return <div className="single-movie-page loading">Loading Movie Details...</div>;
    }

    if (error && !movie) {
        return (
            <div className="single-movie-page error-page">
                <div className="page-header">
                    <button className="action-button back-button" onClick={handleBackClick} title="Go back">
                        <span role="img" aria-label="Back Arrow">⬅️</span> Back
                    </button>
                </div>
                <div className="content error-content">
                    <h1>Error Loading Movie</h1>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    if (!movie) {
        return (
            <div className="single-movie-page error-page">
                <div className="page-header">
                    <button className="action-button back-button" onClick={handleBackClick} title="Go back">
                        <span role="img" aria-label="Back Arrow">⬅️</span> Back
                    </button>
                </div>
                <div className="content error-content">
                    <h1>Movie Not Found</h1>
                    <p>The requested movie could not be loaded.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="single-movie-page">
            <div className="page-header">
                <button className="action-button back-button" onClick={handleBackClick} title="Go back">
                    <span role="img" aria-label="Back Arrow">⬅️</span> Back
                </button>
                <div className="header-actions">
                    <button className="action-button reviews-button" onClick={handleViewReviewClick} title="See user reviews">
                        <span role="img" aria-label="Reviews">📝</span> Reviews
                    </button>
                    {isAuthenticated && (
                        <button className="action-button write-review-button" onClick={handleWriteReviewClick} title="Write your own review">
                            <span role="img" aria-label="Write">✏️</span> Write Review
                        </button>
                    )}
                    {isAuthenticated && (
                        <button
                            className={`action-button like-button ${isLiked ? 'liked' : ''}`}
                            onClick={handleLikeUnlikeClick}
                            disabled={likeLoading}
                            title={isLiked ? 'Unlike this movie' : 'Like this movie'}
                        >
                            {likeLoading ? '...' : (isLiked ? '❤️ Liked' : '🤍 Like')}
                        </button>
                    )}
                </div>
            </div>

            <div className="content">
                {error && <p className="inline-error">{error}</p>}

                <div className="movie-layout">
                    <div className="movie-poster-container">
                        <img
                            className="movie-poster"
                            src={imageUrl}
                            alt={`${movie.title} Poster Placeholder`}
                            onError={(e) => { e.target.style.visibility = 'hidden'; }}
                        />
                    </div>
                    <div className="movie-details">
                        <h1>{movie.title}</h1>
                        <div className="movie-meta">
                            <span className="meta-item rating-tag">{movie.rating || 'NR'}</span>
                            <span className="meta-item"><span role="img" aria-label="Clock">⏱️</span> {movie.runtime_in_minutes || 'N/A'} min</span>
                            <span className="meta-item"><span role="img" aria-label="Calendar">🗓️</span> Released: {formatDate(movie.in_theaters_date)}</span>
                            {movie.on_streaming_date &&
                                <span className="meta-item"><span role="img" aria-label="Streaming">📺</span> Streaming: {formatDate(movie.on_streaming_date)}</span>
                            }
                        </div>

                        <div className="section description-section">
                            <h2>Synopsis</h2>
                            <p className="description">{movie.info || 'No synopsis available.'}</p>
                        </div>

                        {movie.critics_consensus &&
                            <div className="section critics-consensus-section">
                                <h2>Critics Consensus</h2>
                                <p className="consensus">"{movie.critics_consensus}"</p>
                            </div>
                        }

                        <div className="section scores-section">
                            <h2>Ratings</h2>
                            <div className="scores">
                                <div className="score-item">
                                    <span className="score-label tomatometer-label"><span role="img" aria-label="Tomato">🍅</span> Tomatometer:</span>
                                    <span className="score-value">{movie.tomatometer_rating ?? 'N/A'}%</span>
                                    <span className="score-details">({movie.tomatometer_status || 'N/A'}) - {movie.tomatometer_count ?? 0} reviews</span>
                                </div>
                                <div className="score-item">
                                    <span className="score-label audience-label"><span role="img" aria-label="Popcorn">🍿</span> Audience Score:</span>
                                    <span className="score-value">{movie.audience_rating ?? 'N/A'}%</span>
                                    <span className="score-details">{movie.audience_count?.toLocaleString() ?? 0} ratings</span>
                                </div>
                            </div>
                        </div>

                        <div className="section details-section">
                            <h2>Details</h2>
                            <div className="details-grid">
                                <p><strong>Genres:</strong> {movie.genres?.join(', ') || 'N/A'}</p>
                                <p><strong>Directors:</strong> {movie.directors?.join(', ') || 'N/A'}</p>
                                <p><strong>Writers:</strong> {movie.writers?.join(', ') || 'N/A'}</p>
                                <p><strong>Studios:</strong> {movie.studios?.join(', ') || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="section cast-section">
                    <h2>Cast</h2>
                    <ul className="cast-list">
                        {movie.actors && movie.actors.length > 0 ? (
                            movie.actors.map((actor, index) => (
                                <li key={index}>{actor}</li>
                            ))
                        ) : (
                            <li className="no-cast">No cast information available.</li>
                        )}
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default SingleMoviePage;
