import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FaArrowRight,
  FaPlay,
  FaRobot,
  FaClipboardList,
  FaComments,
  FaChartBar,
  FaLightbulb,
  FaFileAlt,
  FaCheckCircle,
  FaBolt,
  FaShieldAlt,
  FaStar
} from 'react-icons/fa';
import './Home.css';

const Home = () => {
  const heroBenefits = [
    { icon: <FaCheckCircle />, label: 'Guided workflow with instant insights' },
    { icon: <FaBolt />, label: 'Lightning-fast ATS parsing & scoring' },
    { icon: <FaShieldAlt />, label: 'Private, secure, and compliant' }
  ];

  const featureCards = [
    {
      title: 'AI Resume Parser',
      description: 'Automatically extract and analyze key information from resumes using advanced NLP and machine learning algorithms.',
      icon: <FaRobot />
    },
    {
      title: 'ATS Scoring System',
      description: 'Get comprehensive ATS compatibility scores with detailed insights on keywords, formatting, and resume optimization.',
      icon: <FaClipboardList />
    },
    {
      title: 'AI Interview Bot',
      description: 'Practice with intelligent interview bots that ask role-specific questions and provide real-time feedback.',
      icon: <FaComments />
    },
    {
      title: 'Performance Analytics',
      description: 'Track your progress with detailed analytics on ATS scores, interview performance, and improvement trends.',
      icon: <FaChartBar />
    },
    {
      title: 'Smart Recommendations',
      description: 'Receive personalized suggestions to improve your resume, enhance skills, and optimize interview responses.',
      icon: <FaLightbulb />
    },
    {
      title: 'Report Generation',
      description: 'Download comprehensive PDF reports with ATS analysis, interview transcripts, and actionable recommendations.',
      icon: <FaFileAlt />
    }
  ];

  const stats = [
    { label: 'Hiring teams onboarded', value: '2.1K+' },
    { label: 'Candidate journeys automated', value: '48K+' },
    { label: 'Avg. time saved per hire', value: '62%' },
    { label: 'Candidate satisfaction score', value: '4.9/5' }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    const revealEls = document.querySelectorAll('.reveal-on-scroll');
    revealEls.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  return (
    <div className="home landing">
      <section className="hero-section">
        <div className="hero-blur hero-blur-left" aria-hidden="true"></div>
        <div className="hero-blur hero-blur-right" aria-hidden="true"></div>

        <div className="hero-grid">
          <div className="hero-copy">
            <h1>
              Reinventing the hiring journey with powerful AI insights
            </h1>
            <p className="hero-lead">
              Upload resumes, surface ATS insights, and run interviewer bots in a single guided journey. No noise—just a
              polished workflow that moves candidates from upload to decision in minutes.
            </p>

            <div className="hero-actions">
              <Link to="/upload" className="hero-btn primary">
                Start analyzing resumes
                <FaArrowRight />
              </Link>
             
            
            </div>
            <div className="hero-benefits">
              {heroBenefits.map((benefit) => (
                <p key={benefit.label}>
                  <span className="benefit-icon">{benefit.icon}</span>
                  {benefit.label}
                </p>
              ))}
            </div>
            <div className="hero-proof">
              <div className="hero-avatars">
                <img src="https://i.pravatar.cc/80?img=12" alt="Hiring lead" />
                <img src="https://i.pravatar.cc/80?img=32" alt="Recruiter" />
                <img src="https://i.pravatar.cc/80?img=5" alt="Talent partner" />
                <img src="https://i.pravatar.cc/80?img=48" alt="People ops" />
              </div>
              <div className="hero-rating">
                <div className="rating-stars">
                  {[...Array(5)].map((_, idx) => (
                    <FaStar key={idx} />
                  ))}
                </div>
                <strong>Trusted by 2,000+ modern recruiting teams</strong>
                <small>4.9/5 average satisfaction across active workspaces</small>
              </div>
            </div>
          </div>
          <div className="hero-image-box">
            <div className="hero-image-wrapper">
              <img 
                src="/person-with-laptop.jpg" 
                alt="RecruifyAi" 
                className="hero-image"
              />
            </div>
            <div className="hero-features-box reveal-on-scroll">
              <ul className="hero-features-list">
                <li>
                  <span className="feature-marker">01</span>
                  <span className="feature-content">
                    <strong>Instant resume scan</strong>
                    <small>Upload once, extract every key detail immediately.</small>
                  </span>
                </li>
                <li>
                  <span className="feature-marker">02</span>
                  <span className="feature-content">
                    <strong>Deep ATS scoring</strong>
                    <small>Surface keyword gaps, structure issues, and quick wins.</small>
                  </span>
                </li>
                <li>
                  <span className="feature-marker">03</span>
                  <span className="feature-content">
                    <strong>Adaptive AI interview</strong>
                    <small>Practice with role-aware questions and coaching.</small>
                  </span>
                </li>
                <li>
                  <span className="feature-marker">04</span>
                  <span className="feature-content">
                    <strong>Actionable dossier</strong>
                    <small>Download a full report with insights & recommendations.</small>
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Project Features Grid */}
        <div className="project-features-section">
          <div className="project-features-grid">
            {featureCards.map((feature, index) => (
              <div
                className="project-feature-box reveal-on-scroll"
                key={feature.title}
                style={{ '--reveal-delay': `${index * 0.1}s` }}
              >
                <span className="project-feature-icon">{feature.icon}</span>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="stats-section">
          <div className="stats-grid">
            {stats.map((stat, index) => (
              <div className="stat-item reveal-on-scroll" key={stat.label} style={{ '--reveal-delay': `${index * 0.1}s` }}>
                <p className="stat-label">{stat.label}</p>
                <p className="stat-number">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;