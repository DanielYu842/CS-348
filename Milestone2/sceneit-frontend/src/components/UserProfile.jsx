
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import './UserProfile.css';
import { API_ENDPOINT } from '../config';

const UserProfile = () => {
  const { userId } = useParams();
  const [userData, setUserData] = useState(null);
  const [userReviews, setUserReviews] = useState([]);
  const [likedReviews, setLikedReviews] = useState([]);
  const [likedMovies, setLikedMovies] = useState([]);
  const [similarUsers, setSimilarUsers] = useState([]);
  const [reputation, setReputation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUserData = async () => {
      setLoading(true);
      setError('');
      setUserData(null);
      setReputation(null);
      setUserReviews([]);
      setLikedReviews([]);
      setLikedMovies([]);
      setSimilarUsers([]);

      try {
        const results = await Promise.allSettled([
          fetch(`${API_ENDPOINT}/users/${userId}`),
          fetch(`${API_ENDPOINT}/user_profile/${userId}/user_reviews`),
          fetch(`${API_ENDPOINT}/user_profile/${userId}/user_liked`),
          fetch(`${API_ENDPOINT}/user_profile/${userId}/similar_likes`),
          fetch(`${API_ENDPOINT}/user_profile/${userId}/reputation`),
          fetch(`${API_ENDPOINT}/user_profile/${userId}/liked_movies`)
        ]);

        const [userRes, reviewsRes, likesRes, similarRes, repRes, likedMoviesRes] = results;

        if (userRes.status === 'fulfilled' && userRes.value.ok) {
          setUserData(await userRes.value.json());
        } else {
          console.error("Failed to fetch user details:", userRes.reason || userRes.value?.statusText);
          setError(prev => prev + ' Failed to load user details.');
        }

        if (reviewsRes.status === 'fulfilled' && reviewsRes.value.ok) {
          const reviewsData = await reviewsRes.value.json();
          setUserReviews(reviewsData.results || []);
        } else {
          console.error("Failed to fetch user reviews:", reviewsRes.reason || reviewsRes.value?.statusText);
        }

        if (likesRes.status === 'fulfilled' && likesRes.value.ok) {
          const likesData = await likesRes.value.json();
          const likedReviewIds = likesData.review_ids || [];
          if (likedReviewIds.length > 0) {
            const likedReviewFetches = likedReviewIds.map(id =>
              fetch(`${API_ENDPOINT}/reviews/${id}`)
                .then(res => res.ok ? res.json() : Promise.reject(`Review ${id} fetch failed`))
            );
            const likedReviewResults = await Promise.allSettled(likedReviewFetches);
            const successfulLikedReviews = likedReviewResults
              .filter(result => result.status === 'fulfilled')
              .map(result => result.value);
            setLikedReviews(successfulLikedReviews);
          } else {
            setLikedReviews([]);
          }
        } else {
          console.error("Failed to fetch liked review IDs:", likesRes.reason || likesRes.value?.statusText);
        }

        if (similarRes.status === 'fulfilled' && similarRes.value.ok) {
          setSimilarUsers(await similarRes.value.json() || []);
        } else {
          console.error("Failed to fetch similar users:", similarRes.reason || similarRes.value?.statusText);
        }

        if (repRes.status === 'fulfilled' && repRes.value.ok) {
          setReputation(await repRes.value.json());
        } else {
           if (repRes.status === 'fulfilled' && repRes.value.status === 404) {
                setReputation({ reputation_score: 0, last_updated: null });
           } else {
                console.error("Failed to fetch reputation:", repRes.reason || repRes.value?.statusText);
           }
        }

        if (likedMoviesRes.status === 'fulfilled' && likedMoviesRes.value.ok) {
             setLikedMovies(await likedMoviesRes.value.json() || []);
        } else {
             console.error("Failed to fetch liked movies:", likedMoviesRes.reason || likedMoviesRes.value?.statusText);
        }

      } catch (err) {
        console.error('Unexpected error fetching profile data:', err);
        setError('Could not load profile data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [userId]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
          return 'Invalid date';
      }
      if (!dateString.includes('T') && dateString.length <= 10) {
         const utcDate = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
         return utcDate.toLocaleDateString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric'
         });
      }
      return date.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
      });
    } catch (e) {
      console.error("Error formatting date:", dateString, e);
      return 'Invalid date';
    }
  };

  if (loading) return <div className="user-profile loading">Loading profile...</div>;

  const profileTitle = userData ? `${userData.username}'s Profile` : `User ${userId}'s Profile`;

  return (
    <div className="user-profile">
      <h1>{profileTitle}</h1>

      {error && <p className="error-message">{error}</p>}

      {reputation !== null && (
        <section className="profile-section reputation-section">
          <h2 className="section-title">
            <span className="section-icon" role="img" aria-label="Star">⭐</span>
             Reputation
          </h2>
          <div className="section-content">
            <p><strong>Score:</strong> {reputation.reputation_score ?? 0}</p>
            <p>
                <span className="inline-icon" role="img" aria-label="Calendar">📅</span>
                <strong>Last Updated:</strong> {formatDate(reputation.last_updated)}
            </p>
          </div>
        </section>
      )}

       <section className="profile-section liked-movies-section">
         <h2 className="section-title">
           <span className="section-icon" role="img" aria-label="Heart">❤️</span>
            Liked Movies
         </h2>
          <div className="section-content">
             <ul className="item-list movie-list">
                 {likedMovies.length === 0 ? (
                 <li className="empty-list-item">No liked movies yet.</li>
                 ) : (
                 likedMovies.map(movie => (
                     <li key={movie.movie_id} className="list-item movie-item">
                         <Link to={`/movie/${movie.movie_id}`} className="movie-link">
                             {movie.title}
                         </Link>
                         <span className="liked-date">
                              <span className="inline-icon" role="img" aria-label="Calendar">📅</span>
                             Liked on: {formatDate(movie.liked_at)}
                         </span>
                     </li>
                 ))
                 )}
             </ul>
         </div>
       </section>

      <section className="profile-section reviews-section">
        <h2 className="section-title">
          <span className="section-icon" role="img" aria-label="Scroll">📜</span>
           Your Reviews
        </h2>
        <div className="section-content">
          <ul className="item-list">
            {userReviews.length === 0 ? (
              <li className="empty-list-item">You haven't written any reviews yet.</li>
            ) : (
              userReviews.map(review => (
                <li key={review.review_id} className="list-item review-item">
                  <div className="item-header">
                    <strong>{review.title}</strong>
                    <span className="item-rating">Rated: {review.rating}/100</span>
                  </div>
                  <p className="item-content">{review.content}</p>
                  <div className="item-footer">
                    <span className="item-date">
                      <span className="inline-icon" role="img" aria-label="Calendar">📅</span>
                      {formatDate(review.created_at)}
                    </span>
                    <Link to={`/view-reviews/${review.movie_id}?highlight=${review.review_id}`} className="item-context-link">
                      View Context
                    </Link>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      </section>

      <section className="profile-section likes-section">
        <h2 className="section-title">
          <span className="section-icon" role="img" aria-label="Thumbs Up">👍</span>
           Liked Reviews
        </h2>
         <div className="section-content">
            <ul className="item-list">
                {likedReviews.length === 0 ? (
                <li className="empty-list-item">You haven't liked any reviews yet.</li>
                ) : (
                likedReviews.map(like => (
                    like.review ? (
                        <li key={like.review.review_id} className="list-item liked-item">
                            <div className="item-header">
                                <strong>{like.review.title}</strong>
                                <span className="item-author">by {like.review.username || 'Unknown User'}</span>
                            </div>
                            <p className="item-content">{like.review.content}</p>
                             <div className="item-footer">
                                <span className="item-date">
                                   <span className="inline-icon" role="img" aria-label="Calendar">📅</span>
                                   {formatDate(like.review.created_at)}
                                </span>
                                <Link to={`/view-reviews/${like.review.movie_id}?highlight=${like.review.review_id}`} className="item-context-link">
                                    View Context
                                </Link>
                            </div>
                        </li>
                    ) : (
                         <li key={`liked-review-error-${Math.random()}`} className="error-item">Could not load liked review details.</li>
                    )
                ))
                )}
            </ul>
        </div>
      </section>

      <section className="profile-section similar-users-section">
        <h2 className="section-title">
          <span className="section-icon" role="img" aria-label="Users">👥</span>
           Users with Similar Taste
        </h2>
        <div className="section-content">
          <ul className="item-list user-list">
            {similarUsers.length === 0 ? (
              <li className="empty-list-item">No users found with similar liked movies.</li>
            ) : (
              similarUsers.map(user => (
                <li key={user.user_id} className="list-item user-item">
                  <Link to={`/profile/${user.user_id}`} className="user-link">
                    <strong>{user.username}</strong>
                  </Link>
                  <span className="mutual-count"> – {user.mutual_count} liked movies in common</span>
                </li>
              ))
            )}
          </ul>
        </div>
      </section>
    </div>
  );
};

export default UserProfile;
