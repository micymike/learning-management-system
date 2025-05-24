from datetime import datetime
from typing import List, Dict, Optional, Any
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
import json


class MongoDBConnection:
    """MongoDB connection manager"""
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", database_name: str = "assessment_system"):
        self.client = MongoClient(connection_string)
        self.db: Database = self.client[database_name]
        self._setup_indexes()
    
    def _setup_indexes(self):
        """Create indexes for optimal performance"""
        # Students collection indexes
        self.db.students.create_index([("email", ASCENDING)], unique=True, sparse=True)
        self.db.students.create_index([("github_username", ASCENDING)])
        
        # Student assessments collection indexes
        self.db.student_assessments.create_index([("student_id", ASCENDING)])
        self.db.student_assessments.create_index([("assessment_id", ASCENDING)])
        self.db.student_assessments.create_index([("student_id", ASCENDING), ("assessment_id", ASCENDING)])
        
        # Assessments collection indexes
        self.db.assessments.create_index([("name", ASCENDING)])
        self.db.assessments.create_index([("date", ASCENDING)])


class Assessment:
    """Assessment model for MongoDB"""
    
    def __init__(self, db: Database):
        self.collection: Collection = db.assessments
    
    def create(self, name: str, rubric: str, date: Optional[datetime] = None, results: Optional[Dict] = None) -> str:
        """Create a new assessment"""
        now = datetime.utcnow()
        assessment_data = {
            'name': name,
            'date': date or now,
            'rubric': rubric,
            'results': results,
            'created_at': now,
            'updated_at': now
        }
        
        result = self.collection.insert_one(assessment_data)
        return str(result.inserted_id)
    
    def find_by_id(self, assessment_id: str) -> Optional[Dict]:
        """Find assessment by ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(assessment_id)})
        except:
            return None
    
    def find_all(self) -> List[Dict]:
        """Find all assessments"""
        return list(self.collection.find())
    
    def update(self, assessment_id: str, **kwargs) -> bool:
        """Update assessment"""
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {'_id': ObjectId(assessment_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete(self, assessment_id: str) -> bool:
        """Delete assessment"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(assessment_id)})
            return result.deleted_count > 0
        except:
            return False
    
    @staticmethod
    def to_dict(assessment_doc: Dict) -> Dict:
        """Convert MongoDB document to dictionary"""
        if not assessment_doc:
            return {}
        
        return {
            'id': str(assessment_doc['_id']),
            'name': assessment_doc['name'],
            'date': assessment_doc['date'].isoformat() if assessment_doc.get('date') else None,
            'rubric': assessment_doc['rubric'],
            'results': assessment_doc.get('results'),
            'created_at': assessment_doc['created_at'].isoformat(),
            'updated_at': assessment_doc['updated_at'].isoformat()
        }


class Student:
    """Student model for MongoDB"""
    
    def __init__(self, db: Database):
        self.collection: Collection = db.students
        self.db = db
    
    def create(self, name: str, email: Optional[str] = None, github_username: Optional[str] = None) -> str:
        """Create a new student"""
        now = datetime.utcnow()
        student_data = {
            'name': name,
            'email': email,
            'github_username': github_username,
            'created_at': now,
            'updated_at': now
        }
        
        result = self.collection.insert_one(student_data)
        return str(result.inserted_id)
    
    def find_by_id(self, student_id: str) -> Optional[Dict]:
        """Find student by ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(student_id)})
        except:
            return None
    
    def find_by_email(self, email: str) -> Optional[Dict]:
        """Find student by email"""
        return self.collection.find_one({'email': email})
    
    def find_all(self) -> List[Dict]:
        """Find all students"""
        return list(self.collection.find())
    
    def update(self, student_id: str, **kwargs) -> bool:
        """Update student"""
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {'_id': ObjectId(student_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete(self, student_id: str) -> bool:
        """Delete student and cascade delete their assessments"""
        try:
            # First delete all student assessments (cascade delete)
            student_assessment = StudentAssessment(self.db)
            student_assessment.delete_by_student_id(student_id)
            
            # Then delete the student
            result = self.collection.delete_one({'_id': ObjectId(student_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def get_assessment_count(self, student_id: str) -> int:
        """Get count of assessments for a student"""
        try:
            return self.db.student_assessments.count_documents({'student_id': ObjectId(student_id)})
        except:
            return 0
    
    def get_assessments(self, student_id: str) -> List[Dict]:
        """Get all assessments for a student"""
        try:
            student_assessment = StudentAssessment(self.db)
            return student_assessment.find_by_student_id(student_id)
        except:
            return []
    
    def to_dict(self, student_doc: Dict) -> Dict:
        """Convert MongoDB document to dictionary"""
        if not student_doc:
            return {}
        
        student_id = str(student_doc['_id'])
        return {
            'id': student_id,
            'name': student_doc['name'],
            'email': student_doc.get('email'),
            'github_username': student_doc.get('github_username'),
            'created_at': student_doc['created_at'].isoformat(),
            'updated_at': student_doc['updated_at'].isoformat(),
            'assessment_count': self.get_assessment_count(student_id)
        }
    
    def to_dict_with_assessments(self, student_doc: Dict) -> Dict:
        """Convert MongoDB document to dictionary with assessments included"""
        result = self.to_dict(student_doc)
        if result:
            student_id = result['id']
            student_assessment = StudentAssessment(self.db)
            assessments = student_assessment.find_by_student_id(student_id)
            result['assessments'] = [
                StudentAssessment.to_dict(sa, self.db) for sa in assessments
            ]
        return result


class StudentAssessment:
    """StudentAssessment model for MongoDB"""
    
    def __init__(self, db: Database):
        self.collection: Collection = db.student_assessments
        self.db = db
    
    def create(self, student_id: str, assessment_id: str, scores: Optional[Dict] = None, 
              repo_url: Optional[str] = None, submission: Optional[str] = None) -> str:
        """Create a new student assessment"""
        now = datetime.utcnow()
        student_assessment_data = {
            'student_id': ObjectId(student_id),
            'assessment_id': ObjectId(assessment_id),
            'scores': scores,
            'repo_url': repo_url,
            'submission': submission,
            'created_at': now
        }
        
        result = self.collection.insert_one(student_assessment_data)
        return str(result.inserted_id)
    
    def find_by_id(self, student_assessment_id: str) -> Optional[Dict]:
        """Find student assessment by ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(student_assessment_id)})
        except:
            return None
    
    def find_by_student_id(self, student_id: str) -> List[Dict]:
        """Find all assessments for a student"""
        try:
            return list(self.collection.find({'student_id': ObjectId(student_id)}))
        except:
            return []
    
    def find_by_assessment_id(self, assessment_id: str) -> List[Dict]:
        """Find all student submissions for an assessment"""
        try:
            return list(self.collection.find({'assessment_id': ObjectId(assessment_id)}))
        except:
            return []
    
    def find_by_student_and_assessment(self, student_id: str, assessment_id: str) -> Optional[Dict]:
        """Find specific student assessment"""
        try:
            return self.collection.find_one({
                'student_id': ObjectId(student_id),
                'assessment_id': ObjectId(assessment_id)
            })
        except:
            return None
    
    def update(self, student_assessment_id: str, **kwargs) -> bool:
        """Update student assessment"""
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            result = self.collection.update_one(
                {'_id': ObjectId(student_assessment_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete(self, student_assessment_id: str) -> bool:
        """Delete student assessment"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(student_assessment_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def delete_by_student_id(self, student_id: str) -> int:
        """Delete all assessments for a student (for cascade delete)"""
        try:
            result = self.collection.delete_many({'student_id': ObjectId(student_id)})
            return result.deleted_count
        except:
            return 0
    
    @staticmethod
    def _calculate_average_score(scores: Optional[Dict]) -> float:
        """Calculate average score from scores dictionary"""
        if not scores:
            return 0.0
        
        numeric_scores = [score for score in scores.values() if isinstance(score, (int, float))]
        return sum(numeric_scores) / len(numeric_scores) if numeric_scores else 0.0
    
    @staticmethod
    def to_dict(student_assessment_doc: Dict, db: Database) -> Dict:
        """Convert MongoDB document to dictionary"""
        if not student_assessment_doc:
            return {}
        
        # Get assessment name
        assessment_name = None
        if student_assessment_doc.get('assessment_id'):
            assessment_doc = db.assessments.find_one({'_id': student_assessment_doc['assessment_id']})
            if assessment_doc:
                assessment_name = assessment_doc['name']
        
        return {
            'id': str(student_assessment_doc['_id']),
            'student_id': str(student_assessment_doc['student_id']),
            'assessment_id': str(student_assessment_doc['assessment_id']),
            'assessment_name': assessment_name,
            'scores': student_assessment_doc.get('scores'),
            'repo_url': student_assessment_doc.get('repo_url'),
            'created_at': student_assessment_doc['created_at'].isoformat(),
            'average_score': StudentAssessment._calculate_average_score(student_assessment_doc.get('scores'))
        }


class AssessmentSystemMongoDB:
    """Main class to manage the assessment system"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", database_name: str = "assessment_system"):
        self.connection = MongoDBConnection(connection_string, database_name)
        self.db = self.connection.db
        
        # Initialize models
        self.assessments = Assessment(self.db)
        self.students = Student(self.db)
        self.student_assessments = StudentAssessment(self.db)
    
    def close_connection(self):
        """Close MongoDB connection"""
        self.connection.client.close()


# Example usage and testing
if __name__ == "__main__":
    # Initialize system
    system = AssessmentSystemMongoDB()
    
    try:
        # Create an assessment
        assessment_id = system.assessments.create(
            name="Python Programming Assessment",
            rubric="Code quality: 25pts, Functionality: 25pts, Documentation: 25pts, Testing: 25pts"
        )
        print(f"Created assessment: {assessment_id}")
        
        # Create a student
        student_id = system.students.create(
            name="John Doe",
            email="john.doe@example.com",
            github_username="johndoe"
        )
        print(f"Created student: {student_id}")
        
        # Create student assessment
        student_assessment_id = system.student_assessments.create(
            student_id=student_id,
            assessment_id=assessment_id,
            scores={"code_quality": 22, "functionality": 25, "documentation": 20, "testing": 23},
            repo_url="https://github.com/johndoe/assessment1"
        )
        print(f"Created student assessment: {student_assessment_id}")
        
        # Retrieve and display data
        student_doc = system.students.find_by_id(student_id)
        student_dict = system.students.to_dict_with_assessments(student_doc)
        print(f"Student with assessments: {json.dumps(student_dict, indent=2)}")
        
        assessment_doc = system.assessments.find_by_id(assessment_id)
        assessment_dict = Assessment.to_dict(assessment_doc)
        print(f"Assessment: {json.dumps(assessment_dict, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        system.close_connection()