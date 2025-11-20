import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { FaCloudUploadAlt, FaFilePdf, FaUser, FaBriefcase } from 'react-icons/fa';
import axios from 'axios';
import { useProgress } from '../contexts/ProgressContext';
import API_URL from '../config';
import './ResumeUpload.css';

const ResumeUpload = () => {
  const navigate = useNavigate();
  const { updateProgress } = useProgress();
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
      const response = await axios.post(`${API_URL}/api/upload-resume`, formData, {
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
        skills: response.data.skills,
        session_key: response.data.session_key
      };
      localStorage.setItem('candidateInfo', JSON.stringify(candidateInfo));
      
      // Mark resume as uploaded using context
      updateProgress('resumeUploaded', true);
      
      // Clear form
      setFile(null);
      setCandidateName('');
      setSelectedRole('');
      
      // Navigate to ATS Score page after successful upload
      setTimeout(() => {
        navigate('/ats-score');
      }, 1000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload resume');
    } finally {
      setIsUploading(false);
    }
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
            <h3>✓ Resume Successfully Analyzed!</h3>
            <p style={{ color: '#666', marginTop: '1rem' }}>
              Redirecting to your ATS Score...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeUpload; 