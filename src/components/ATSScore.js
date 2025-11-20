import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaChartLine, FaArrowRight, FaCheckCircle } from 'react-icons/fa';
import { useProgress } from '../contexts/ProgressContext';
import './ATSScore.css';

const ATSScore = () => {
  const navigate = useNavigate();
  const { canAccess, updateProgress } = useProgress();
  const [candidateInfo, setCandidateInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user can access ATS score page
    if (!canAccess('ats-score')) {
      navigate('/upload');
      return;
    }

    // Get candidate info from localStorage
    const saved = localStorage.getItem('candidateInfo');
    if (saved) {
      setCandidateInfo(JSON.parse(saved));
      setLoading(false);
      // Mark ATS score as viewed
      updateProgress('atsScoreViewed', true);
    } else {
      // No resume uploaded, redirect to upload
      navigate('/upload');
    }
  }, [navigate, canAccess, updateProgress]);

  const handleStartInterview = () => {
    navigate('/interview');
  };

  if (loading) {
    return (
      <div className="ats-score">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your ATS score...</p>
        </div>
      </div>
    );
  }

  if (!candidateInfo) {
    return null;
  }

  const getScoreColor = (score) => {
    if (score >= 90) return '#27ae60';
    if (score >= 80) return '#2ecc71';
    if (score >= 70) return '#f39c12';
    if (score >= 60) return '#e67e22';
    return '#e74c3c';
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Needs Improvement';
  };

  return (
    <div className="ats-score">
      <h1 className="page-title">ATS Compatibility Score</h1>
      <p className="page-subtitle">
        Your resume has been analyzed by our AI system
      </p>

      <div className="ats-container">
        <div className="score-display-card">
          <div className="score-icon">
            <FaChartLine />
          </div>
          <div className="score-value" style={{ color: getScoreColor(candidateInfo.ats_score) }}>
            {candidateInfo.ats_score}/100
          </div>
          <div className="score-label">{getScoreLabel(candidateInfo.ats_score)}</div>
          
          <div className="progress-bar-large">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${candidateInfo.ats_score}%`,
                backgroundColor: getScoreColor(candidateInfo.ats_score)
              }}
            ></div>
          </div>
        </div>

        <div className="analysis-section">
          <div className="analysis-card">
            <h3>Resume Analysis</h3>
            <div className="result-grid">
              <div className="result-item">
                <div className="result-label">Candidate Name</div>
                <div className="result-value">{candidateInfo.candidate_name}</div>
              </div>
              <div className="result-item">
                <div className="result-label">Selected Role</div>
                <div className="result-value">{candidateInfo.selected_role}</div>
              </div>
              <div className="result-item">
                <div className="result-label">Predicted Role</div>
                <div className="result-value">{candidateInfo.predicted_role}</div>
              </div>
              {candidateInfo.skills && candidateInfo.skills.length > 0 && (
                <div className="result-item full-width">
                  <div className="result-label">Key Skills Identified</div>
                  <div className="skills-list">
                    {candidateInfo.skills.map((skill, index) => (
                      <span key={index} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="info-box">
            <FaCheckCircle className="info-icon" />
            <div>
              <h4>What does this score mean?</h4>
              <p>
                Your ATS (Applicant Tracking System) score reflects how well your resume matches 
                the requirements for the selected role. A higher score indicates better alignment 
                with job requirements and keyword matching.
              </p>
            </div>
          </div>
        </div>

        <div className="action-section">
          <button className="btn btn-primary" onClick={handleStartInterview}>
            Proceed to AI Interview
            <FaArrowRight className="btn-icon" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ATSScore;

