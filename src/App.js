import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ProgressProvider } from './contexts/ProgressContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './components/Home';
import ResumeUpload from './components/ResumeUpload';
import ATSScore from './components/ATSScore';
import Interview from './components/Interview';
import Results from './components/Results';
import './App.css';

function App() {
  return (
    <ProgressProvider>
      <Router>
        <div className="App">
          <Navbar />
          <main className="main-content">
            <div className="container">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/upload" element={<ResumeUpload />} />
                <Route path="/ats-score" element={<ATSScore />} />
                <Route path="/interview" element={<Interview />} />
                <Route path="/results" element={<Results />} />
              </Routes>
            </div>
          </main>
          <Footer />
        </div>
      </Router>
    </ProgressProvider>
  );
}

export default App; 