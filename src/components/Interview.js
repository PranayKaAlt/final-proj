import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaMicrophone, FaMicrophoneSlash } from 'react-icons/fa';
import axios from 'axios';
import { useProgress } from '../contexts/ProgressContext';
import API_URL from '../config';
import './Interview.css';

const Interview = () => {
  const navigate = useNavigate();
  const { canAccess, updateProgress } = useProgress();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [interviewComplete, setInterviewComplete] = useState(false);
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [validationError, setValidationError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Get candidate info from localStorage
  const [candidateInfo] = useState(() => {
    const saved = localStorage.getItem('candidateInfo');
    return saved ? JSON.parse(saved) : null;
  });

  // Check if user can access interview
  useEffect(() => {
    if (!canAccess('interview')) {
      // Redirect to appropriate step
      if (!canAccess('upload')) {
        navigate('/upload');
      } else if (!canAccess('ats-score')) {
        navigate('/ats-score');
      }
    }
  }, [canAccess, navigate]);

  const loadInterviewQuestions = useCallback(async () => {
    try {
      setLoading(true);
                     const response = await axios.post(`${API_URL}/api/interview-questions`, {
                 candidate_name: candidateInfo.candidate_name,
                 selected_role: candidateInfo.selected_role,
                 session_key: candidateInfo.session_key
               });

      if (response.data.questions && response.data.questions.length > 0) {
        setQuestions(response.data.questions);
        setLoading(false);
      } else {
        setError('No questions generated. Please try again.');
        setLoading(false);
      }
    } catch (err) {
      console.error('Error loading questions:', err);
      setError(err.response?.data?.error || 'Failed to load interview questions');
      setLoading(false);
    }
  }, [candidateInfo]);

  useEffect(() => {
    if (!candidateInfo) {
      setError('No candidate information found. Please upload a resume first.');
      setLoading(false);
      navigate('/upload');
      return;
    }

    // Get interview questions from the AI backend
    if (canAccess('interview')) {
      loadInterviewQuestions();
    }
  }, [candidateInfo, loadInterviewQuestions, canAccess, navigate]);

  // Clear validation error when question changes
  useEffect(() => {
    setValidationError('');
  }, [currentQuestion]);

  const handleAnswerSubmit = async (answer) => {
    // Clear any previous validation errors
    setValidationError('');
    
    // Validate answer before submission
    const trimmedAnswer = answer.trim();
    if (!trimmedAnswer) {
      setValidationError('Please provide an answer before submitting.');
      return;
    }

    if (trimmedAnswer.length < 10) {
      setValidationError('Please provide a more detailed answer (at least 10 characters).');
      return;
    }

    setIsSubmitting(true);

    try {
      // Submit answer to AI backend for analysis
      const response = await axios.post(`${API_URL}/api/submit-answer`, {
        candidate_name: candidateInfo.candidate_name,
        selected_role: candidateInfo.selected_role,
        session_key: candidateInfo.session_key,
        question: questions[currentQuestion],
        answer: trimmedAnswer,
        question_index: currentQuestion
      });

      const { score, feedback } = response.data;
      
      // Store the answer and score
      const newAnswers = [...answers, trimmedAnswer];
      const newScores = [...scores, score];
      
      setAnswers(newAnswers);
      setScores(newScores);
      
      // Clear the textarea only after successful submission
      const answerInput = document.getElementById('answerInput');
      if (answerInput) {
        answerInput.value = '';
      }
      
      // Show feedback
      alert(`Score: ${score}/10\nFeedback: ${feedback}`);
      
      // Clear validation error on success
      setValidationError('');
      
      // Move to next question or complete interview
      if (currentQuestion < questions.length - 1) {
        setCurrentQuestion(currentQuestion + 1);
      } else {
        setInterviewComplete(true);
        // Get final results
        await getFinalResults();
      }
    } catch (err) {
      console.error('Error submitting answer:', err);
      // Show validation error instead of breaking the page
      setValidationError(err.response?.data?.error || 'Failed to submit answer. Please try again.');
      // Don't clear the answer so user can retry
    } finally {
      setIsSubmitting(false);
    }
  };

  const getFinalResults = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/interview-results`, {
        candidate_name: candidateInfo.candidate_name,
        selected_role: candidateInfo.selected_role,
        session_key: candidateInfo.session_key
      });

      // Store results in localStorage for the Results component
      localStorage.setItem('interviewResults', JSON.stringify(response.data));
      
      // Mark interview as completed
      updateProgress('interviewCompleted', 'true');
      updateProgress('resultsAvailable', 'true');
    } catch (err) {
      console.error('Error getting final results:', err);
      setError('Failed to get final results');
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // In a real app, this would handle actual voice recording
  };

  const getOverallScore = () => {
    if (scores.length === 0) return 0;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  };

  if (loading) {
    return (
      <div className="interview">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading AI-generated questions...</p>
        </div>
      </div>
    );
  }

  // Only show full error page for unrecoverable errors (missing data, no questions, etc.)
  // Validation errors are shown inline
  if (error && !questions.length && !loading) {
    return (
      <div className="interview">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button className="btn" onClick={() => navigate('/upload')}>
            Go Back to Upload
          </button>
        </div>
      </div>
    );
  }

  if (interviewComplete) {
    return (
      <div className="interview">
        <h1 className="page-title">Interview Complete!</h1>
        <div className="results-container">
          <div className="overall-score">
            <h2>Overall Score</h2>
            <div className="score-display">{getOverallScore()}/100</div>
            <p>Your interview has been completed and analyzed by AI!</p>
          </div>
          
          <div className="question-results">
            <h3>Question-by-Question Results</h3>
            {questions.map((question, index) => (
              <div key={index} className="question-result">
                <div className="question-text">{question}</div>
                <div className="answer-text">{answers[index]}</div>
                <div className="score-bar">
                  <div className="score-label">Score: {scores[index]}/100</div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${scores[index]}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="interview-actions">
            <button className="btn" onClick={() => navigate('/results')}>
              View Detailed Results
            </button>
            <button className="btn secondary" onClick={() => {
              // Reset progress and navigate to upload
              localStorage.clear();
              window.location.href = '/upload';
            }}>
              Start New Session
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="interview">
      <h1 className="page-title">AI Interview Session</h1>
      <p className="page-subtitle">
        Answer the following AI-generated questions to complete your interview assessment
      </p>

      <div className="interview-container">
        <div className="progress-indicator">
          <div className="progress-text">
            Question {currentQuestion + 1} of {questions.length}
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="question-card">
          <h2 className="question-title">Question {currentQuestion + 1}</h2>
          <p className="question-text">{questions[currentQuestion]}</p>
          
          <div className="answer-input">
            <textarea
              placeholder="Type your answer here..."
              className="answer-textarea"
              rows="6"
              id="answerInput"
              disabled={isSubmitting}
            />
            
            {validationError && (
              <div className="validation-error">
                {validationError}
              </div>
            )}
            
            <div className="input-actions">
              <button 
                className={`btn record-btn ${isRecording ? 'recording' : ''}`}
                onClick={toggleRecording}
                disabled={isSubmitting}
              >
                {isRecording ? <FaMicrophoneSlash /> : <FaMicrophone />}
                {isRecording ? 'Stop Recording' : 'Voice Input'}
              </button>
              
              <button 
                className="btn submit-btn"
                onClick={() => {
                  const answer = document.getElementById('answerInput').value;
                  handleAnswerSubmit(answer);
                }}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Answer'}
              </button>
            </div>
          </div>
        </div>

        <div className="interview-tips">
          <h3>💡 Interview Tips</h3>
          <ul>
            <li>Provide specific examples from your experience</li>
            <li>Use the STAR method (Situation, Task, Action, Result)</li>
            <li>Be concise but thorough in your responses</li>
            <li>Show your problem-solving approach</li>
            <li>Demonstrate your technical knowledge</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Interview; 