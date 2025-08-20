import streamlit as st
import resume_parser
import pickle
import os
import pandas as pd
import pyttsx3
import speech_recognition as sr
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from fpdf import FPDF

# --- Utility Functions ---
def load_models():
    with open("model/tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open("model/resume_classifier.pkl", "rb") as f:
        model = pickle.load(f)
    return vectorizer, model

def get_roles():
    # Dynamically load all roles from question_templates.json
    import json
    with open("data/question_templates.json") as f:
        templates = json.load(f)
    return list(templates.keys())

def get_keywords_for_role(role):
    keywords = {
        "Frontend Developer": ["react", "javascript", "html", "css", "frontend", "ui", "web"],
        "Backend Developer": ["python", "django", "rest", "api", "backend", "sql", "database"],
        "DevOps Engineer": ["ci/cd", "docker", "kubernetes", "aws", "devops", "cloud", "infrastructure"],
        "ML Engineer": ["machine learning", "ml", "scikit-learn", "tensorflow", "model", "data pipeline"],
        "Data Analyst": ["python", "pandas", "tableau", "data analysis", "excel", "visualization"],
        "Full Stack Developer": ["full stack", "frontend", "backend", "javascript", "python", "react", "django", "api", "sql", "css", "html"],
        "UI/UX Designer": ["ui", "ux", "design", "figma", "sketch", "adobe xd", "wireframe", "prototype", "user research", "usability", "aesthetics"],
        "Android Developer": ["android", "kotlin", "java", "jetpack", "compose", "xml", "android studio", "mobile", "api", "gradle"],
        "QA Tester": ["qa", "testing", "test case", "automation", "selenium", "regression", "bug", "coverage", "manual", "script"],
        "Project Manager": ["project", "manager", "scrum", "agile", "kanban", "timeline", "stakeholder", "risk", "collaboration", "communication"]
    }
    return keywords.get(role, [])

def ats_score(resume_text, role):
    import re
    from difflib import get_close_matches
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

def speak(text):
    # Disabled text-to-speech to avoid system crashes
    st.info(f"🎤 Question: {text}")
    pass

def listen():
    # Disabled speech recognition to avoid system crashes
    st.warning("Speech recognition disabled. Please type your answers.")
    return ""

def analyze_answer(answer, role):
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

import json
import re

def extract_skills(resume_text, role):
    # Use keywords from role and extract top occurring words from resume
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
    # Load question templates
    with open("data/question_templates.json") as f:
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

def run_voice_interview(resume_text, role):
    questions = generate_questions(resume_text, role)
    interview_log = []
    for idx, q in enumerate(questions):
        st.markdown(f"**Question {idx+1}:** {q}")
        speak(q)
        st.info("Please type your answer below:")
        answer = st.text_input(f"Your answer for Question {idx+1}", key=f"answer_{idx}")
        if not answer:
            st.warning("Please provide an answer to continue.")
            st.stop()
        
        score, l, r, c = analyze_answer(answer, role)
        score10 = round(score * 10, 2)
        fb = []
        if l < 0.5:
            fb.append("Try to give a more detailed answer.")
        if r < 0.5:
            fb.append("Include more relevant technical keywords.")
        if c > 0.7:
            fb.append("Answer was confident and clear.")
        elif c < 0.3:
            fb.append("Try to sound more positive and clear.")
        feedback = " ".join(fb) if fb else "Good answer!"
        interview_log.append({
            "question": q,
            "answer": answer,
            "score": score10,
            "sentiment": round(c, 2),
            "length": round(l, 2),
            "relevance": round(r, 2),
            "feedback": feedback
        })
        st.info(f"Score: {score10}/10 | Feedback: {feedback}")
        st.markdown("---")
    avg_score = sum([item["score"] for item in interview_log]) / len(interview_log) if interview_log else 0
    st.success("✅ Interview complete!")
    st.session_state["interview_log"] = interview_log
    st.session_state["interview_score"] = avg_score
    return avg_score, interview_log

def final_decision(predicted_role, selected_role, ats, interview, ats_thr=60, int_thr=0.5):
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

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO

def generate_pdf_report(candidate_name, selected_role, predicted_role, ats, interview, result, reasons):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 30
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, y, "AI Interviewer - Candidate Report")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(30, y, f"Candidate Name: {candidate_name}")
    y -= 18
    c.drawString(30, y, f"Selected Role: {selected_role}")
    y -= 18
    c.drawString(30, y, f"Predicted Role: {predicted_role}")
    y -= 18
    c.drawString(30, y, f"ATS Compatibility Score: {ats}")
    y -= 18
    c.drawString(30, y, f"Interview Score: {interview:.2f}")
    y -= 18
    # Remove emoji from result for PDF
    clean_result = result.replace("✅", "Selected").replace("🟡", "Maybe").replace("❌", "Rejected").replace("🔴", "Rejected").replace("🟢", "Selected")
    c.drawString(30, y, f"Final Decision: {clean_result}")
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, "Key Insights:")
    y -= 16
    c.setFont("Helvetica", 11)
    for line in reasons.split('; '):
        c.drawString(40, y, f"- {line}")
        y -= 14
        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 11)
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# --- Streamlit UI ---
st.set_page_config(page_title="AI Interviewer", layout="centered")
st.title("AI Interviewer")
st.write("Upload your resume, select a role, and start your AI-powered interview!")

role = st.selectbox("Select Role", get_roles())
candidate_name = st.text_input("Your Name")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    temp_path = os.path.join("temp_resume.pdf")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
    resume_text = resume_parser.extract_text_from_pdf(temp_path)
    st.success("Resume uploaded and parsed!")
    # Resume Preview (first 5 lines)
    preview_lines = resume_text.strip().split('\n')[:5]
    st.subheader("Resume Preview (first 5 lines)")
    st.code('\n'.join(preview_lines), language="text")
    # Load models
    vectorizer, model = load_models()
    X = vectorizer.transform([resume_text])
    predicted_role = model.predict(X)[0]
    ats = ats_score(resume_text, role)
    st.write(f"**Predicted Role:** {predicted_role}")
    # Animated ATS Progress Bar
    st.subheader("ATS Compatibility Score")
    st.progress(ats)
    st.write(f"{ats} / 100")
    if st.button("Start Interview"):
        st.session_state["interview_started"] = True
        st.session_state["resume_text"] = resume_text
        st.session_state["predicted_role"] = predicted_role
        st.session_state["ats"] = ats
        st.session_state["candidate_name"] = candidate_name
        st.session_state["selected_role"] = role
else:
    st.session_state["interview_started"] = False

if st.session_state.get("interview_started"):
    st.header("Voice Interview")
    interview_score, interview_log = run_voice_interview(
        st.session_state["resume_text"], st.session_state["selected_role"])
    # Animated Interview Score Progress Bar
    st.subheader("Interview Score")
    st.progress(int(interview_score * 10))
    st.write(f"{interview_score:.2f} / 10.00")
    # Confidence Meter (based on average sentiment)
    if interview_log:
        avg_sentiment = sum([item["sentiment"] for item in interview_log]) / len(interview_log)
        st.subheader("Candidate Confidence Meter")
        st.progress(int(avg_sentiment * 100))
    # Final Decision Badge
    result, reasons = final_decision(
        st.session_state["predicted_role"],
        st.session_state["selected_role"],
        st.session_state["ats"],
        interview_score
    )
    st.subheader("Final Decision")
    if "Selected" in result:
        st.markdown('<span style="color:green;font-size:2em;">🟢 Selected</span>', unsafe_allow_html=True)
    elif "On Hold" in result or "Maybe" in result:
        st.markdown('<span style="color:orange;font-size:2em;">🟡 Maybe</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:red;font-size:2em;">🔴 Rejected</span>', unsafe_allow_html=True)
    st.write(f"**Key Insights:** {reasons}")
    # PDF report
    if st.button("Download PDF Report"):
        pdf_bytes = generate_pdf_report(
            st.session_state["candidate_name"],
            st.session_state["selected_role"],
            st.session_state["predicted_role"],
            st.session_state["ats"],
            interview_score,
            result,
            reasons
        )
        st.download_button(
            label="Download Report as PDF",
            data=pdf_bytes,
            file_name="AI_Interview_Report.pdf",
            mime="application/pdf"
        )
