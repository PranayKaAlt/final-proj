import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaDownload, FaUser, FaBriefcase, FaStar } from 'react-icons/fa';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useProgress } from '../contexts/ProgressContext';
import jsPDF from 'jspdf';
import './Results.css';

const Results = () => {
  const navigate = useNavigate();
  const { canAccess, resetProgress } = useProgress();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if user can access results
    if (!canAccess('results')) {
      // Redirect to appropriate step
      if (!canAccess('upload')) {
        navigate('/upload');
      } else if (!canAccess('ats-score')) {
        navigate('/ats-score');
      } else if (!canAccess('interview')) {
        navigate('/interview');
      }
      return;
    }

    // Get results from localStorage (set by Interview component)
    const savedResults = localStorage.getItem('interviewResults');
    if (savedResults) {
      setResults(JSON.parse(savedResults));
      setLoading(false);
    } else {
      setError('No interview results found. Please complete an interview first.');
      setLoading(false);
      navigate('/interview');
    }
  }, [canAccess, navigate]);

  const chartData = results ? [
    { name: 'ATS Score', score: results.ats_score },
    { name: 'Interview Score', score: (results.interview_score / 10) * 100 },
    { name: 'Overall Score', score: Math.round((results.ats_score + (results.interview_score / 10) * 100) / 2) }
  ] : [];

  const getScoreColor = (score) => {
    if (score >= 90) return '#27ae60';
    if (score >= 80) return '#2ecc71';
    if (score >= 70) return '#f39c12';
    if (score >= 60) return '#e67e22';
    return '#e74c3c';
  };

  const getDecisionColor = (decision) => {
    if (decision.includes('Selected')) return '#27ae60';
    if (decision.includes('On Hold')) return '#f39c12';
    return '#e74c3c';
  };

  const handleDownloadPDF = () => {
    if (!results) return;

    const doc = new jsPDF();
    const margin = 18;
    let y = 20;

    const addLine = (text, spacing = 8) => {
      doc.text(text, margin, y);
      y += spacing;
      if (y > 280) {
        doc.addPage();
        y = 20;
      }
    };

    doc.setFontSize(18);
    addLine('AI Interview Report', 12);

    doc.setFontSize(12);
    addLine(`Candidate: ${results.candidate_name}`);
    addLine(`Applied Role: ${results.selected_role}`);
    if (results.predicted_role) {
      addLine(`Predicted Role: ${results.predicted_role}`);
    }
    addLine(`Final Decision: ${results.final_decision}`, 12);

    doc.setFontSize(14);
    addLine('Scores', 10);
    doc.setFontSize(12);
    addLine(`• ATS Compatibility: ${results.ats_score}/100`);
    addLine(`• Interview Performance: ${results.interview_score}/10`);
    addLine(
      `• Overall Score: ${Math.round(
        (results.ats_score + (results.interview_score / 10) * 100) / 2
      )}/100`,
      12
    );

    if (results.reasons) {
      doc.setFontSize(14);
      addLine('Decision Reasons', 10);
      doc.setFontSize(12);
      const splitReasons = doc.splitTextToSize(results.reasons, 170);
      splitReasons.forEach((line) => addLine(line));
      y += 4;
    }

    if (results.skills?.length) {
      doc.setFontSize(14);
      addLine('Key Skills Identified', 10);
      doc.setFontSize(12);
      addLine(results.skills.join(', '), 12);
    }

    if (results.interview_details?.length) {
      doc.setFontSize(14);
      addLine('Interview Breakdown', 10);
      doc.setFontSize(12);
      results.interview_details.forEach((detail, index) => {
        addLine(`${index + 1}. Question: ${detail.question}`);
        if (detail.answer) {
          const answerLines = doc.splitTextToSize(
            `Answer: ${detail.answer}`,
            170
          );
          answerLines.forEach((line) => addLine(line));
        }
        if (detail.score !== undefined) {
          addLine(`Score: ${detail.score}/100`, 10);
        } else {
          y += 6;
        }
      });
    }

    doc.save('AI-Interview-Report.pdf');
  };

  if (loading) {
    return (
      <div className="results">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results">
        <div className="no-results">
          <h2>No Results Available</h2>
          <p>{error}</p>
          <button className="btn" onClick={() => navigate('/upload')}>
            Upload Resume & Start Interview
          </button>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="results">
        <div className="no-results">
          <h2>No Results Available</h2>
          <p>Please complete the interview process to view your results.</p>
          <button className="btn" onClick={() => navigate('/upload')}>
            Upload Resume & Start Interview
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="results">
      <h1 className="page-title">Interview Results & Analysis</h1>
      
      <div className="results-container">
        {/* Header Summary */}
        <div className="results-header">
          <div className="candidate-info">
            <div className="info-item">
              <FaUser className="info-icon" />
              <div>
                <label>Candidate:</label>
                <span>{results.candidate_name}</span>
              </div>
            </div>
            <div className="info-item">
              <FaBriefcase className="info-icon" />
              <div>
                <label>Applied Role:</label>
                <span>{results.selected_role}</span>
              </div>
            </div>
            <div className="info-item">
              <FaStar className="info-icon" />
              <div>
                <label>Predicted Role:</label>
                <span>{results.predicted_role}</span>
              </div>
            </div>
          </div>
          
          <div 
            className="decision-badge" 
            style={{ backgroundColor: getDecisionColor(results.final_decision) }}
          >
            {results.final_decision}
          </div>
        </div>

        {/* Score Overview */}
        <div className="score-overview">
          <div className="score-card">
            <h3>ATS Compatibility</h3>
            <div className="score-value" style={{ color: getScoreColor(results.ats_score) }}>
              {results.ats_score}/100
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${results.ats_score}%`,
                  backgroundColor: getScoreColor(results.ats_score)
                }}
              ></div>
            </div>
          </div>
          
          <div className="score-card">
            <h3>Interview Performance</h3>
            <div className="score-value" style={{ color: getScoreColor((results.interview_score / 10) * 100) }}>
              {results.interview_score}/10
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${(results.interview_score / 10) * 100}%`,
                  backgroundColor: getScoreColor((results.interview_score / 10) * 100)
                }}
              ></div>
            </div>
          </div>
          
          <div className="score-card">
            <h3>Overall Score</h3>
            <div className="score-value" style={{ color: getScoreColor(Math.round((results.ats_score + (results.interview_score / 10) * 100) / 2)) }}>
              {Math.round((results.ats_score + (results.interview_score / 10) * 100) / 2)}/100
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${Math.round((results.ats_score + (results.interview_score / 10) * 100) / 2)}%`,
                  backgroundColor: getScoreColor(Math.round((results.ats_score + (results.interview_score / 10) * 100) / 2))
                }}
              ></div>
            </div>
          </div>
        </div>

        {/* Skills Analysis Chart */}
        <div className="chart-container">
          <h3>Performance Overview</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="score" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Detailed Analysis */}
        <div className="analysis-grid">
          <div className="analysis-card">
            <h3>📋 Decision Reasons</h3>
            <p className="decision-reasons">{results.reasons}</p>
          </div>
          
          {results.skills && results.skills.length > 0 && (
            <div className="analysis-card">
              <h3>🔧 Key Skills Identified</h3>
              <div className="skills-list">
                {results.skills.map((skill, index) => (
                  <span key={index} className="skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          )}
          
          <div className="analysis-card">
            <h3>📊 Interview Details</h3>
            <div className="interview-summary">
              <p><strong>Total Questions:</strong> {results.interview_details?.length || 0}</p>
              <p><strong>Average Score:</strong> {results.interview_score}/10</p>
              <p><strong>Final Decision:</strong> {results.final_decision}</p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="results-actions">
          <button className="btn download-btn" onClick={handleDownloadPDF}>
            <FaDownload /> Download PDF Report
          </button>
          <button
            className="btn"
            onClick={() => {
              resetProgress();
              navigate('/upload');
            }}
          >
            Upload Another Resume
          </button>
        </div>
      </div>
    </div>
  );
};

export default Results; 