// components/MasterTable.jsx
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
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await fetch(`${API_ENDPOINT}/movies/search`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        setRowData(data.results || []);
      } catch (error) {
        console.error('Error fetching movies:', error);
        setRowData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [API_ENDPOINT]); 

  const [columnDefs] = useState([
    { field: 'title', headerName: 'Title', sortable: true, filter: true, flex: 2 },
    { field: 'rating', headerName: 'Rating', sortable: true, filter: true, width: 120 },
    { field: 'in_theaters_date', headerName: 'Release Date', sortable: true, filter: 'agDateColumnFilter', width: 150 },
    { field: 'runtime_in_minutes', headerName: 'Runtime', sortable: true, filter: true, width: 120 },
    { field: 'tomatometer_rating', headerName: 'Tomatometer', sortable: true, filter: true, width: 140 },
    { field: 'audience_rating', headerName: 'Audience Score', sortable: true, filter: true, width: 140 },
  ]);

  // Filter data based on search term
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

        <div className="ag-theme-alpine" style={{ height: 500, width: '100%' }}>
          {loading ? (
            <p>Loading movies...</p>
          ) : (
            <AgGridReact
              rowData={filteredData}
              columnDefs={columnDefs}
              pagination={true}
              paginationPageSize={5}
              paginationPageSizeSelector={[5, 10, 20]}
              defaultColDef={{
                resizable: true,
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default MasterTable;