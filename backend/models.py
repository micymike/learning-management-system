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
    numeric_id = IntField()  # Optional numeric ID for easier reference
    rubric = DictField(required=True)  # Store rubric as a single dict
    results = ListField(ReferenceField('StudentAssessment'))  # Store references to StudentAssessment

    def save(self, *args, **kwargs):
        """Override save to set numeric_id if not already set"""
        if not self.numeric_id:
            # Generate a numeric ID based on timestamp if not set
            import time
            self.numeric_id = int(time.time() * 1000)
        return super(Assessment, self).save(*args, **kwargs)

    def to_dict(self):
        """Convert assessment to dictionary format"""
        # Get result IDs as strings instead of trying to convert objects
        result_ids = [str(r.id) for r in self.results] if self.results else []
        
        return {
            'id': str(self.id),
            'numeric_id': self.numeric_id,
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'rubric': self.rubric,
            'results': result_ids
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
