import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import os
import json
import re
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

class EnhancedResumeTrainer:
    def __init__(self):
        self.models = {}
        self.vectorizers = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        
    def create_sample_dataset(self, num_samples=1000):
        """Create a comprehensive sample dataset for demonstration"""
        print("🔄 Creating enhanced sample dataset...")
        
        # Sample data structure
        roles = [
            'Frontend Developer', 'Backend Developer', 'Full Stack Developer',
            'Data Scientist', 'ML Engineer', 'DevOps Engineer', 'UI/UX Designer',
            'Android Developer', 'QA Tester', 'Project Manager', 'Product Manager',
            'Data Engineer', 'Cloud Architect', 'Security Engineer', 'Mobile Developer'
        ]
        
        industries = ['Technology', 'Healthcare', 'Finance', 'Education', 'E-commerce', 'Manufacturing']
        experience_levels = ['Entry', 'Junior', 'Mid', 'Senior', 'Lead', 'Principal']
        
        data = []
        
        for i in range(num_samples):
            role = np.random.choice(roles)
            industry = np.random.choice(industries)
            exp_level = np.random.choice(experience_levels)
            
            # Generate realistic resume content based on role
            resume_content = self._generate_role_specific_content(role, exp_level)
            
            # Generate comprehensive features
            sample = {
                'id': i + 1,
                'role': role,
                'industry': industry,
                'experience_level': exp_level,
                'years_experience': np.random.randint(0, 15),
                'education_level': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD']),
                'resume_text': resume_content,
                'technical_skills': self._extract_skills_from_text(resume_content),
                'project_count': np.random.randint(1, 10),
                'certification_count': np.random.randint(0, 5),
                'github_projects': np.random.randint(0, 20),
                'salary_expectation': np.random.randint(30000, 150000),
                'location': np.random.choice(['Remote', 'On-site', 'Hybrid']),
                'selected': np.random.choice([True, False], p=[0.3, 0.7]),  # 30% selection rate
                'interview_score': np.random.uniform(0.3, 1.0),
                'ats_score': np.random.randint(40, 95),
                'culture_fit_score': np.random.uniform(0.4, 1.0)
            }
            data.append(sample)
        
        df = pd.DataFrame(data)
        df.to_csv('data/enhanced_resumes.csv', index=False)
        print(f"✅ Created enhanced dataset with {num_samples} samples")
        return df
    
    def _generate_role_specific_content(self, role, exp_level):
        """Generate realistic resume content based on role and experience"""
        role_keywords = {
            'Frontend Developer': ['React', 'JavaScript', 'HTML', 'CSS', 'Vue.js', 'Angular', 'TypeScript'],
            'Backend Developer': ['Python', 'Django', 'Node.js', 'Java', 'Spring', 'SQL', 'PostgreSQL'],
            'Data Scientist': ['Python', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'SQL', 'Tableau'],
            'ML Engineer': ['Python', 'TensorFlow', 'PyTorch', 'MLOps', 'Docker', 'Kubernetes', 'AWS'],
            'DevOps Engineer': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Jenkins', 'Terraform', 'Ansible']
        }
        
        keywords = role_keywords.get(role, ['Python', 'JavaScript', 'SQL'])
        exp_multiplier = {'Entry': 1, 'Junior': 2, 'Mid': 3, 'Senior': 4, 'Lead': 5, 'Principal': 6}
        
        content = f"Experienced {role} with {exp_multiplier[exp_level]} years in software development. "
        content += f"Proficient in {', '.join(np.random.choice(keywords, size=min(4, len(keywords)), replace=False))}. "
        content += "Led multiple projects and collaborated with cross-functional teams. "
        content += "Strong problem-solving skills and ability to work in agile environments."
        
        return content
    
    def _extract_skills_from_text(self, text):
        """Extract skills from resume text"""
        skills = re.findall(r'\b[A-Z][a-z]+(?:\.[A-Z][a-z]+)*\b', text)
        return list(set(skills))[:8]
    
    def load_and_preprocess_data(self, filepath='data/enhanced_resumes.csv'):
        """Load and preprocess the enhanced dataset"""
        print("🔄 Loading and preprocessing data...")
        
        if not os.path.exists(filepath):
            print("📊 Dataset not found, creating sample dataset...")
            df = self.create_sample_dataset()
        else:
            df = pd.read_csv(filepath)
        
        # Text preprocessing
        df['resume_text_clean'] = df['resume_text'].apply(self._clean_text)
        
        # Feature engineering
        df['text_length'] = df['resume_text'].str.len()
        df['word_count'] = df['resume_text'].str.split().str.len()
        df['skill_diversity'] = df['technical_skills'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        
        # Sentiment analysis
        df['sentiment_score'] = df['resume_text'].apply(lambda x: TextBlob(x).sentiment.polarity)
        
        print(f"✅ Loaded {len(df)} resumes with {len(df.columns)} features")
        return df
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def create_advanced_features(self, df):
        """Create advanced features for ML models"""
        print("🔧 Creating advanced features...")
        
        # TF-IDF for resume text
        tfidf = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
        tfidf_features = tfidf.fit_transform(df['resume_text_clean'])
        self.vectorizers['tfidf'] = tfidf
        
        # Numerical features
        numerical_features = [
            'years_experience', 'project_count', 'certification_count',
            'github_projects', 'text_length', 'word_count', 'skill_diversity',
            'sentiment_score'
        ]
        
        # Categorical features
        categorical_features = ['industry', 'experience_level', 'education_level', 'location']
        
        # Encode categorical variables
        for feature in categorical_features:
            le = LabelEncoder()
            df[f'{feature}_encoded'] = le.fit_transform(df[feature].astype(str))
            self.label_encoders[feature] = le
        
        # Combine all features
        numerical_data = df[numerical_features].values
        categorical_data = df[[f'{f}_encoded' for f in categorical_features]].values
        
        # Scale numerical features
        scaler = StandardScaler()
        numerical_scaled = scaler.fit_transform(numerical_data)
        self.scalers['numerical'] = scaler
        
        # Combine features
        X_combined = np.hstack([tfidf_features.toarray(), numerical_scaled, categorical_data])
        
        print(f"✅ Created feature matrix with shape: {X_combined.shape}")
        return X_combined
    
    def train_ensemble_models(self, X, y):
        """Train multiple ML models and create ensemble"""
        print("🤖 Training ensemble models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Define models
        models = {
            'naive_bayes': MultinomialNB(),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(random_state=42),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000)
        }
        
        # Train each model
        for name, model in models.items():
            print(f"🔄 Training {name}...")
            
            if name == 'naive_bayes':
                # Naive Bayes works better with non-negative features
                X_train_nb = X_train.copy()
                X_train_nb[X_train_nb < 0] = 0
                X_test_nb = X_test.copy()
                X_test_nb[X_test_nb < 0] = 0
                
                model.fit(X_train_nb, y_train)
                y_pred = model.predict(X_test_nb)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Evaluate model
            accuracy = accuracy_score(y_test, y_pred)
            print(f"   {name} accuracy: {accuracy:.4f}")
            
            # Store model and feature importance
            self.models[name] = model
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = model.feature_importances_
        
        # Create ensemble prediction
        ensemble_pred = self._ensemble_predict(X_test)
        ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
        print(f"🎯 Ensemble accuracy: {ensemble_accuracy:.4f}")
        
        return X_test, y_test
    
    def _ensemble_predict(self, X):
        """Make ensemble predictions"""
        predictions = []
        weights = {'naive_bayes': 0.2, 'random_forest': 0.3, 'gradient_boosting': 0.3, 'logistic_regression': 0.2}
        
        for name, model in self.models.items():
            # Skip tuned models in ensemble prediction
            if name == 'random_forest_tuned':
                continue
                
            if name == 'naive_bayes':
                X_nb = X.copy()
                X_nb[X_nb < 0] = 0
                pred = model.predict_proba(X_nb)[:, 1]
            else:
                pred = model.predict_proba(X)[:, 1]
            predictions.append(pred * weights[name])
        
        ensemble_pred = np.sum(predictions, axis=0)
        return (ensemble_pred > 0.5).astype(int)
    
    def hyperparameter_tuning(self, X, y):
        """Perform hyperparameter tuning for best models"""
        print("🔍 Performing hyperparameter tuning...")
        
        # Random Forest tuning
        rf_params = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10]
        }
        
        rf_grid = GridSearchCV(RandomForestClassifier(random_state=42), rf_params, cv=5, scoring='accuracy')
        rf_grid.fit(X, y)
        
        print(f"✅ Best Random Forest params: {rf_grid.best_params_}")
        print(f"   Best score: {rf_grid.best_score_:.4f}")
        
        # Update with best model
        self.models['random_forest_tuned'] = rf_grid.best_estimator_
    
    def save_models(self):
        """Save all trained models and preprocessing objects"""
        print("💾 Saving models and preprocessing objects...")
        
        os.makedirs("model", exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            with open(f"model/{name}.pkl", "wb") as f:
                pickle.dump(model, f)
        
        # Save vectorizers
        for name, vectorizer in self.vectorizers.items():
            with open(f"model/{name}.pkl", "wb") as f:
                pickle.dump(vectorizer, f)
        
        # Save scalers
        for name, scaler in self.scalers.items():
            with open(f"model/{name}.pkl", "wb") as f:
                pickle.dump(scaler, f)
        
        # Save label encoders
        for name, encoder in self.label_encoders.items():
            with open(f"model/{name}_encoder.pkl", "wb") as f:
                pickle.dump(encoder, f)
        
        # Save feature importance
        with open("model/feature_importance.json", "w") as f:
            json.dump({k: v.tolist() if hasattr(v, 'tolist') else v for k, v in self.feature_importance.items()}, f)
        
        print("✅ All models and objects saved successfully!")
    
    def generate_training_report(self, X_test, y_test):
        """Generate comprehensive training report"""
        print("📊 Generating training report...")
        
        report = {
            'dataset_info': {
                'total_samples': len(X_test) * 5,  # Approximate total
                'features': X_test.shape[1],
                'test_samples': len(X_test)
            },
            'model_performance': {},
            'ensemble_performance': {}
        }
        
        # Individual model performance
        for name, model in self.models.items():
            if name == 'random_forest_tuned':
                continue
                
            if name == 'naive_bayes':
                X_test_nb = X_test.copy()
                X_test_nb[X_test_nb < 0] = 0
                y_pred = model.predict(X_test_nb)
            else:
                y_pred = model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            report['model_performance'][name] = {
                'accuracy': accuracy,
                'classification_report': classification_report(y_test, y_pred, output_dict=True)
            }
        
        # Ensemble performance
        ensemble_pred = self._ensemble_predict(X_test)
        ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
        report['ensemble_performance'] = {
            'accuracy': ensemble_accuracy,
            'classification_report': classification_report(y_test, ensemble_pred, output_dict=True)
        }
        
        # Save report
        with open("model/training_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("✅ Training report generated and saved!")
        return report

def main():
    """Main training pipeline"""
    print("🚀 Starting Enhanced Resume Training Pipeline...")
    
    # Initialize trainer
    trainer = EnhancedResumeTrainer()
    
    # Load and preprocess data
    df = trainer.load_and_preprocess_data()
    
    # Create advanced features
    X = trainer.create_advanced_features(df)
    y = df['selected'].values
    
    # Train models
    X_test, y_test = trainer.train_ensemble_models(X, y)
    
    # Hyperparameter tuning
    trainer.hyperparameter_tuning(X, y)
    
    # Save models
    trainer.save_models()
    
    # Generate report
    report = trainer.generate_training_report(X_test, y_test)
    
    print("\n🎉 Enhanced Training Pipeline Complete!")
    print(f"📊 Final Ensemble Accuracy: {report['ensemble_performance']['accuracy']:.4f}")
    print("💾 Models saved in 'model/' directory")
    print("📋 Training report saved as 'model/training_report.json'")

if __name__ == "__main__":
    main() 