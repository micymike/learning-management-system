from mongoengine import connect, disconnect
import os
from dotenv import load_dotenv
from models import Assessment, Student, StudentAssessment

load_dotenv()

def initialize_db():
    """Initialize MongoDB connection and create indexes"""
    try:
        # Close any existing connections
        disconnect()
        
        # Connect to MongoDB
        db_url = os.getenv('MONGODB_URL')
        if not db_url:
            raise ValueError("MONGODB_URL not found in environment variables")
        
        print(f"Connecting to database...")
        connect(host=db_url)
        print("Connected successfully")
        
        # Create indexes
        Assessment.ensure_indexes()
        Student.ensure_indexes()
        StudentAssessment.ensure_indexes()
        
        print("Indexes created successfully")
        
        # Clear existing data (for testing)
        if os.getenv('ENVIRONMENT') == 'development':
            Assessment.objects.delete()
            Student.objects.delete()
            StudentAssessment.objects.delete()
            print("Database cleared for development")
            
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    initialize_db()
