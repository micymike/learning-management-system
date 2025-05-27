from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ListField, DictField, ReferenceField
from datetime import datetime

class Student(Document):
    """Student model for storing student information"""
    name = StringField(required=True)
    email = StringField()
    github_username = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

class Assessment(Document):
    """Assessment model for storing assessment details and results"""
    name = StringField(required=True)
    date = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    rubric = ListField(DictField(), required=True)  # Store rubric as list of dicts
    results = ListField(DictField())  # Store assessment results

    def to_dict(self):
        """Convert assessment to dictionary format"""
        return {
            'id': str(self.id),
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'rubric': self.rubric,
            'results': self.results
        }

class StudentAssessment(Document):
    """Model for individual student assessment results"""
    student = ReferenceField(Student, required=True)
    assessment = ReferenceField(Assessment, required=True)
    scores = DictField(required=True)  # Store detailed scores
    repo_url = StringField()
    submission = StringField()  # Store code submission
    created_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        """Convert student assessment to dictionary format"""
        return {
            'id': str(self.id),
            'student_name': self.student.name,
            'assessment_name': self.assessment.name,
            'scores': self.scores,
            'repo_url': self.repo_url,
            'created_at': self.created_at.isoformat()
        }
