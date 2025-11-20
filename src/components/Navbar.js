import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FaHome, FaUpload, FaChartLine, FaComments, FaChartBar, FaLock } from 'react-icons/fa';
import { useProgress } from '../contexts/ProgressContext';
import './Navbar.css';

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { progress, canAccess } = useProgress();

  const navItems = [
    { path: '/', label: 'Home', icon: <FaHome />, step: null },
    { path: '/upload', label: 'Upload Resume', icon: <FaUpload />, step: 'upload' },
    { path: '/ats-score', label: 'ATS Score', icon: <FaChartLine />, step: 'ats-score' },
    { path: '/interview', label: 'Interview', icon: <FaComments />, step: 'interview' },
    { path: '/results', label: 'Results', icon: <FaChartBar />, step: 'results' }
  ];

  const handleNavClick = (e, item) => {
    if (!item.step) return;

    if (!canAccess(item.step)) {
      e.preventDefault();

      // Guide user to the correct previous step in order
      if (!progress.resumeUploaded) {
        navigate('/upload');
      } else if (!progress.atsScoreViewed) {
        navigate('/ats-score');
      } else if (!progress.interviewCompleted) {
        navigate('/interview');
      }
    }
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          RecruifyAi
        </Link>
        <ul className="nav-menu">
          {navItems.map((item) => {
            const isDisabled = item.step && !canAccess(item.step);
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.path} className="nav-item">
                {isDisabled ? (
                  <span
                    className={`nav-link disabled ${isActive ? 'active' : ''}`}
                    title="Complete previous steps to unlock"
                  >
                    <span className="nav-icon">{item.icon}</span>
                    {item.label}
                    <FaLock className="lock-icon" />
                  </span>
                ) : (
                  <Link
                    to={item.path}
                    className={`nav-link ${isActive ? 'active' : ''}`}
                    onClick={(e) => handleNavClick(e, item)}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    {item.label}
                  </Link>
                )}
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar; 