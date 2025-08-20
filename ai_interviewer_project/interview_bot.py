from textblob import TextBlob
import pyttsx3
import speech_recognition as sr

def analyze_answer(answer):
    blob = TextBlob(answer)
    polarity = blob.sentiment.polarity
    return polarity

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        answer = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {answer}")
        return answer
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return ""

def run_interview():
    with open("data/interview_questions.txt") as f:
        questions = f.readlines()

    total_score = 0
    for q in questions:
        question = q.strip()
        print(f"❓ {question}")
        speak(question)
        ans = listen()
        score = analyze_answer(ans)
        print(f"🧠 Sentiment score: {score:.2f}")
        total_score += score

    avg_score = total_score / len(questions)
    return avg_score
