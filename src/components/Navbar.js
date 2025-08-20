import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaHome, FaUpload, FaComments, FaChartBar } from 'react-icons/fa';
import './Navbar.css';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: <FaHome /> },
    { path: '/upload', label: 'Upload Resume', icon: <FaUpload /> },
    { path: '/interview', label: 'Interview', icon: <FaComments /> },
    { path: '/results', label: 'Results', icon: <FaChartBar /> }
  ];

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          AI Recruitment System
        </Link>
        <ul className="nav-menu">
          {navItems.map((item) => (
            <li key={item.path} className="nav-item">
              <Link
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar; 