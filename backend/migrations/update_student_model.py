from mongoengine import connect
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Student
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def update_students():
    """Add updated_at field to existing Student documents"""
    print("Starting migration: Adding updated_at field to Student documents")
    
    try:
        # Connect to MongoDB
        connect(host=os.getenv('MONGODB_URL'))
        
        # Get all students without updated_at
        students = Student.objects()
        count = 0
        
        for student in students:
            # Add updated_at if it doesn't exist
            if not hasattr(student, 'updated_at'):
                student.updated_at = student.created_at  # Use created_at as initial value
                student.save()
                count += 1
                
        print(f"Successfully updated {count} Student documents")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise e

if __name__ == '__main__':
    update_students()
