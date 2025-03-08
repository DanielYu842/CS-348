import React, { useState } from 'react';
import './AddMovie.css';

const AddMovie = ({ onMovieAdded }) => {
  const [title, setTitle] = useState('');
  const [info, setInfo] = useState('');
  const [criticsConsensus, setCriticsConsensus] = useState('');
  const [rating, setRating] = useState('');
  const [inTheatersDate, setInTheatersDate] = useState('');
  const [onStreamingDate, setOnStreamingDate] = useState('');
  const [runtime, setRuntime] = useState('');
  const [tomatometerStatus, setTomatometerStatus] = useState('');
  const [tomatometerRating, setTomatometerRating] = useState('');
  const [tomatometerCount, setTomatometerCount] = useState('');
  const [audienceRating, setAudienceRating] = useState('');
  const [audienceCount, setAudienceCount] = useState('');
  const [genres, setGenres] = useState('');
  const [writers, setWriters] = useState('');
  const [actors, setActors] = useState('');
  const [studios, setStudios] = useState('');
  const [directors, setDirectors] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
 
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
  
    const movieData = {
      title,
      info,
      critics_consensus: criticsConsensus,
      rating,
      in_theaters_date: inTheatersDate,
      on_streaming_date: onStreamingDate,
      runtime_in_minutes: runtime ? parseInt(runtime) : 0, // Ensure it's a number
      tomatometer_status: tomatometerStatus,
      tomatometer_rating: tomatometerRating ? parseFloat(tomatometerRating) : 0,
      tomatometer_count: tomatometerCount ? parseInt(tomatometerCount) : 0,
      audience_rating: audienceRating ? parseFloat(audienceRating) : 0,
      audience_count: audienceCount ? parseInt(audienceCount) : 0,
      genres: genres ? genres.split(',').map(g => g.trim()) : [],
      writers: writers ? writers.split(',').map(w => w.trim()) : [],
      actors: actors ? actors.split(',').map(a => a.trim()) : [],
      studios: studios ? studios.split(',').map(s => s.trim()) : [],
      directors: directors ? directors.split(',').map(d => d.trim()) : [],
    };
  
    console.log("🚀 Sending movie data:", JSON.stringify(movieData, null, 2)); // ✅ Log formatted data
  
    try {
      const response = await fetch('http://localhost:8000/movies/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(movieData),
      });
  
      console.log("📡 Response Status:", response.status); // ✅ Log response status
  
      const data = await response.json();
      console.log("🔍 API Response:", data); // ✅ Log API response
  
      if (!response.ok) {
        throw new Error(data.message || 'Failed to add movie');
      }
  
      alert('✅ Movie added successfully!');
      onMovieAdded();
    } catch (error) {
      console.error("❌ Error adding movie:", error); // ✅ Log errors
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-movie-page">
      <div className="add-movie-container">
        <h1 className="logo">Add a Movie</h1>
        <div className="scrollable-form">
          <form className="add-movie-form" onSubmit={handleSubmit}>
            <input type="text" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} className="movie-input" required />
            <input type="text" placeholder="Info" value={info} onChange={(e) => setInfo(e.target.value)} className="movie-input" required />
            <input type="text" placeholder="Critics Consensus" value={criticsConsensus} onChange={(e) => setCriticsConsensus(e.target.value)} className="movie-input" required />
            <input type="text" placeholder="Rating (e.g., PG-13)" value={rating} onChange={(e) => setRating(e.target.value)} className="movie-input" required />
            <input type="date" placeholder="In Theaters Date" value={inTheatersDate} onChange={(e) => setInTheatersDate(e.target.value)} className="movie-input" required />
            <input type="date" placeholder="On Streaming Date" value={onStreamingDate} onChange={(e) => setOnStreamingDate(e.target.value)} className="movie-input" required />
            <input type="number" placeholder="Runtime in Minutes" value={runtime} onChange={(e) => setRuntime(e.target.value)} className="movie-input" required />
            <input type="text" placeholder="Tomatometer Status" value={tomatometerStatus} onChange={(e) => setTomatometerStatus(e.target.value)} className="movie-input" required />
            <input type="text" placeholder="Genres (comma-separated)" value={genres} onChange={(e) => setGenres(e.target.value)} className="movie-input" required />
            <input type="text" placeholder="Writers (comma-separated)" value={writers} onChange={(e) => setWriters(e.target.value)} className="movie-input" required />
            <input type="text" placeholder="Actors (comma-separated)" value={actors} onChange={(e) => setActors(e.target.value)} className="movie-input" required />
            <input type="text" placeholder="Studios (comma-separated)" value={studios} onChange={(e) => setStudios(e.target.value)} className="movie-input" required />
            <input type="text" placeholder="Directors (comma-separated)" value={directors} onChange={(e) => setDirectors(e.target.value)} className="movie-input" required />
            {error && <p className="error-message">{error}</p>}
            <button type="submit" className="movie-button" disabled={loading}>{loading ? 'Adding Movie...' : 'Add Movie'}</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AddMovie;