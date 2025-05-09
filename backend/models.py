from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    rubric = db.Column(db.Text, nullable=False)
    results = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'rubric': self.rubric,
            'results': self.results,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    github_username = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with StudentAssessment
    assessments = db.relationship('StudentAssessment', back_populates='student', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'github_username': self.github_username,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'assessment_count': len(self.assessments)
        }
    
    def to_dict_with_assessments(self):
        result = self.to_dict()
        result['assessments'] = [sa.to_dict() for sa in self.assessments]
        return result

class StudentAssessment(db.Model):
    __tablename__ = 'student_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    scores = db.Column(JSON)
    repo_url = db.Column(db.String(255), nullable=True)
    submission = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', back_populates='assessments')
    assessment = db.relationship('Assessment')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'assessment_id': self.assessment_id,
            'assessment_name': self.assessment.name if self.assessment else None,
            'scores': self.scores,
            'repo_url': self.repo_url,
            'created_at': self.created_at.isoformat(),
            'average_score': self._calculate_average_score()
        }
    
    def _calculate_average_score(self):
        if not self.scores:
            return 0
        scores = [score for score in self.scores.values() if isinstance(score, (int, float))]
        return sum(scores) / len(scores) if scores else 0
