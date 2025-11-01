# Gemini 1.5 Flash Integration

This document describes the Gemini AI integration for enhanced resume parsing, question generation, and feedback analysis.

## Overview

The system now uses Google's Gemini 1.5 Flash model to provide:
- **Enhanced ATS Scoring**: More intelligent resume analysis and ATS compatibility scoring
- **Better Question Generation**: Role-specific, context-aware interview questions
- **Detailed Feedback**: Comprehensive answer analysis with technical and communication insights

## Setup

### 1. Get Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 2. Configure Environment Variable

**For Local Development:**
Create a `.env` file in the backend directory:
```
GEMINI_API_KEY=your_api_key_here
```

**For Production (Railway/Heroku/etc.):**
Set the environment variable:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Install Dependencies
The `google-generativeai` package has been added to `requirements.txt`. Install it:
```bash
cd backend
pip install -r requirements.txt
```

## Features

### 1. Enhanced Resume Analysis (`analyze_resume_with_gemini`)
- Intelligent ATS scoring (0-100)
- Role prediction based on resume content
- Skill extraction relevant to the target role
- Identifies strengths and weaknesses
- Keyword matching analysis
- Experience level assessment
- Personalized recommendations

### 2. Smart Question Generation (`generate_interview_questions_with_gemini`)
- Context-aware questions based on candidate's resume
- Role-specific technical questions
- Behavioral and situational questions
- Progressive difficulty (basic to advanced)
- Personalized to candidate's skills and experience

### 3. Detailed Answer Analysis (`analyze_answer_with_gemini`)
- Comprehensive scoring (0-10 scale)
- Technical accuracy assessment
- Communication clarity evaluation
- Identifies strengths in answers
- Actionable improvement suggestions
- Overall assessment summary

## Fallback Behavior

The system gracefully falls back to traditional methods if:
- Gemini API key is not configured
- API requests fail
- Rate limits are reached

This ensures the system continues to function even without Gemini integration.

## API Changes

### Resume Upload Response
When Gemini is used, additional fields are included:
```json
{
  "ats_score": 85,
  "predicted_role": "Full Stack Developer",
  "skills": ["React", "Python", "Django", "SQL", "REST API"],
  "gemini_analysis": {
    "strengths": [...],
    "weaknesses": [...],
    "experience_level": "mid",
    "recommendation": "..."
  }
}
```

### Answer Analysis Response
When Gemini is used:
```json
{
  "score": 8.5,
  "feedback": "Detailed feedback text...",
  "analysis": {
    "technical_accuracy": "High - demonstrated strong understanding",
    "communication_clarity": "Clear and well-structured",
    "strengths": ["Strong technical knowledge", "Good examples"],
    "improvements": ["Could expand on specific implementation details"],
    "overall_assessment": "Excellent answer demonstrating expertise"
  },
  "analyzed_by": "gemini"
}
```

## Health Check

Check if Gemini is available:
```bash
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "message": "AI Recruitment System API is running",
  "gemini_available": true
}
```

## Model Configuration

- **Model**: `gemini-1.5-flash`
- **Purpose**: Fast, efficient responses for real-time interactions
- **Token Limits**: 
  - Resume analysis: 4000 characters max
  - Question generation: 2000 characters max
  - Answer analysis: Full answer text (handled by API)

## Benefits

1. **Better ATS Scoring**: More accurate assessment of resume compatibility
2. **Personalized Questions**: Questions tailored to each candidate's background
3. **Detailed Feedback**: Actionable insights to help candidates improve
4. **Scalability**: Fast responses suitable for production use
5. **Reliability**: Fallback ensures system always works

## Troubleshooting

### Gemini not working?
1. Check API key is set: `echo $GEMINI_API_KEY`
2. Verify API key is valid
3. Check network connectivity
4. Review server logs for error messages

### Getting errors?
- Check quota limits on Google AI Studio
- Verify API key permissions
- Review error logs in console

## Notes

- The system automatically uses Gemini when available
- Traditional methods are used as fallback
- No code changes needed to switch between modes
- All existing API endpoints remain compatible

