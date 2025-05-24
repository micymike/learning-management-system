from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, IntField, ReferenceField, DictField, ListField, connect

# MongoDB connection will be established in main.py

class Assessment(Document):
    name = StringField(required=True)
    date = DateTimeField(default=datetime.utcnow)
    rubric = StringField(required=True)
    results = ListField(DictField())
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'rubric': self.rubric,
            'results': self.results,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Student(Document):
    name = StringField(required=True)
    email = StringField()
    github_username = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        assessments = StudentAssessment.objects(student=self)
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'github_username': self.github_username,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'assessment_count': len(assessments)
        }
    
    def to_dict_with_assessments(self):
        result = self.to_dict()
        assessments = StudentAssessment.objects(student=self)
        result['assessments'] = [sa.to_dict() for sa in assessments]
        return result

class StudentAssessment(Document):
    student = ReferenceField(Student, required=True)
    assessment = ReferenceField(Assessment, required=True)
    scores = DictField()
    repo_url = StringField()
    submission = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'student_id': str(self.student.id),
            'assessment_id': str(self.assessment.id),
            'assessment_name': self.assessment.name if self.assessment else None,
            'scores': self.scores,
            'repo_url': self.repo_url,
            'created_at': self.created_at.isoformat(),
            'average_score': self._calculate_average_score()
        }
    
    def _calculate_average_score(self):
        if not self.scores:
            return 0
            
        # Check if we have the new format with criteria_scores
        if 'criteria_scores' in self.scores:
            if 'percentage' in self.scores:
                return self.scores['percentage']
            elif self.scores.get('max_points', 0) > 0:
                return (self.scores['total_points'] / self.scores['max_points']) * 100
            else:
                return 0
        
        # Legacy format - direct scores
        scores = [score for score in self.scores.values() if isinstance(score, (int, float))]
        return sum(scores) / len(scores) if scores else 0