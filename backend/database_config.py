import os
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'ai_recruitment'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        self.redis_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': os.getenv('REDIS_PORT', 6379),
            'db': os.getenv('REDIS_DB', 0)
        }
        
        self.connection = None
        self.redis_client = None
        
    def connect_postgres(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
            return False
    
    def connect_redis(self):
        """Connect to Redis for caching"""
        try:
            self.redis_client = redis.Redis(**self.redis_config)
            self.redis_client.ping()
            logger.info("✅ Connected to Redis cache")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            return False
    
    def create_tables(self):
        """Create necessary database tables"""
        if not self.connection:
            logger.error("❌ No database connection")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Candidates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id SERIAL PRIMARY KEY,
                    candidate_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    phone VARCHAR(50),
                    location VARCHAR(255),
                    years_experience INTEGER,
                    education_level VARCHAR(100),
                    industry VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Resumes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id SERIAL PRIMARY KEY,
                    candidate_id INTEGER REFERENCES candidates(id),
                    resume_text TEXT NOT NULL,
                    resume_file_path VARCHAR(500),
                    file_size INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_status VARCHAR(50) DEFAULT 'pending'
                )
            """)
            
            # Applications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id SERIAL PRIMARY KEY,
                    candidate_id INTEGER REFERENCES candidates(id),
                    resume_id INTEGER REFERENCES resumes(id),
                    selected_role VARCHAR(255) NOT NULL,
                    predicted_role VARCHAR(255),
                    ats_score INTEGER,
                    application_status VARCHAR(50) DEFAULT 'pending',
                    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Interviews table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interviews (
                    id SERIAL PRIMARY KEY,
                    application_id INTEGER REFERENCES applications(id),
                    interview_date TIMESTAMP,
                    interview_type VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'scheduled',
                    notes TEXT
                )
            """)
            
            # Interview questions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interview_questions (
                    id SERIAL PRIMARY KEY,
                    interview_id INTEGER REFERENCES interviews(id),
                    question_text TEXT NOT NULL,
                    question_type VARCHAR(50),
                    question_order INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Interview answers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interview_answers (
                    id SERIAL PRIMARY KEY,
                    question_id INTEGER REFERENCES interview_questions(id),
                    answer_text TEXT NOT NULL,
                    score DECIMAL(5,2),
                    feedback TEXT,
                    sentiment_score DECIMAL(3,2),
                    length_score DECIMAL(3,2),
                    relevance_score DECIMAL(3,2),
                    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Decisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id SERIAL PRIMARY KEY,
                    application_id INTEGER REFERENCES applications(id),
                    final_decision VARCHAR(100) NOT NULL,
                    final_score DECIMAL(5,2),
                    decision_reasons TEXT,
                    confidence_level VARCHAR(50),
                    bias_flags TEXT[],
                    decision_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    decision_maker VARCHAR(255)
                )
            """)
            
            # Skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id SERIAL PRIMARY KEY,
                    skill_name VARCHAR(255) UNIQUE NOT NULL,
                    skill_category VARCHAR(100),
                    skill_level VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Candidate skills mapping table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS candidate_skills (
                    id SERIAL PRIMARY KEY,
                    candidate_id INTEGER REFERENCES candidates(id),
                    skill_id INTEGER REFERENCES skills(id),
                    proficiency_level VARCHAR(50),
                    years_experience INTEGER,
                    verified BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Model performance tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_performance (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(255) NOT NULL,
                    model_version VARCHAR(100),
                    accuracy_score DECIMAL(5,4),
                    precision_score DECIMAL(5,4),
                    recall_score DECIMAL(5,4),
                    f1_score DECIMAL(5,4),
                    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dataset_size INTEGER,
                    features_count INTEGER
                )
            """)
            
            # Audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    action VARCHAR(100) NOT NULL,
                    table_name VARCHAR(100),
                    record_id INTEGER,
                    old_values JSONB,
                    new_values JSONB,
                    user_id VARCHAR(255),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address INET
                )
            """)
            
            self.connection.commit()
            logger.info("✅ Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def insert_candidate(self, candidate_data):
        """Insert a new candidate"""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                INSERT INTO candidates (candidate_name, email, phone, location, years_experience, education_level, industry)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                candidate_data.get('candidate_name'),
                candidate_data.get('email'),
                candidate_data.get('phone'),
                candidate_data.get('location'),
                candidate_data.get('years_experience'),
                candidate_data.get('education_level'),
                candidate_data.get('industry')
            ))
            
            candidate_id = cursor.fetchone()['id']
            self.connection.commit()
            
            logger.info(f"✅ Candidate inserted with ID: {candidate_id}")
            return candidate_id
            
        except Exception as e:
            logger.error(f"❌ Failed to insert candidate: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()
    
    def insert_resume(self, candidate_id, resume_data):
        """Insert resume data"""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                INSERT INTO resumes (candidate_id, resume_text, resume_file_path, file_size)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                candidate_id,
                resume_data.get('resume_text'),
                resume_data.get('file_path'),
                resume_data.get('file_size')
            ))
            
            resume_id = cursor.fetchone()['id']
            self.connection.commit()
            
            logger.info(f"✅ Resume inserted with ID: {resume_id}")
            return resume_id
            
        except Exception as e:
            logger.error(f"❌ Failed to insert resume: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()
    
    def insert_application(self, candidate_id, resume_id, application_data):
        """Insert application data"""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                INSERT INTO applications (candidate_id, resume_id, selected_role, predicted_role, ats_score)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                candidate_id,
                resume_id,
                application_data.get('selected_role'),
                application_data.get('predicted_role'),
                application_data.get('ats_score')
            ))
            
            application_id = cursor.fetchone()['id']
            self.connection.commit()
            
            logger.info(f"✅ Application inserted with ID: {application_id}")
            return application_id
            
        except Exception as e:
            logger.error(f"❌ Failed to insert application: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()
    
    def cache_data(self, key, data, expire_time=3600):
        """Cache data in Redis"""
        if not self.redis_client:
            return False
        
        try:
            serialized_data = json.dumps(data, default=str)
            self.redis_client.setex(key, expire_time, serialized_data)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cache data: {e}")
            return False
    
    def get_cached_data(self, key):
        """Retrieve cached data from Redis"""
        if not self.redis_client:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to retrieve cached data: {e}")
            return None
    
    def close_connections(self):
        """Close all database connections"""
        if self.connection:
            self.connection.close()
            logger.info("✅ PostgreSQL connection closed")
        
        if self.redis_client:
            self.redis_client.close()
            logger.info("✅ Redis connection closed")

# Database initialization function
def init_database():
    """Initialize database and create tables"""
    db_manager = DatabaseManager()
    
    # Connect to databases
    if db_manager.connect_postgres():
        db_manager.create_tables()
    
    if db_manager.connect_redis():
        logger.info("✅ Redis cache available")
    
    return db_manager

# Example usage
if __name__ == "__main__":
    # Test database connection
    db = init_database()
    
    if db:
        # Test candidate insertion
        candidate_data = {
            'candidate_name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'location': 'New York, NY',
            'years_experience': 5,
            'education_level': 'Bachelor',
            'industry': 'Technology'
        }
        
        candidate_id = db.insert_candidate(candidate_data)
        if candidate_id:
            print(f"✅ Test candidate inserted with ID: {candidate_id}")
        
        # Test caching
        test_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
        if db.cache_data('test_key', test_data):
            print("✅ Test data cached successfully")
        
        cached_data = db.get_cached_data('test_key')
        if cached_data:
            print(f"✅ Cached data retrieved: {cached_data}")
        
        db.close_connections() 