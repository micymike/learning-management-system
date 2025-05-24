"""
This file defines the routes for the application
"""
from flask import Blueprint, request, jsonify, send_file, session
from flask_cors import CORS
from openpyxl.styles import PatternFill, Font, Alignment
import io
import pandas as pd
import os
import json
from datetime import datetime
from AI_assessor import assess_code, client
from repo_analyzer import analyze_github_repo
from csv_analyzer import process_csv
from rubric_handler import load_rubric
import openai
from dotenv import load_dotenv
from models import db, Assessment, Student, StudentAssessment
from rag_assessor import get_assessor

load_dotenv()

# Create Blueprint
routes_blueprint = Blueprint('routes', __name__)

# Load OpenAI credentials from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
try:
    openai.api_key = OPENAI_API_KEY
except Exception as e:
    print(f"OpenAI API Error: {e}")

@routes_blueprint.route('/assess', methods=['POST'])
def assess():
    """Assess code using either traditional or RAG-based approach"""
    try:
        code = request.form.get('code')
        rubric = request.form.get('rubric')
        
        if not code:
            return jsonify({"error": "No code provided"}), 400
        
        if not rubric:
            return jsonify({"error": "No rubric provided"}), 400
        
        # Try RAG-based assessment first
        try:
            rag = get_assessor()
            result = rag.assess_code(code, rubric)
        except Exception as e:
            print(f"RAG assessment failed, falling back to direct assessment: {e}")
            # Fall back to direct assessment
            result = assess_code(code, rubric, client)
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/assessments', methods=['GET'])
def get_assessments():
    """Get all assessments"""
    try:
        assessments = Assessment.query.all()
        return jsonify({
            "success": True,
            "assessments": [a.to_dict() for a in assessments]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/assessments/<int:assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    """Get a specific assessment"""
    try:
        assessment = Assessment.query.get_or_404(assessment_id)
        return jsonify({
            "success": True,
            "assessment": assessment.to_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/upload_csv', methods=['POST'])
def upload_csv():
    """Process CSV file with student data"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get assessment name and rubric
        name = request.form.get('name', f'Assessment {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        rubric = request.form.get('rubric')
        
        if not rubric and 'rubric' in request.files:
            rubric_file = request.files['rubric']
            rubric = rubric_file.read().decode('utf-8')
        
        if not rubric:
            return jsonify({"error": "No rubric provided"}), 400
        
        # Save the file temporarily
        temp_path = f"temp_{datetime.now().timestamp()}.csv"
        file.save(temp_path)
        
        try:
            # Process the CSV
            df = pd.read_csv(temp_path)
            
            # Create assessment record
            assessment = Assessment(
                name=name,
                rubric=rubric,
                date=datetime.utcnow()
            )
            db.session.add(assessment)
            
            # Process each student
            results = []
            for _, row in df.iterrows():
                student_name = row.get('name', '').strip()
                repo_url = row.get('repo_url', '').strip()
                
                if not student_name or not repo_url:
                    continue
                
                try:
                    # Get or create student
                    student = Student.query.filter_by(name=student_name).first()
                    if not student:
                        student = Student(name=student_name)
                        db.session.add(student)
                    
                    # Create student assessment
                    student_assessment = StudentAssessment(
                        student=student,
                        assessment=assessment,
                        repo_url=repo_url
                    )
                    db.session.add(student_assessment)
                    
                    # Add to results
                    results.append({
                        'name': student_name,
                        'repo_url': repo_url,
                        'status': 'Pending Assessment'
                    })
                except Exception as e:
                    print(f"Error processing student {student_name}: {e}")
                    results.append({
                        'name': student_name,
                        'repo_url': repo_url,
                        'status': 'Error',
                        'error': str(e)
                    })
            
            # Save all changes
            db.session.commit()
            
            # Return success response
            return jsonify({
                "success": True,
                "message": "CSV processed successfully",
                "assessment": assessment.to_dict(),
                "results": results
            })
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/upload_github_url', methods=['POST'])
def upload_github_url():
    """Process a GitHub repository URL"""
    try:
        url = request.form.get('url')
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        # Analyze the repository
        code = analyze_github_repo(url)
        if not code:
            return jsonify({"error": "No code found in repository"}), 400
        
        return jsonify({
            "success": True,
            "code": code
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/upload_rubric', methods=['POST'])
def upload_rubric():
    """Process a rubric file"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read the rubric file
        rubric = file.read().decode('utf-8')
        
        return jsonify({
            "success": True,
            "rubric": rubric
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    try:
        students = Student.query.all()
        return jsonify({
            "success": True,
            "students": [s.to_dict() for s in students]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get a specific student"""
    try:
        student = Student.query.get_or_404(student_id)
        return jsonify({
            "success": True,
            "student": student.to_dict_with_assessments()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        # Get all assessments
        assessments = Assessment.query.all()
        
        # Calculate analytics
        total_assessments = len(assessments)
        total_students = Student.query.count()
        total_submissions = StudentAssessment.query.count()
        
        # Get average scores
        scores = []
        for assessment in assessments:
            for student_assessment in assessment.student_assessments:
                if student_assessment.scores:
                    avg_score = student_assessment._calculate_average_score()
                    if avg_score > 0:
                        scores.append(avg_score)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return jsonify({
            "success": True,
            "analytics": {
                "total_assessments": total_assessments,
                "total_students": total_students,
                "total_submissions": total_submissions,
                "average_score": round(avg_score, 2)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
