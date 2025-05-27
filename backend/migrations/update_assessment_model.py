from mongoengine import connect
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Assessment
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def update_assessments():
    """Add updated_at field to existing Assessment documents"""
    print("Starting migration: Adding updated_at field to Assessment documents")
    
    try:
        # Connect to MongoDB
        connect(host=os.getenv('MONGODB_URL'))
        
        # Get all assessments without updated_at
        assessments = Assessment.objects()
        count = 0
        
        for assessment in assessments:
            # Add updated_at if it doesn't exist
            if not hasattr(assessment, 'updated_at'):
                assessment.updated_at = assessment.created_at  # Use created_at as initial value
                assessment.save()
                count += 1
                
        print(f"Successfully updated {count} Assessment documents")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise e

if __name__ == '__main__':
    update_assessments()
