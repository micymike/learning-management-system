"""
Migration script to add numeric_id to existing Assessment documents
"""
import os
import sys
import time
from dotenv import load_dotenv
from mongoengine import connect
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Assessment

def main():
    """Add numeric_id to existing Assessment documents"""
    # Load environment variables
    load_dotenv()
    
    # Connect to MongoDB
    mongodb_url = os.getenv('MONGODB_URL')
    if not mongodb_url:
        print("Error: MONGODB_URL environment variable not set")
        sys.exit(1)
    
    connect(host=mongodb_url)
    
    # Get all assessments without numeric_id
    assessments = Assessment.objects(numeric_id__exists=False)
    count = assessments.count()
    
    if count == 0:
        print("No assessments found without numeric_id")
        return
    
    print(f"Found {count} assessments without numeric_id")
    
    # Update each assessment with a numeric_id
    for i, assessment in enumerate(assessments):
        # Generate a unique numeric ID based on timestamp and index
        numeric_id = int(time.time() * 1000) + i
        
        print(f"Updating assessment {assessment.id} with numeric_id {numeric_id}")
        assessment.numeric_id = numeric_id
        assessment.save()
    
    print(f"Successfully updated {count} assessments with numeric_id")

if __name__ == "__main__":
    main()