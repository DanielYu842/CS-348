import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import './UserProfile.css';
import { API_ENDPOINT } from '../config';

const UserProfile = () => {
  const { userId } = useParams();
  const [userReviews, setUserReviews] = useState([]);
  const [likedReviews, setLikedReviews] = useState([]);
  const [similarUsers, setSimilarUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const [reviewsRes, likesRes, similarRes] = await Promise.allSettled([
          fetch(`${API_ENDPOINT}/user_profile/${userId}/user_reviews`),
          fetch(`${API_ENDPOINT}/user_profile/${userId}/user_liked`),
          fetch(`${API_ENDPOINT}/user_profile/${userId}/most_mutual`)
        ]);

        // Handle reviews
        if (reviewsRes.status === 'fulfilled' && reviewsRes.value.ok) {
          const reviewsData = await reviewsRes.value.json();
          setUserReviews(reviewsData.results || []);
        } else {
          setUserReviews([]);
        }

        // Handle likes
        if (likesRes.status === 'fulfilled' && likesRes.value.ok) {
          const likesData = await likesRes.value.json();
          const likedReviewIds = likesData.review_ids || [];
          const likedReviewFetches = likedReviewIds.map(id =>
            fetch(`${API_ENDPOINT}/reviews/${id}`).then(res => res.json())
          );
          const likedReviewData = await Promise.all(likedReviewFetches);
          setLikedReviews(likedReviewData);
        } else {
          setLikedReviews([]);
        }

        // Handle similar users
        if (similarRes.status === 'fulfilled' && similarRes.value.ok) {
          const similarData = await similarRes.value.json();
          setSimilarUsers(similarData ? [similarData] : []);
        } else {
          setSimilarUsers([]);
        }
      } catch (err) {
        setError('Unexpected error fetching profile data');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [userId]);

  if (loading) return <div className="user-profile">Loading...</div>;

  return (
    <div className="user-profile">
      {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}

      <h1 className="section-title">Your Reviews</h1>
      <ul className="review-list">
        {userReviews.length === 0 ? (
          <li>No reviews yet.</li>
        ) : (
          userReviews.map(review => (
            <li key={review.review_id}>
              <strong>{review.title}</strong> – Rated {review.rating}/100
              <p>{review.content}</p>
            </li>
          ))
        )}
      </ul>

      <h1 className="section-title">Liked Reviews</h1>
      <ul className="review-list">
        {likedReviews.length === 0 ? (
          <li>No liked reviews yet.</li>
        ) : (
          likedReviews.map(like => (
            <li key={like.review.review_id}>
              <strong>{like.review.title}</strong> – By {like.review.username}
              <p>{like.review.content}</p>
            </li>
          ))
        )}
      </ul>

      <h1 className="section-title">Users with Similar Taste</h1>
      <ul className="user-list">
        {similarUsers.length === 0 ? (
          <li>No similar users found.</li>
        ) : (
          similarUsers.map(user => (
            <li key={user.user_id}>
              <strong>User {user.user_id}</strong> – {user.mutual_count} movies in common
            </li>
          ))
        )}
      </ul>
    </div>
  );
};

export default UserProfile;