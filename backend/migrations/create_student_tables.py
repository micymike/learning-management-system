"""
Migration script to create student tracking tables
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Assessment, Student, StudentAssessment
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def create_tables():
    """Create student tracking tables"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("Student tracking tables created successfully")
        
        # Check if there are existing assessments to migrate
        assessments = Assessment.query.all()
        if assessments:
            print(f"Found {len(assessments)} existing assessments to migrate")
            
            # Migrate existing assessment data to student records
            for assessment in assessments:
                if not assessment.results:
                    continue
                    
                for result in assessment.results:
                    name = result.get('name')
                    if not name:
                        continue
                        
                    # Find or create student
                    student = Student.query.filter_by(name=name).first()
                    if not student:
                        student = Student(name=name)
                        db.session.add(student)
                        db.session.flush()
                    
                    # Create student assessment record
                    student_assessment = StudentAssessment(
                        student_id=student.id,
                        assessment_id=assessment.id,
                        scores=result.get('scores', {}),
                        repo_url=result.get('repo_url'),
                        submission=None  # No submission data in existing assessments
                    )
                    db.session.add(student_assessment)
            
            db.session.commit()
            print("Existing assessment data migrated to student records")
        
        print("Migration completed successfully")

if __name__ == '__main__':
    create_tables()
