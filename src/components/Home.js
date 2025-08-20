import React from 'react';
import { Link } from 'react-router-dom';
import { FaRobot, FaFileAlt, FaComments, FaChartLine, FaUsers, FaClock } from 'react-icons/fa';
import './Home.css';

const Home = () => {
  const features = [
    {
      icon: <FaRobot />,
      title: 'AI-Powered Analysis',
      description: 'Advanced machine learning algorithms analyze resumes and match candidates with job requirements.'
    },
    {
      icon: <FaFileAlt />,
      title: 'Smart Resume Parsing',
      description: 'Automatically extract key information from resumes including skills, experience, and education.'
    },
    {
      icon: <FaComments />,
      title: 'AI Interviewer',
      description: 'Intelligent interview system that asks role-specific questions and evaluates responses in real-time.'
    },
    {
      icon: <FaChartLine />,
      title: 'Performance Analytics',
      description: 'Comprehensive scoring and feedback system with detailed performance metrics.'
    },
    {
      icon: <FaUsers />,
      title: 'Bias-Free Evaluation',
      description: 'Objective assessment system that eliminates human bias and ensures fair candidate evaluation.'
    },
    {
      icon: <FaClock />,
      title: 'Time Efficient',
      description: 'Reduce recruitment time by up to 80% with automated screening and evaluation.'
    }
  ];

  return (
    <div className="home">
      <h1 className="page-title">AI-Powered Recruitment System</h1>
      <p className="page-subtitle">
        Transform your hiring process with intelligent automation, unbiased evaluation, and data-driven insights
      </p>

      <div className="feature-grid">
        {features.map((feature, index) => (
          <div key={index} className="feature-card">
            <div className="feature-icon">{feature.icon}</div>
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-description">{feature.description}</p>
          </div>
        ))}
      </div>

      <div className="cta-section">
        <h2>Ready to revolutionize your recruitment?</h2>
        <p className="mb-20">Start with a simple resume upload and experience the future of hiring</p>
        <Link to="/upload" className="cta-button">
          Get Started Now
        </Link>
      </div>

      <div className="stats-section">
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-number">90%</div>
            <div className="stat-label">Time Saved</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">95%</div>
            <div className="stat-label">Accuracy Rate</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">24/7</div>
            <div className="stat-label">Availability</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home; 