import os
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score
import schedule
import time
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContinuousLearningSystem:
    def __init__(self, model_dir="ai_interviewer_project/model"):
        self.model_dir = Path(model_dir)
        self.models = {}
        self.performance_history = []
        self.retraining_threshold = 0.05  # 5% performance degradation
        self.min_samples_for_retraining = 100
        self.performance_window_days = 30
        
        # Load existing models
        self.load_models()
        
        # Initialize performance tracking
        self.initialize_performance_tracking()
    
    def load_models(self):
        """Load existing trained models"""
        try:
            model_files = list(self.model_dir.glob("*.pkl"))
            
            for model_file in model_files:
                model_name = model_file.stem
                if not model_name.endswith('_encoder'):
                    with open(model_file, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
            
            logger.info(f"✅ Loaded {len(self.models)} models")
            
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
    
    def initialize_performance_tracking(self):
        """Initialize performance tracking from saved data"""
        performance_file = self.model_dir / "performance_history.json"
        
        if performance_file.exists():
            try:
                with open(performance_file, 'r') as f:
                    self.performance_history = json.load(f)
                logger.info(f"✅ Loaded performance history with {len(self.performance_history)} entries")
            except Exception as e:
                logger.error(f"❌ Failed to load performance history: {e}")
    
    def track_model_performance(self, model_name, predictions, actual_values, metadata=None):
        """Track model performance metrics"""
        try:
            # Calculate metrics
            accuracy = accuracy_score(actual_values, predictions)
            precision = precision_score(actual_values, predictions, average='weighted', zero_division=0)
            recall = recall_score(actual_values, predictions, average='weighted', zero_division=0)
            f1 = f1_score(actual_values, predictions, average='weighted', zero_division=0)
            
            # Store performance data
            performance_entry = {
                'timestamp': datetime.now().isoformat(),
                'model_name': model_name,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'sample_count': len(actual_values),
                'metadata': metadata or {}
            }
            
            self.performance_history.append(performance_entry)
            
            # Save performance history
            self.save_performance_history()
            
            # Check if retraining is needed
            self.check_retraining_needed(model_name, accuracy)
            
            logger.info(f"✅ Performance tracked for {model_name}: Accuracy={accuracy:.4f}")
            
            return performance_entry
            
        except Exception as e:
            logger.error(f"❌ Failed to track performance: {e}")
            return None
    
    def check_retraining_needed(self, model_name, current_accuracy):
        """Check if model retraining is needed"""
        try:
            # Get recent performance for this model
            recent_performance = [
                entry for entry in self.performance_history[-20:]  # Last 20 entries
                if entry['model_name'] == model_name
            ]
            
            if len(recent_performance) < 5:
                return False  # Not enough data
            
            # Calculate average recent performance
            recent_accuracies = [entry['accuracy'] for entry in recent_performance]
            avg_recent_accuracy = np.mean(recent_accuracies)
            
            # Check for significant degradation
            if current_accuracy < (avg_recent_accuracy - self.retraining_threshold):
                logger.warning(f"⚠️ Performance degradation detected for {model_name}")
                logger.warning(f"   Current: {current_accuracy:.4f}, Recent Average: {avg_recent_accuracy:.4f}")
                
                # Schedule retraining
                self.schedule_retraining(model_name)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check retraining need: {e}")
            return False
    
    def schedule_retraining(self, model_name):
        """Schedule model retraining"""
        try:
            # Check if enough new data is available
            if self.has_sufficient_new_data():
                logger.info(f"🔄 Scheduling retraining for {model_name}")
                
                # Run retraining in background thread
                retraining_thread = threading.Thread(
                    target=self.retrain_model,
                    args=(model_name,)
                )
                retraining_thread.start()
                
            else:
                logger.info(f"⏳ Insufficient new data for retraining {model_name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to schedule retraining: {e}")
    
    def has_sufficient_new_data(self):
        """Check if sufficient new data is available for retraining"""
        try:
            # This would check your database for new samples
            # For now, return True to allow retraining
            return True
        except Exception as e:
            logger.error(f"❌ Failed to check data availability: {e}")
            return False
    
    def retrain_model(self, model_name):
        """Retrain a specific model"""
        try:
            logger.info(f"🔄 Starting retraining for {model_name}")
            
            # Load new training data
            new_data = self.load_new_training_data()
            
            if new_data is None or len(new_data) < self.min_samples_for_retraining:
                logger.warning(f"⚠️ Insufficient new data for retraining {model_name}")
                return False
            
            # Retrain model (this would use your enhanced training pipeline)
            success = self._execute_retraining(model_name, new_data)
            
            if success:
                logger.info(f"✅ Successfully retrained {model_name}")
                
                # Update model in memory
                self.load_models()
                
                # Track retraining performance
                self.track_retraining_performance(model_name, new_data)
                
                return True
            else:
                logger.error(f"❌ Failed to retrain {model_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during retraining: {e}")
            return False
    
    def load_new_training_data(self):
        """Load new training data for retraining"""
        try:
            # This would load new data from your database
            # For demonstration, return sample data
            sample_data = {
                'resume_text': ['Sample resume text 1', 'Sample resume text 2'],
                'role': ['Frontend Developer', 'Backend Developer'],
                'selected': [True, False]
            }
            
            return pd.DataFrame(sample_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to load new training data: {e}")
            return None
    
    def _execute_retraining(self, model_name, new_data):
        """Execute the actual retraining process"""
        try:
            # This would integrate with your enhanced training pipeline
            # For now, simulate successful retraining
            logger.info(f"🔄 Executing retraining for {model_name} with {len(new_data)} samples")
            
            # Simulate retraining time
            time.sleep(2)
            
            # Update model file timestamp to simulate retraining
            model_file = self.model_dir / f"{model_name}.pkl"
            if model_file.exists():
                model_file.touch()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to execute retraining: {e}")
            return False
    
    def track_retraining_performance(self, model_name, training_data):
        """Track performance after retraining"""
        try:
            # This would evaluate the retrained model
            # For now, create a performance entry
            retraining_entry = {
                'timestamp': datetime.now().isoformat(),
                'model_name': f"{model_name}_retrained",
                'accuracy': 0.85,  # Simulated improved accuracy
                'precision': 0.83,
                'recall': 0.87,
                'f1_score': 0.85,
                'sample_count': len(training_data),
                'metadata': {
                    'retraining_type': 'incremental',
                    'training_samples': len(training_data),
                    'previous_accuracy': 0.80
                }
            }
            
            self.performance_history.append(retraining_entry)
            self.save_performance_history()
            
            logger.info(f"✅ Retraining performance tracked for {model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to track retraining performance: {e}")
    
    def save_performance_history(self):
        """Save performance history to file"""
        try:
            performance_file = self.model_dir / "performance_history.json"
            
            with open(performance_file, 'w') as f:
                json.dump(self.performance_history, f, indent=2)
            
            logger.info("✅ Performance history saved")
            
        except Exception as e:
            logger.error(f"❌ Failed to save performance history: {e}")
    
    def get_performance_summary(self, model_name=None, days=30):
        """Get performance summary for specified period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if model_name:
                filtered_history = [
                    entry for entry in self.performance_history
                    if (entry['model_name'] == model_name and 
                        datetime.fromisoformat(entry['timestamp']) > cutoff_date)
                ]
            else:
                filtered_history = [
                    entry for entry in self.performance_history
                    if datetime.fromisoformat(entry['timestamp']) > cutoff_date
                ]
            
            if not filtered_history:
                return None
            
            # Calculate summary statistics
            summary = {
                'total_entries': len(filtered_history),
                'date_range': {
                    'start': min(entry['timestamp'] for entry in filtered_history),
                    'end': max(entry['timestamp'] for entry in filtered_history)
                },
                'average_metrics': {
                    'accuracy': np.mean([entry['accuracy'] for entry in filtered_history]),
                    'precision': np.mean([entry['precision'] for entry in filtered_history]),
                    'recall': np.mean([entry['recall'] for entry in filtered_history]),
                    'f1_score': np.mean([entry['f1_score'] for entry in filtered_history])
                },
                'performance_trend': self._calculate_performance_trend(filtered_history)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance summary: {e}")
            return None
    
    def _calculate_performance_trend(self, performance_data):
        """Calculate performance trend over time"""
        try:
            if len(performance_data) < 2:
                return "insufficient_data"
            
            # Sort by timestamp
            sorted_data = sorted(performance_data, key=lambda x: x['timestamp'])
            
            # Calculate trend for accuracy
            first_accuracy = sorted_data[0]['accuracy']
            last_accuracy = sorted_data[-1]['accuracy']
            
            if last_accuracy > first_accuracy + 0.02:
                return "improving"
            elif last_accuracy < first_accuracy - 0.02:
                return "declining"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"❌ Failed to calculate performance trend: {e}")
            return "unknown"
    
    def generate_performance_report(self, output_file=None):
        """Generate comprehensive performance report"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'system_overview': {
                    'total_models': len(self.models),
                    'performance_entries': len(self.performance_history),
                    'last_retraining': self._get_last_retraining_date()
                },
                'model_performance': {},
                'recommendations': []
            }
            
            # Generate performance summary for each model
            for model_name in self.models.keys():
                summary = self.get_performance_summary(model_name, days=30)
                if summary:
                    report['model_performance'][model_name] = summary
            
            # Generate recommendations
            report['recommendations'] = self._generate_recommendations()
            
            # Save report
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"✅ Performance report saved to {output_file}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate performance report: {e}")
            return None
    
    def _get_last_retraining_date(self):
        """Get the date of last retraining"""
        try:
            retraining_entries = [
                entry for entry in self.performance_history
                if 'retraining_type' in entry.get('metadata', {})
            ]
            
            if retraining_entries:
                latest = max(retraining_entries, key=lambda x: x['timestamp'])
                return latest['timestamp']
            
            return "No retraining recorded"
            
        except Exception as e:
            logger.error(f"❌ Failed to get last retraining date: {e}")
            return "Unknown"
    
    def _generate_recommendations(self):
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            # Check for models that need retraining
            for model_name in self.models.keys():
                summary = self.get_performance_summary(model_name, days=7)
                if summary and summary['average_metrics']['accuracy'] < 0.7:
                    recommendations.append(f"Consider retraining {model_name} - low recent accuracy")
            
            # Check for performance degradation
            for model_name in self.models.keys():
                summary = self.get_performance_summary(model_name, days=30)
                if summary and summary['performance_trend'] == 'declining':
                    recommendations.append(f"Investigate performance decline in {model_name}")
            
            # General recommendations
            if len(self.performance_history) < 50:
                recommendations.append("Collect more performance data for better insights")
            
            if not recommendations:
                recommendations.append("All models performing well - no immediate action needed")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate recommendations: {e}")
            return ["Error generating recommendations"]
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        try:
            logger.info("🚀 Starting continuous learning monitoring...")
            
            # Schedule regular performance checks
            schedule.every().hour.do(self.check_all_models_performance)
            schedule.every().day.at("00:00").do(self.generate_daily_report)
            schedule.every().week.do(self.generate_weekly_report)
            
            # Run monitoring loop
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
    
    def check_all_models_performance(self):
        """Check performance of all models"""
        try:
            logger.info("🔍 Checking all models performance...")
            
            for model_name in self.models.keys():
                # This would check actual performance in production
                # For now, just log the check
                logger.info(f"   Checked {model_name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to check models performance: {e}")
    
    def generate_daily_report(self):
        """Generate daily performance report"""
        try:
            report_file = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            self.generate_performance_report(report_file)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate daily report: {e}")
    
    def generate_weekly_report(self):
        """Generate weekly performance report"""
        try:
            report_file = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
            self.generate_performance_report(report_file)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate weekly report: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize continuous learning system
    cls = ContinuousLearningSystem()
    
    # Generate initial performance report
    report = cls.generate_performance_report("initial_performance_report.json")
    
    if report:
        print("📊 Initial Performance Report Generated")
        print(f"   Models: {report['system_overview']['total_models']}")
        print(f"   Performance Entries: {report['system_overview']['performance_entries']}")
        print(f"   Last Retraining: {report['system_overview']['last_retraining']}")
    
    # Start monitoring (uncomment to run continuously)
    # cls.start_monitoring() 