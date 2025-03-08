// components/Search.jsx
import React, { useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
// Remove ag-grid.css, keep only the theme CSS
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './Search.css';

// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);

const Search = () => {
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data
  const [rowData] = useState([
    { title: "The Shawshank Redemption", genre: "Drama", rating: 9.3, year: 1994 },
    { title: "The Godfather", genre: "Crime", rating: 9.2, year: 1972 },
    { title: "Inception", genre: "Sci-Fi", rating: 8.8, year: 2010 },
    { title: "Pulp Fiction", genre: "Crime", rating: 8.9, year: 1994 },
    { title: "The Dark Knight", genre: "Action", rating: 9.0, year: 2008 },
    { title: "Forrest Gump", genre: "Drama", rating: 8.8, year: 1994 },
    { title: "The Matrix", genre: "Sci-Fi", rating: 8.7, year: 1999 },
    { title: "Titanic", genre: "Romance", rating: 7.8, year: 1997 },
    { title: "Avatar", genre: "Sci-Fi", rating: 7.8, year: 2009 },
    { title: "The Lion King", genre: "Animation", rating: 8.5, year: 1994 },
  ]);

  // Column definitions
  const [columnDefs] = useState([
    { field: "title", sortable: true, filter: true, flex: 1 },
    { field: "genre", sortable: true, filter: true, width: 150 },
    { field: "rating", sortable: true, filter: true, width: 120 },
    { field: "year", sortable: true, filter: true, width: 100 },
  ]);

  // Filter data based on search term
  const filteredData = rowData.filter(movie =>
    movie.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    movie.genre.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="search-page">
      <header className="header">
        <h1 className="logo">Sceneit</h1>
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
          <AgGridReact
            rowData={filteredData}
            columnDefs={columnDefs}
            pagination={true}
            paginationPageSize={5}
            paginationPageSizeSelector={[5, 10, 20]} // Fix pagination errors
            defaultColDef={{
              resizable: true,
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default Search;