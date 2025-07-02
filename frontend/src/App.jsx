import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <nav className="sidebar">
        <h1 className="logo">GovBidGenie</h1>
        <ul>
          <li>
            <NavLink to="/" end>Dashboard</NavLink>
          </li>
          <li>
            <NavLink to="/opportunities">Opportunities</NavLink>
          </li>
        </ul>
      </nav>
      <div className="main-content">
        <Outlet />
      </div>
      </div>
  );
}

export default App; 