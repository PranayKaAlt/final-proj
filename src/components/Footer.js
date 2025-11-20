import React from 'react';
import { Link } from 'react-router-dom';
import { FaGlobe, FaLinkedin, FaTwitter, FaYoutube } from 'react-icons/fa';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-columns">
          <div className="footer-brand">
            <h3>RecruifyAi</h3>
            <p>
              Smart resume parsing, ATS scoring, and AI-driven interviews—built to help teams hire faster and fairer.
            </p>
          </div>

          <div className="footer-column">
            <p className="footer-heading">Product</p>
            <ul>
              <li><Link to="/">Home</Link></li>
              <li><Link to="/upload">Upload Resume</Link></li>
              <li><Link to="/ats-score">ATS Score</Link></li>
              <li><Link to="/interview">AI Interview</Link></li>
            </ul>
          </div>

          <div className="footer-column">
            <p className="footer-heading">Resources</p>
            <ul>
              <li><a href="/">Company</a></li>
              <li><a href="/">Blogs</a></li>
              <li><a href="/">Community</a></li>
              <li>
                <a href="/">
                  Careers <span className="footer-chip">We’re hiring!</span>
                </a>
              </li>
              <li><a href="/">About</a></li>
            </ul>
          </div>

          <div className="footer-column">
            <p className="footer-heading">Legal</p>
            <ul>
              <li><a href="/">Privacy</a></li>
              <li><a href="/">Terms</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-aside">
          <p className="footer-tagline">
            Making every customer feel valued—no matter the size of your audience.
          </p>

          <div className="footer-socials">
            <span className="footer-social-button" aria-label="Website">
              <FaGlobe className="footer-social-icon" />
            </span>
            <span className="footer-social-button" aria-label="LinkedIn">
              <FaLinkedin className="footer-social-icon" />
            </span>
            <span className="footer-social-button" aria-label="Twitter">
              <FaTwitter className="footer-social-icon" />
            </span>
            <span className="footer-social-button" aria-label="YouTube">
              <FaYoutube className="footer-social-icon" />
            </span>
          </div>

          <p className="footer-copy">© 2025 RecruifyAi</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

