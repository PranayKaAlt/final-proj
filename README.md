# AI-Powered Recruitment System

A modern, full-stack recruitment system that combines React frontend with Python AI backend for intelligent resume screening, candidate matching, and AI-powered interviews.

## 🚀 Features

- **AI Resume Analysis**: Intelligent parsing and role prediction using machine learning
- **ATS Compatibility Scoring**: Automated tracking system compatibility evaluation
- **Interactive AI Interviewer**: Role-specific questions with real-time evaluation
- **Modern React UI**: Beautiful, responsive interface with drag-and-drop resume upload
- **Comprehensive Analytics**: Detailed scoring, feedback, and performance insights
- **PDF Report Generation**: Automated report creation for candidates and recruiters

## 🏗️ Architecture

```
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.js          # Main application
│   │   └── index.js        # Entry point
│   └── package.json        # Frontend dependencies
├── backend/                 # Python Flask API
│   ├── app.py              # Main API server
│   └── requirements.txt    # Python dependencies
└── ai_interviewer_project/ # Original ML models and data
```

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **Styled Components** - CSS-in-JS styling
- **Recharts** - Data visualization
- **React Dropzone** - File upload handling
- **Framer Motion** - Animations and transitions

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **scikit-learn** - Machine learning algorithms
- **PyPDF2** - PDF text extraction
- **TextBlob** - Natural language processing

### AI/ML
- **TF-IDF Vectorization** - Text feature extraction
- **Naive Bayes Classification** - Role prediction
- **NLP Processing** - Text analysis and scoring

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **pip** (Python package manager)
- **npm** or **yarn** (Node package manager)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone khud_ki_bana
cd haha
```

### 2. Setup Backend (Python)
```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend API will be available at `http://localhost:5000`

### 3. Setup Frontend (React)
```bash
# In a new terminal
npm install
npm start
```

The React app will be available at `http://localhost:3000`

## 📁 Project Structure

### Frontend Components
- **Home**: Landing page with feature overview
- **ResumeUpload**: Drag-and-drop resume upload with AI analysis
- **Interview**: Interactive AI interview session
- **Results**: Comprehensive results and analytics dashboard
- **Navbar**: Navigation component with routing

### Backend API Endpoints
- `POST /api/upload-resume` - Resume upload and analysis
- `GET /api/roles` - Available job roles
- `GET /api/health` - Health check endpoint

### AI Models
- **Resume Classifier**: Trained on role-specific data
- **TF-IDF Vectorizer**: Text feature extraction
- **Question Templates**: Role-specific interview questions

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
```

### Model Training
To retrain the AI models:
```bash
cd ai_interviewer_project
python3 train_resume_model.py
```

## 📊 Usage

### 1. Resume Upload
- Navigate to `/upload`
- Enter candidate name and desired role
- Drag and drop PDF resume
- View AI analysis results

### 2. AI Interview
- Start interview session
- Answer role-specific questions
- Receive real-time feedback
- Complete assessment

### 3. Results Analysis
- View comprehensive scoring
- Analyze skills breakdown
- Download detailed reports
- Review recommendations

## 🎨 Customization

### Styling
- Modify `src/index.css` for global styles
- Update component-specific CSS files
- Customize color schemes in CSS variables

### Questions
- Edit `ai_interviewer_project/data/question_templates.json`
- Add new job roles and questions
- Customize scoring algorithms

### AI Models
- Modify `backend/app.py` for custom analysis
- Update keyword matching in `get_keywords_for_role()`
- Enhance scoring algorithms

## 🚀 Deployment

### **Simple Deployment (Recommended)**

Your project is configured for easy deployment using:
- **Frontend**: Vercel (React)
- **Backend**: Railway (Python Flask)

See `VERCEL_RAILWAY_DEPLOYMENT.md` for detailed instructions.

### **Quick Deploy Steps:**
1. **Backend**: Deploy to Railway from `backend/` directory
2. **Frontend**: Deploy to Vercel from project root
3. **Configure**: Set environment variables in both platforms

### **Local Development**
```bash
# Start backend
cd backend
python3 app.py

# Start frontend (in another terminal)
npm start
```

### **Production Build**
```bash
# Frontend build
npm run build

# Backend with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔍 Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - Ensure models are trained: `python3 train_resume_model.py`
   - Check file paths in `backend/app.py`

2. **CORS Issues**
   - Verify Flask-CORS is installed
   - Check CORS configuration in backend

3. **PDF Processing Errors**
   - Ensure PyPDF2 is properly installed
   - Check PDF file format compatibility

4. **Frontend Build Issues**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

### Debug Mode
Enable debug mode in backend:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **scikit-learn** for machine learning capabilities
- **React community** for the excellent frontend framework
- **Flask** for the lightweight Python web framework

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section

---

**Built with ❤️ using React and Python** 
