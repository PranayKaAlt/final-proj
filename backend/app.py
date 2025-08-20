from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import pickle
import pandas as pd
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import json
from difflib import get_close_matches
import PyPDF2
from io import BytesIO

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables to store session data (in production, use a proper database)
session_data = {}

def load_models():
    """Load the trained AI models"""
    try:
        # First try local directory (for Railway deployment)
        model_path = os.path.join(os.path.dirname(__file__), 'model')
        if not os.path.exists(model_path):
            # Fallback to parent directory (for local development)
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_interviewer_project', 'model')
        
        with open(os.path.join(model_path, 'tfidf_vectorizer.pkl'), 'rb') as f:
            vectorizer = pickle.load(f)
        with open(os.path.join(model_path, 'resume_classifier.pkl'), 'rb') as f:
            model = pickle.load(f)
        return vectorizer, model
    except Exception as e:
        print(f"Error loading models: {e}")
        return None, None

def get_roles():
    """Get available job roles from question templates"""
    try:
        # First try local directory (for Railway deployment)
        templates_path = os.path.join(os.path.dirname(__file__), 'data', 'question_templates.json')
        if not os.path.exists(templates_path):
            # Fallback to parent directory (for local development)
            templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_interviewer_project', 'data', 'question_templates.json')
        
        with open(templates_path) as f:
            templates = json.load(f)
        return list(templates.keys())
    except Exception as e:
        print(f"Error loading roles: {e}")
        return []

def get_keywords_for_role(role):
    """Get relevant keywords for a specific role"""
    keywords = {
        "Frontend Developer": ["react", "javascript", "html", "css", "frontend", "ui", "web"],
        "Backend Developer": ["python", "django", "rest", "api", "backend", "sql", "database"],
        "DevOps Engineer": ["ci/cd", "docker", "kubernetes", "aws", "devops", "cloud", "infrastructure"],
        "ML Engineer": ["machine learning", "ml", "scikit-learn", "tensorflow", "model", "data pipeline"],
        "Data Scientist": ["python", "pandas", "tableau", "data analysis", "excel", "visualization"],
        "Full Stack Developer": ["full stack", "frontend", "backend", "javascript", "python", "react", "django", "api", "sql", "css", "html"],
        "UI/UX Designer": ["ui", "ux", "design", "figma", "sketch", "adobe xd", "wireframe", "prototype", "user research", "usability", "aesthetics"],
        "Android Developer": ["android", "kotlin", "java", "jetpack", "compose", "xml", "android studio", "mobile", "api", "gradle"],
        "QA Tester": ["qa", "testing", "test case", "automation", "selenium", "regression", "bug", "coverage", "manual", "script"],
        "Project Manager": ["project", "manager", "scrum", "agile", "kanban", "timeline", "stakeholder", "risk", "collaboration", "communication"]
    }
    return keywords.get(role, [])

def ats_score(resume_text, role):
    """Calculate ATS compatibility score using the actual working logic"""
    keywords = get_keywords_for_role(role)
    resume_text_lower = resume_text.lower()
    
    # Tokenize resume text (words and phrases)
    tokens = set(re.findall(r"\b\w+[\w\s\-/\.]*\w*\b", resume_text_lower))
    found = 0
    
    for kw in keywords:
        kw_lower = kw.lower()
        # Direct word/phrase match
        if any(kw_lower in token for token in tokens):
            found += 1
            continue
        # Fuzzy match (for typos, plurals, etc.)
        close = get_close_matches(kw_lower, tokens, n=1, cutoff=0.85)
        if close:
            found += 1
    
    return int(100 * found / len(keywords)) if keywords else 0

def extract_skills(resume_text, role):
    """Extract skills from resume text using the actual working logic"""
    role_keywords = set(get_keywords_for_role(role))
    
    # Basic word extraction
    words = re.findall(r"\b\w+\b", resume_text.lower())
    freq = {}
    for w in words:
        if len(w) > 2:
            freq[w] = freq.get(w, 0) + 1
    
    # Top N frequent words not in stopwords
    stopwords = set(["the", "and", "for", "with", "you", "are", "but", "all", "can", "has", "have", "from", "that", "this", "was", "will", "your", "not", "use", "our", "who", "his", "her", "she", "him", "their", "they", "them", "its", "it's", "had", "been", "were", "which", "what", "how", "why", "when", "where", "also", "more", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"])
    top_resume_skills = [w for w, c in sorted(freq.items(), key=lambda x: -x[1]) if w not in stopwords and not w.isdigit()][:10]
    
    # Combine role keywords and resume skills
    combined = list(role_keywords) + [w for w in top_resume_skills if w not in role_keywords]
    return combined[:5]

def generate_questions(resume_text, selected_role):
    """Generate role-specific questions using the actual working logic"""
    try:
        # First try local directory (for Railway deployment)
        templates_path = os.path.join(os.path.dirname(__file__), 'data', 'question_templates.json')
        if not os.path.exists(templates_path):
            # Fallback to parent directory (for local development)
            templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_interviewer_project', 'data', 'question_templates.json')
        
        with open(templates_path) as f:
            templates = json.load(f)
        
        role_templates = templates.get(selected_role, [])
        skills = extract_skills(resume_text, selected_role)
        questions = []
        used_skills = set()
        
        for tmpl in role_templates:
            if "{skill}" in tmpl and skills:
                for skill in skills:
                    if skill not in used_skills:
                        questions.append(tmpl.replace("{skill}", skill))
                        used_skills.add(skill)
                        break
            else:
                questions.append(tmpl)
            if len(questions) >= 5:
                break
        
        return questions[:5]
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def analyze_answer(answer, role):
    """Analyze interview answer using the actual working logic"""
    # Length score
    length_score = min(len(answer.split()) / 20, 1.0)  # 20+ words = full score
    
    # Relevance score (keyword overlap)
    keywords = get_keywords_for_role(role)
    overlap = sum(1 for kw in keywords if kw.lower() in answer.lower())
    relevance_score = overlap / len(keywords) if keywords else 0
    
    # Clarity (sentiment)
    polarity = TextBlob(answer).sentiment.polarity
    clarity_score = (polarity + 1) / 2  # scale to 0-1
    
    # Weighted sum
    total = 0.4 * length_score + 0.4 * relevance_score + 0.2 * clarity_score
    return total, length_score, relevance_score, clarity_score

def final_decision(predicted_role, selected_role, ats, interview, ats_thr=60, int_thr=0.5):
    """Make final decision using the actual working logic"""
    reasons = []
    
    if predicted_role == selected_role:
        reasons.append(f"Strong {selected_role.lower()} skills")
    else:
        reasons.append(f"Resume does not match the selected role ({selected_role})")
    
    if ats >= ats_thr:
        reasons.append("Good ATS match")
    else:
        reasons.append("Low ATS compatibility")
    
    if interview > int_thr:
        reasons.append("Good communication/confidence")
    else:
        reasons.append("Low confidence in communication")
    
    # Decision logic
    if predicted_role == selected_role and ats >= ats_thr and interview > int_thr:
        result = "✅ Selected"
    elif ats >= ats_thr - 10 and interview > int_thr - 0.1:
        result = "🟡 On Hold"
    else:
        result = "❌ Rejected"
    
    return result, "; ".join(reasons)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file):
    """Extract text from PDF file using the actual working logic"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """Handle resume upload and analysis using the actual working AI logic"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        candidate_name = request.form.get('candidate_name', '')
        selected_role = request.form.get('selected_role', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        if not candidate_name or not selected_role:
            return jsonify({'error': 'Candidate name and role are required'}), 400
        
        # Extract text from PDF using the actual working logic
        resume_text = extract_text_from_pdf(file)
        if not resume_text.strip():
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        # Load models and predict role using the actual working AI models
        vectorizer, model = load_models()
        if vectorizer is None or model is None:
            return jsonify({'error': 'AI models not available'}), 500
        
        # Predict role using the actual trained model
        X = vectorizer.transform([resume_text])
        predicted_role = model.predict(X)[0]
        
        # Calculate ATS score using the actual working logic
        ats_score_value = ats_score(resume_text, selected_role)
        
        # Extract skills using the actual working logic
        skills = extract_skills(resume_text, selected_role)
        
        # Store data for later use (in production, use a proper database)
        session_key = f"{candidate_name}_{selected_role}"
        session_data[session_key] = {
            'candidate_name': candidate_name,
            'selected_role': selected_role,
            'predicted_role': predicted_role,
            'ats_score': ats_score_value,
            'resume_text': resume_text,
            'skills': skills
        }
        
        return jsonify({
            'candidate_name': candidate_name,
            'selected_role': selected_role,
            'predicted_role': predicted_role,
            'ats_score': ats_score_value,
            'skills': skills,
            'message': 'Resume analyzed successfully using AI models'
        })
        
    except Exception as e:
        print(f"Error processing resume: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/interview-questions', methods=['POST'])
def get_interview_questions():
    """Get AI-generated interview questions using the actual working logic"""
    try:
        data = request.get_json()
        candidate_name = data.get('candidate_name')
        selected_role = data.get('selected_role')
        
        if not candidate_name or not selected_role:
            return jsonify({'error': 'Candidate name and role are required'}), 400
        
        session_key = f"{candidate_name}_{selected_role}"
        if session_key not in session_data:
            return jsonify({'error': 'Resume not found. Please upload resume first.'}), 400
        
        resume_text = session_data[session_key]['resume_text']
        
        # Generate questions using the actual working logic
        questions = generate_questions(resume_text, selected_role)
        
        return jsonify({
            'questions': questions,
            'total_questions': len(questions)
        })
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Submit and analyze interview answer using the actual working logic"""
    try:
        data = request.get_json()
        candidate_name = data.get('candidate_name')
        selected_role = data.get('selected_role')
        question = data.get('question')
        answer = data.get('answer')
        question_index = data.get('question_index')
        
        if not all([candidate_name, selected_role, question, answer, question_index is not None]):
            return jsonify({'error': 'All fields are required'}), 400
        
        session_key = f"{candidate_name}_{selected_role}"
        if session_key not in session_data:
            return jsonify({'error': 'Resume not found. Please upload resume first.'}), 400
        
        # Analyze answer using the actual working logic
        score, length_score, relevance_score, clarity_score = analyze_answer(answer, selected_role)
        score10 = round(score * 10, 2)
        
        # Generate feedback using the actual working logic
        feedback = []
        if length_score < 0.5:
            feedback.append("Try to give a more detailed answer.")
        if relevance_score < 0.5:
            feedback.append("Include more relevant technical keywords.")
        if clarity_score > 0.7:
            feedback.append("Answer was confident and clear.")
        elif clarity_score < 0.3:
            feedback.append("Try to sound more positive and clear.")
        
        feedback_text = " ".join(feedback) if feedback else "Good answer!"
        
        # Store answer in session
        if 'interview_answers' not in session_data[session_key]:
            session_data[session_key]['interview_answers'] = []
        
        session_data[session_key]['interview_answers'].append({
            'question': question,
            'answer': answer,
            'score': score10,
            'sentiment': round(clarity_score, 2),
            'length': round(length_score, 2),
            'relevance': round(relevance_score, 2),
            'feedback': feedback_text
        })
        
        return jsonify({
            'score': score10,
            'feedback': feedback_text,
            'analysis': {
                'length_score': round(length_score, 2),
                'relevance_score': round(relevance_score, 2),
                'clarity_score': round(clarity_score, 2)
            }
        })
        
    except Exception as e:
        print(f"Error analyzing answer: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/interview-results', methods=['POST'])
def get_interview_results():
    """Get complete interview results using the actual working logic"""
    try:
        data = request.get_json()
        candidate_name = data.get('candidate_name')
        selected_role = data.get('selected_role')
        
        if not candidate_name or not selected_role:
            return jsonify({'error': 'Candidate name and role are required'}), 400
        
        session_key = f"{candidate_name}_{selected_role}"
        if session_key not in session_data:
            return jsonify({'error': 'Resume not found. Please upload resume first.'}), 400
        
        session_info = session_data[session_key]
        interview_answers = session_info.get('interview_answers', [])
        
        if not interview_answers:
            return jsonify({'error': 'No interview answers found'}), 400
        
        # Calculate average interview score
        avg_score = sum([item["score"] for item in interview_answers]) / len(interview_answers)
        
        # Get final decision using the actual working logic
        result, reasons = final_decision(
            session_info['predicted_role'],
            session_info['selected_role'],
            session_info['ats_score'],
            avg_score / 10  # Convert to 0-1 scale
        )
        
        return jsonify({
            'candidate_name': candidate_name,
            'selected_role': selected_role,
            'predicted_role': session_info['predicted_role'],
            'ats_score': session_info['ats_score'],
            'interview_score': round(avg_score, 2),
            'final_decision': result,
            'reasons': reasons,
            'interview_details': interview_answers,
            'skills': session_info.get('skills', [])
        })
        
    except Exception as e:
        print(f"Error getting results: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'AI Recruitment System API is running'})

@app.route('/api/roles', methods=['GET'])
def get_roles_endpoint():
    """Get available job roles"""
    roles = get_roles()
    return jsonify({'roles': roles})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting AI Recruitment System API...")
    print(f"API will be available at: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port) 