import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { FaCloudUploadAlt, FaFilePdf, FaUser, FaBriefcase } from 'react-icons/fa';
import axios from 'axios';
import './ResumeUpload.css';

const ResumeUpload = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [candidateName, setCandidateName] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');

  const roles = [
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
    'Data Scientist',
    'ML Engineer',
    'DevOps Engineer',
    'UI/UX Designer',
    'Android Developer',
    'QA Tester',
    'Project Manager'
  ];

  const onDrop = (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError('');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file || !candidateName || !selectedRole) {
      setError('Please fill in all fields and upload a resume');
      return;
    }

    setIsUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('resume', file);
    formData.append('candidate_name', candidateName);
    formData.append('selected_role', selectedRole);

    try {
      const response = await axios.post('/api/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setUploadResult(response.data);
      
      // Store candidate info for the interview component
      const candidateInfo = {
        candidate_name: candidateName,
        selected_role: selectedRole,
        predicted_role: response.data.predicted_role,
        ats_score: response.data.ats_score,
        skills: response.data.skills
      };
      localStorage.setItem('candidateInfo', JSON.stringify(candidateInfo));
      
      // Clear form
      setFile(null);
      setCandidateName('');
      setSelectedRole('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload resume');
    } finally {
      setIsUploading(false);
    }
  };

  const startInterview = () => {
    navigate('/interview');
  };

  return (
    <div className="resume-upload">
      <h1 className="page-title">Upload Resume</h1>
      <p className="page-subtitle">
        Upload your resume and let our AI analyze it for the perfect role match
      </p>

      <div className="upload-container">
        <div className="upload-form">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="candidateName">
                <FaUser /> Candidate Name
              </label>
              <input
                type="text"
                id="candidateName"
                value={candidateName}
                onChange={(e) => setCandidateName(e.target.value)}
                className="input-field"
                placeholder="Enter your full name"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="selectedRole">
                <FaBriefcase /> Desired Role
              </label>
              <select
                id="selectedRole"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="input-field"
                required
              >
                <option value="">Select a role</option>
                {roles.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Resume Upload</label>
              <div
                {...getRootProps()}
                className={`dropzone ${isDragActive ? 'active' : ''}`}
              >
                <input {...getInputProps()} />
                <FaCloudUploadAlt className="upload-icon" />
                {isDragActive ? (
                  <p>Drop the resume here...</p>
                ) : (
                  <div>
                    <p>Drag & drop a PDF resume here, or click to select</p>
                    <p className="file-info">Only PDF files are supported</p>
                  </div>
                )}
              </div>
              {file && (
                <div className="file-preview">
                  <FaFilePdf className="file-icon" />
                  <span>{file.name}</span>
                  <span className="file-size">
                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
              )}
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              className="btn upload-btn"
              disabled={isUploading || !file || !candidateName || !selectedRole}
            >
              {isUploading ? 'Analyzing...' : 'Analyze Resume'}
            </button>
          </form>
        </div>

        {uploadResult && (
          <div className="upload-result">
            <h3>AI Analysis Complete!</h3>
            <div className="result-grid">
              <div className="result-item">
                <div className="result-label">Predicted Role</div>
                <div className="result-value">{uploadResult.predicted_role}</div>
              </div>
              <div className="result-item">
                <div className="result-label">ATS Score</div>
                <div className="result-value">{uploadResult.ats_score}/100</div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${uploadResult.ats_score}%` }}
                  ></div>
                </div>
              </div>
              {uploadResult.skills && uploadResult.skills.length > 0 && (
                <div className="result-item">
                  <div className="result-label">Key Skills</div>
                  <div className="skills-list">
                    {uploadResult.skills.map((skill, index) => (
                      <span key={index} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="result-actions">
              <button 
                className="btn"
                onClick={startInterview}
              >
                Start AI Interview
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeUpload; 