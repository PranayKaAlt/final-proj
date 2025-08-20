import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

# 1. Load and prepare data
df = pd.read_csv("data/resumes.csv")  # Columns: Role, ResumeText, Selected, Skills

# Use ResumeText for vectorization, predict Role
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['ResumeText'])
y = df['Role']

# 2. Train model (multi-class classification)
model = MultinomialNB()
model.fit(X, y)

# 3. Save models
os.makedirs("model", exist_ok=True)
with open("model/tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("model/resume_classifier.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Enhanced resume model trained and saved.")
