import React, { createContext, useContext, useState, useEffect } from 'react';

const ProgressContext = createContext();

export const useProgress = () => {
  const context = useContext(ProgressContext);
  if (!context) {
    throw new Error('useProgress must be used within a ProgressProvider');
  }
  return context;
};

export const ProgressProvider = ({ children }) => {
  const [progress, setProgress] = useState({
    resumeUploaded: false,
    atsScoreViewed: false,
    interviewCompleted: false,
    resultsAvailable: false
  });

  useEffect(() => {
    // Load progress from localStorage
    const resumeUploaded = localStorage.getItem('resumeUploaded') === 'true';
    const atsScoreViewed = localStorage.getItem('atsScoreViewed') === 'true';
    const interviewCompleted = localStorage.getItem('interviewCompleted') === 'true';
    const resultsAvailable = localStorage.getItem('interviewResults') !== null;

    setProgress({
      resumeUploaded,
      atsScoreViewed,
      interviewCompleted,
      resultsAvailable
    });
  }, []);

  const updateProgress = (key, value) => {
    setProgress(prev => ({
      ...prev,
      [key]: value
    }));
    localStorage.setItem(key, value);
  };

  const resetProgress = () => {
    setProgress({
      resumeUploaded: false,
      atsScoreViewed: false,
      interviewCompleted: false,
      resultsAvailable: false
    });
    localStorage.removeItem('resumeUploaded');
    localStorage.removeItem('atsScoreViewed');
    localStorage.removeItem('interviewCompleted');
    localStorage.removeItem('interviewResults');
    localStorage.removeItem('candidateInfo');
  };

  const canAccess = (step) => {
    switch (step) {
      case 'upload':
        return true; // Always accessible
      case 'ats-score':
        return progress.resumeUploaded;
      case 'interview':
        return progress.resumeUploaded && progress.atsScoreViewed;
      case 'results':
        return progress.interviewCompleted && progress.resultsAvailable;
      default:
        return false;
    }
  };

  return (
    <ProgressContext.Provider value={{ progress, updateProgress, resetProgress, canAccess }}>
      {children}
    </ProgressContext.Provider>
  );
};

