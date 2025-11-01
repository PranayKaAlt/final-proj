// API Configuration
// This file sets the backend API URL
// For local development, create a .env file with REACT_APP_API_URL=http://localhost:5000
// For production, set REACT_APP_API_URL in your deployment platform (Vercel, Netlify, etc.)

const API_URL = process.env.REACT_APP_API_URL || 'https://final-proj-backend-2.onrender.com';

export default API_URL;

