import './UserCard.css';

const UserCard = ({ user }) => {
  return (
    <div className="user-card">
      <img 
        src= "https://img.freepik.com/premium-vector/vector-flat-illustration-black-color-avatar-user-profile-person-icon-gender-neutral-silhouette-profile-picture-suitable-social-media-profiles-icons-screensavers-as-templatex9xa_719432-859.jpg" 
        alt={user.username || 'User'} 
        className="user-avatar"
      />
      <div className="user-info">
        <h3 className="user-name">{user.username || 'Unknown User'}</h3>
        <p className="user-likes">Likes: {user.like_count || 0}</p>
      </div>
    </div>
  );
};

export default UserCard;