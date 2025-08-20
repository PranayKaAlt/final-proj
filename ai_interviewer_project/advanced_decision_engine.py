import numpy as np
import json
from textblob import TextBlob
import re
from datetime import datetime

class AdvancedDecisionEngine:
    def __init__(self):
        self.decision_thresholds = {
            'ats_score': 60,
            'interview_score': 0.5,
            'culture_fit': 0.6,
            'skill_match': 0.7,
            'experience_level': 0.6
        }
        
        self.bias_indicators = {
            'gender_bias': False,
            'age_bias': False,
            'location_bias': False,
            'education_bias': False
        }
        
        self.decision_weights = {
            'ats_score': 0.25,
            'interview_score': 0.30,
            'culture_fit': 0.20,
            'skill_match': 0.15,
            'experience_level': 0.10
        }
    
    def calculate_comprehensive_score(self, candidate_data):
        """Calculate comprehensive score across multiple dimensions"""
        scores = {}
        
        # ATS Score (already calculated)
        scores['ats_score'] = candidate_data.get('ats_score', 0) / 100
        
        # Interview Score (already calculated)
        scores['interview_score'] = candidate_data.get('interview_score', 0) / 100
        
        # Culture Fit Score
        scores['culture_fit'] = self._calculate_culture_fit(candidate_data)
        
        # Skill Match Score
        scores['skill_match'] = self._calculate_skill_match(candidate_data)
        
        # Experience Level Score
        scores['experience_level'] = self._calculate_experience_score(candidate_data)
        
        # Calculate weighted final score
        final_score = sum(scores[dim] * self.decision_weights[dim] for dim in scores)
        
        return scores, final_score
    
    def _calculate_culture_fit(self, candidate_data):
        """Calculate culture fit based on communication style and values"""
        interview_answers = candidate_data.get('interview_details', [])
        
        if not interview_answers:
            return 0.5  # Default neutral score
        
        # Analyze communication patterns
        communication_scores = []
        for answer in interview_answers:
            text = answer.get('answer', '')
            if text:
                # Sentiment analysis
                sentiment = TextBlob(text).sentiment.polarity
                # Length appropriateness (not too short, not too long)
                length_score = min(len(text.split()) / 30, 1.0)
                # Professional language detection
                professional_words = ['collaborate', 'team', 'project', 'develop', 'implement', 'optimize']
                professional_score = sum(1 for word in professional_words if word.lower() in text.lower()) / len(professional_words)
                
                # Combine scores
                answer_score = (sentiment + 1) / 2 * 0.4 + length_score * 0.3 + professional_score * 0.3
                communication_scores.append(answer_score)
        
        return np.mean(communication_scores) if communication_scores else 0.5
    
    def _calculate_skill_match(self, candidate_data):
        """Calculate skill match between predicted and desired role"""
        predicted_role = candidate_data.get('predicted_role', '')
        selected_role = candidate_data.get('selected_role', '')
        
        if not predicted_role or not selected_role:
            return 0.5
        
        # Exact match
        if predicted_role == selected_role:
            return 1.0
        
        # Related roles (partial match)
        related_roles = {
            'Frontend Developer': ['Full Stack Developer', 'UI/UX Designer'],
            'Backend Developer': ['Full Stack Developer', 'DevOps Engineer'],
            'Data Scientist': ['ML Engineer', 'Data Engineer'],
            'ML Engineer': ['Data Scientist', 'Data Engineer'],
            'DevOps Engineer': ['Backend Developer', 'Cloud Architect']
        }
        
        if selected_role in related_roles.get(predicted_role, []):
            return 0.8
        
        # Completely different roles
        return 0.3
    
    def _calculate_experience_score(self, candidate_data):
        """Calculate experience level appropriateness"""
        years_experience = candidate_data.get('years_experience', 0)
        selected_role = candidate_data.get('selected_role', '')
        
        # Define expected experience ranges for roles
        role_experience_ranges = {
            'Frontend Developer': (0, 8),
            'Backend Developer': (1, 10),
            'Full Stack Developer': (2, 12),
            'Data Scientist': (1, 10),
            'ML Engineer': (2, 12),
            'DevOps Engineer': (2, 12),
            'UI/UX Designer': (0, 8),
            'Project Manager': (3, 15),
            'Senior Developer': (5, 15),
            'Lead Developer': (7, 20)
        }
        
        expected_range = role_experience_ranges.get(selected_role, (0, 10))
        min_exp, max_exp = expected_range
        
        if years_experience < min_exp:
            return 0.3  # Underqualified
        elif years_experience <= max_exp:
            return 1.0  # Well-qualified
        else:
            return 0.7  # Overqualified but acceptable
    
    def detect_bias(self, candidate_data):
        """Detect potential bias in the decision process"""
        bias_flags = []
        
        # Check for gender bias (if gender info is available)
        if 'gender' in candidate_data:
            # This would require historical data analysis
            pass
        
        # Check for age bias
        if 'years_experience' in candidate_data:
            years = candidate_data['years_experience']
            if years > 20:  # Potential age bias
                bias_flags.append('potential_age_bias')
        
        # Check for location bias
        if 'location' in candidate_data:
            location = candidate_data['location']
            if location == 'Remote':
                # Ensure remote candidates aren't penalized
                pass
        
        # Check for education bias
        if 'education_level' in candidate_data:
            education = candidate_data['education_level']
            if education == 'High School':
                # Ensure non-degree candidates aren't automatically rejected
                pass
        
        return bias_flags
    
    def make_final_decision(self, candidate_data):
        """Make comprehensive final decision with detailed reasoning"""
        # Calculate all scores
        dimension_scores, final_score = self.calculate_comprehensive_score(candidate_data)
        
        # Detect bias
        bias_flags = self.detect_bias(candidate_data)
        
        # Decision logic with multiple thresholds
        decision, reasons = self._evaluate_candidate(dimension_scores, final_score)
        
        # Generate detailed feedback
        feedback = self._generate_detailed_feedback(dimension_scores, bias_flags)
        
        # Calculate confidence level
        confidence = self._calculate_confidence(dimension_scores)
        
        return {
            'decision': decision,
            'final_score': round(final_score * 100, 2),
            'dimension_scores': {k: round(v * 100, 2) for k, v in dimension_scores.items()},
            'reasons': reasons,
            'feedback': feedback,
            'confidence': confidence,
            'bias_flags': bias_flags,
            'timestamp': datetime.now().isoformat()
        }
    
    def _evaluate_candidate(self, dimension_scores, final_score):
        """Evaluate candidate based on multiple dimensions"""
        reasons = []
        
        # Check each dimension
        if dimension_scores['ats_score'] >= self.decision_thresholds['ats_score'] / 100:
            reasons.append("Strong ATS compatibility")
        else:
            reasons.append("Low ATS compatibility - consider keyword optimization")
        
        if dimension_scores['interview_score'] >= self.decision_thresholds['interview_score']:
            reasons.append("Good communication and technical skills demonstrated")
        else:
            reasons.append("Interview performance needs improvement")
        
        if dimension_scores['culture_fit'] >= self.decision_thresholds['culture_fit']:
            reasons.append("Good cultural fit and communication style")
        else:
            reasons.append("Cultural fit may need assessment")
        
        if dimension_scores['skill_match'] >= self.decision_thresholds['skill_match']:
            reasons.append("Skills align well with role requirements")
        else:
            reasons.append("Skills may not fully match role requirements")
        
        if dimension_scores['experience_level'] >= self.decision_thresholds['experience_level']:
            reasons.append("Experience level appropriate for role")
        else:
            reasons.append("Experience level may not match role expectations")
        
        # Final decision logic
        if (final_score >= 0.7 and 
            dimension_scores['ats_score'] >= 0.6 and 
            dimension_scores['interview_score'] >= 0.6):
            decision = "✅ Strongly Recommended"
        elif (final_score >= 0.6 and 
              dimension_scores['ats_score'] >= 0.5 and 
              dimension_scores['interview_score'] >= 0.5):
            decision = "🟡 Recommended"
        elif (final_score >= 0.5 and 
              dimension_scores['ats_score'] >= 0.4 and 
              dimension_scores['interview_score'] >= 0.4):
            decision = "🟡 On Hold - Further Assessment Needed"
        else:
            decision = "❌ Not Recommended"
        
        return decision, reasons
    
    def _generate_detailed_feedback(self, dimension_scores, bias_flags):
        """Generate detailed feedback for improvement"""
        feedback = {
            'strengths': [],
            'areas_for_improvement': [],
            'recommendations': []
        }
        
        # Identify strengths
        for dimension, score in dimension_scores.items():
            if score >= 0.8:
                feedback['strengths'].append(f"Excellent {dimension.replace('_', ' ')}")
            elif score >= 0.6:
                feedback['strengths'].append(f"Good {dimension.replace('_', ' ')}")
        
        # Identify areas for improvement
        for dimension, score in dimension_scores.items():
            if score < 0.5:
                feedback['areas_for_improvement'].append(f"Improve {dimension.replace('_', ' ')}")
        
        # Generate recommendations
        if dimension_scores['ats_score'] < 0.6:
            feedback['recommendations'].append("Optimize resume with relevant keywords")
        
        if dimension_scores['interview_score'] < 0.6:
            feedback['recommendations'].append("Practice technical interview questions")
        
        if dimension_scores['culture_fit'] < 0.6:
            feedback['recommendations'].append("Focus on professional communication")
        
        if dimension_scores['skill_match'] < 0.6:
            feedback['recommendations'].append("Develop skills specific to the role")
        
        # Add bias-related recommendations
        if bias_flags:
            feedback['recommendations'].append("Review decision for potential bias")
        
        return feedback
    
    def _calculate_confidence(self, dimension_scores):
        """Calculate confidence level in the decision"""
        # Higher confidence when all dimensions are consistent
        variance = np.var(list(dimension_scores.values()))
        
        if variance < 0.05:
            confidence = "High"
        elif variance < 0.1:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return confidence
    
    def generate_decision_report(self, candidate_data):
        """Generate comprehensive decision report"""
        decision_result = self.make_final_decision(candidate_data)
        
        report = {
            'candidate_info': {
                'name': candidate_data.get('candidate_name', 'Unknown'),
                'role': candidate_data.get('selected_role', 'Unknown'),
                'predicted_role': candidate_data.get('predicted_role', 'Unknown')
            },
            'decision_summary': decision_result,
            'detailed_analysis': {
                'ats_analysis': self._analyze_ats_score(candidate_data),
                'interview_analysis': self._analyze_interview_performance(candidate_data),
                'skill_analysis': self._analyze_skills(candidate_data)
            },
            'risk_assessment': self._assess_risks(decision_result),
            'next_steps': self._suggest_next_steps(decision_result)
        }
        
        return report
    
    def _analyze_ats_score(self, candidate_data):
        """Analyze ATS score in detail"""
        ats_score = candidate_data.get('ats_score', 0)
        
        if ats_score >= 80:
            return "Excellent ATS compatibility - resume will pass most screening systems"
        elif ats_score >= 60:
            return "Good ATS compatibility - resume should pass most screenings"
        elif ats_score >= 40:
            return "Fair ATS compatibility - some optimization needed"
        else:
            return "Low ATS compatibility - significant optimization required"
    
    def _analyze_interview_performance(self, candidate_data):
        """Analyze interview performance in detail"""
        interview_details = candidate_data.get('interview_details', [])
        
        if not interview_details:
            return "No interview data available"
        
        scores = [answer.get('score', 0) for answer in interview_details]
        avg_score = np.mean(scores)
        
        if avg_score >= 80:
            return f"Strong interview performance (Average: {avg_score:.1f}/100)"
        elif avg_score >= 60:
            return f"Good interview performance (Average: {avg_score:.1f}/100)"
        else:
            return f"Interview performance needs improvement (Average: {avg_score:.1f}/100)"
    
    def _analyze_skills(self, candidate_data):
        """Analyze skills alignment"""
        predicted_role = candidate_data.get('predicted_role', '')
        selected_role = candidate_data.get('selected_role', '')
        
        if predicted_role == selected_role:
            return "Skills perfectly align with selected role"
        elif predicted_role in ['Frontend Developer', 'Backend Developer'] and selected_role == 'Full Stack Developer':
            return "Skills align well with full stack requirements"
        else:
            return f"Skills may not fully align (Predicted: {predicted_role}, Selected: {selected_role})"
    
    def _assess_risks(self, decision_result):
        """Assess risks associated with the decision"""
        risks = []
        
        if decision_result['final_score'] < 60:
            risks.append("Low candidate quality score")
        
        if decision_result['confidence'] == 'Low':
            risks.append("Low confidence in decision")
        
        if decision_result['bias_flags']:
            risks.append("Potential bias detected")
        
        if not risks:
            risks.append("Low risk decision")
        
        return risks
    
    def _suggest_next_steps(self, decision_result):
        """Suggest next steps based on decision"""
        decision = decision_result['decision']
        
        if 'Recommended' in decision:
            return [
                "Schedule follow-up interview with hiring manager",
                "Begin reference checks",
                "Prepare offer letter"
            ]
        elif 'On Hold' in decision:
            return [
                "Schedule additional technical assessment",
                "Request portfolio or work samples",
                "Consider alternative roles"
            ]
        else:
            return [
                "Send polite rejection letter",
                "Keep resume on file for future opportunities",
                "Provide constructive feedback if requested"
            ]

# Example usage
if __name__ == "__main__":
    # Sample candidate data
    sample_candidate = {
        'candidate_name': 'John Doe',
        'selected_role': 'Frontend Developer',
        'predicted_role': 'Frontend Developer',
        'ats_score': 85,
        'interview_score': 78,
        'years_experience': 3,
        'interview_details': [
            {'answer': 'I have experience with React and JavaScript', 'score': 85},
            {'answer': 'I worked on responsive design projects', 'score': 80},
            {'answer': 'I collaborate well with design teams', 'score': 75}
        ]
    }
    
    # Initialize decision engine
    engine = AdvancedDecisionEngine()
    
    # Generate decision report
    report = engine.generate_decision_report(sample_candidate)
    
    # Print results
    print("🎯 Advanced Decision Engine Test")
    print("=" * 50)
    print(f"Decision: {report['decision_summary']['decision']}")
    print(f"Final Score: {report['decision_summary']['final_score']}/100")
    print(f"Confidence: {report['decision_summary']['confidence']}")
    print("\nDetailed Analysis:")
    for key, value in report['detailed_analysis'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}") 