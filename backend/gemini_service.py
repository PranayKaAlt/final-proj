"""
Gemini AI Service for enhanced resume parsing, question generation, and feedback
"""
import os
import json
import google.generativeai as genai
from typing import List, Dict, Optional, Tuple

# Try to load from .env file if python-dotenv is available (for local development)
try:
    from dotenv import load_dotenv
    # Try loading from multiple locations
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(backend_dir)
    current_dir = os.getcwd()
    
    # Try loading from different locations (in order of preference)
    env_paths = [
        os.path.join(backend_dir, '.env'),      # backend/.env
        os.path.join(parent_dir, '.env'),       # root/.env
        os.path.join(current_dir, '.env'),      # current directory/.env
        '.env'                                   # relative path
    ]
    
    # Try loading from each path (load_dotenv will skip if file doesn't exist)
    loaded_any = False
    for env_path in env_paths:
        if os.path.exists(env_path):
            result = load_dotenv(env_path, override=True)  # Use override=True to ensure it loads
            if result:
                print(f"✅ Loaded .env from: {env_path}")
                loaded_any = True
    
    # Also try default load_dotenv() which searches current directory and parents
    if not loaded_any:
        result = load_dotenv(override=True)
        if result:
            print("✅ Loaded .env using default search")
except ImportError:
    print("⚠️  python-dotenv not installed - install it with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Error loading .env file: {e}")

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print(f"✅ Gemini API key configured (length: {len(GEMINI_API_KEY)} characters)")
else:
    print("⚠️  GEMINI_API_KEY not found in environment")
    print("   Please set GEMINI_API_KEY in your .env file or environment variables")

# Use Gemini 1.5 Flash model
MODEL_NAME = 'gemini-2.5-flash-lite'

def get_gemini_model():
    """Get the Gemini model instance"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return genai.GenerativeModel(MODEL_NAME)

def analyze_resume_with_gemini(resume_text: str, selected_role: str) -> Dict:
    """
    Analyze resume using Gemini for better ATS scoring and parsing
    
    Returns:
        Dict with ats_score, predicted_role, skills, and detailed analysis
    """
    try:
        model = get_gemini_model()
        
        # Limit text to avoid token limits
        resume_text_limited = resume_text[:4000]
        
        prompt = f"""You are an expert ATS (Applicant Tracking System) analyzer for recruiting. 
Analyze the following resume for a {selected_role} position.

Resume Text:
{resume_text_limited}

Provide a comprehensive analysis in JSON format with the following structure:
{{
    "ats_score": <integer 0-100>,  // Overall ATS compatibility score
    "predicted_role": "<job role>",  // Best matching role from the resume
    "skills": ["skill1", "skill2", "skill3"],  // Top 5 relevant technical skills
    "strengths": ["strength1", "strength2"],  // Key strengths for this role
    "weaknesses": ["weakness1", "weakness2"],  // Areas for improvement
    "keyword_match": <integer 0-100>,  // How well keywords match the role
    "experience_level": "<junior/mid/senior>",  // Estimated experience level
    "recommendation": "<brief recommendation text>"
}}

Focus on:
- Technical skills relevant to {selected_role}
- Experience alignment with role requirements
- Keyword matching with job description
- Overall candidate fit

Return ONLY valid JSON, no additional text."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response text (remove markdown code blocks if present)
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        
        # Ensure required fields exist
        return {
            'ats_score': int(result.get('ats_score', 0)),
            'predicted_role': result.get('predicted_role', selected_role),
            'skills': result.get('skills', [])[:5],
            'strengths': result.get('strengths', []),
            'weaknesses': result.get('weaknesses', []),
            'keyword_match': int(result.get('keyword_match', 0)),
            'experience_level': result.get('experience_level', 'mid'),
            'recommendation': result.get('recommendation', '')
        }
    except Exception as e:
        print(f"Error in Gemini resume analysis: {e}")
        # Fallback to basic analysis
        return None

def generate_interview_questions_with_gemini(resume_text: str, selected_role: str, skills: List[str]) -> List[str]:
    """
    Generate intelligent interview questions using Gemini
    
    Args:
        resume_text: Extracted resume text
        selected_role: Target job role
        skills: Extracted skills from resume
    
    Returns:
        List of 5 interview questions
    """
    try:
        model = get_gemini_model()
        
        skills_text = ", ".join(skills[:5]) if skills else "Not specified"
        
        # Limit resume text to avoid token limits
        resume_text_limited = resume_text[:2000]
        
        prompt = f"""You are an expert technical interviewer for {selected_role} positions.
Generate 5 high-quality, role-specific interview questions based on the candidate's resume.

Resume Summary:
{resume_text_limited}

Candidate Skills: {skills_text}
Target Role: {selected_role}

Generate 5 questions that:
1. Test technical knowledge relevant to {selected_role}
2. Are specific to the candidate's experience and skills
3. Include behavioral and situational questions
4. Progress from basic to more advanced concepts
5. Are practical and job-relevant

Return ONLY a JSON array of 5 questions in this format:
["question1", "question2", "question3", "question4", "question5"]

Each question should be clear, specific, and allow candidates to demonstrate their skills.
No additional text, only the JSON array."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response text
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        questions = json.loads(response_text)
        
        # Ensure we have exactly 5 questions
        if isinstance(questions, list) and len(questions) >= 5:
            return questions[:5]
        elif isinstance(questions, list):
            return questions
        else:
            return []
    except Exception as e:
        print(f"Error in Gemini question generation: {e}")
        return None

def analyze_answer_with_gemini(question: str, answer: str, selected_role: str, context: Optional[Dict] = None) -> Dict:
    """
    Analyze interview answer using Gemini for detailed feedback
    
    Args:
        question: The interview question asked
        answer: Candidate's answer
        selected_role: Target job role
        context: Optional context (resume info, previous answers, etc.)
    
    Returns:
        Dict with score (0-10), detailed feedback, and analysis
    """
    try:
        model = get_gemini_model()
        
        context_info = ""
        if context:
            skills = context.get('skills', [])
            if skills:
                context_info = f"Candidate Skills: {', '.join(skills[:5])}\n"
        
        prompt = f"""You are an expert interviewer evaluating a candidate's answer for a {selected_role} position.

Question: {question}

Candidate's Answer: {answer}

{context_info}
Evaluate this answer and provide:
1. A numerical score from 0 to 10 (where 10 is excellent)
2. Detailed feedback on what was good and what could be improved
3. Assessment of technical accuracy
4. Assessment of communication clarity
5. Suggestions for improvement

Return ONLY a JSON object in this format:
{{
    "score": <float 0-10>,
    "feedback": "<detailed feedback text>",
    "technical_accuracy": "<assessment>",
    "communication_clarity": "<assessment>",
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "overall_assessment": "<brief overall assessment>"
}}

Be constructive and specific in your feedback. Focus on actionable insights.
Return ONLY valid JSON, no additional text."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response text
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        
        score = float(result.get('score', 5.0))
        # Ensure score is between 0-10
        score = max(0, min(10, score))
        
        return {
            'score': round(score, 2),
            'feedback': result.get('feedback', 'Good answer, but could be more detailed.'),
            'technical_accuracy': result.get('technical_accuracy', 'Moderate'),
            'communication_clarity': result.get('communication_clarity', 'Moderate'),
            'strengths': result.get('strengths', []),
            'improvements': result.get('improvements', []),
            'overall_assessment': result.get('overall_assessment', '')
        }
    except Exception as e:
        print(f"Error in Gemini answer analysis: {e}")
        return None

def is_gemini_available() -> bool:
    """Check if Gemini API is available"""
    return GEMINI_API_KEY is not None and GEMINI_API_KEY.strip() != ""

