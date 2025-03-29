import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './MasterTable.css';
import { API_ENDPOINT } from '../config';

ModuleRegistry.registerModules([AllCommunityModule]);

const MasterTable = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [rowData, setRowData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const pageSize = 10;

  const fetchMovies = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_ENDPOINT}/movies/search?limit=${pageSize}&offset=${page * pageSize}`);
      const data = await response.json();

      if (data.results.length === 0) {
        setHasMore(false); // no more movies to load
      } else {
        setRowData(prev => [...prev, ...data.results]); // append new movies
      }
    } catch (error) {
      console.error("Error fetching movies:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovies();
  }, [page]);

  useEffect(() => {
    setRowData([]);
    setPage(0);
    setHasMore(true);
  }, [searchTerm]);

  const [columnDefs] = useState([
    { field: 'title', headerName: 'Title', sortable: true, filter: true, flex: 2 },
    { field: 'rating', headerName: 'Rating', sortable: true, filter: true, width: 120 },
    { field: 'in_theaters_date', headerName: 'Release Date', sortable: true, filter: 'agDateColumnFilter', width: 150 },
    { field: 'runtime_in_minutes', headerName: 'Runtime', sortable: true, filter: true, width: 120 },
    { field: 'tomatometer_rating', headerName: 'Tomatometer', sortable: true, filter: true, width: 140 },
    { field: 'audience_rating', headerName: 'Audience Score', sortable: true, filter: true, width: 140 },
  ]);

  const filteredData = rowData.filter(movie =>
    movie.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    movie.rating?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="search-page">
      <header className="header">
        <h1 className="logo">SceneIt</h1>
      </header>

      <div className="search-container">
        <input
          type="text"
          placeholder="Search movies..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />

        <div className="ag-theme-alpine" style={{ height: '480px', width: '100%' }}>
          <AgGridReact
            rowData={filteredData}
            columnDefs={columnDefs}
            defaultColDef={{
              resizable: true,
            }}
          />
        </div>

        {hasMore && (
          <button
            className="load-more-button"
            onClick={() => setPage(prev => prev + 1)}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Load More'}
          </button>
        )}

        {!hasMore && <p className="end-message">You’ve reached the end!</p>}
      </div>
    </div>
  );
};

export default MasterTable;