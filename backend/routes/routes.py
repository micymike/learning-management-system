"""
This file defines the routes for the application
"""
from flask import Blueprint, request, jsonify, send_file, session
from flask_cors import CORS
from openpyxl.styles import PatternFill, Font
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

load_dotenv()

# Load OpenAI credentials from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
try:
    openai.api_key = OPENAI_API_KEY
except Exception as e:
    print(f"OpenAI API Error: {e}")

def format_scores_results(results):
    """
    Format scores into a pandas DataFrame and save as Excel
    """
    if not results:
        return io.BytesIO()

    # Extract all criteria from the results to ensure consistent columns
    criteria = set()
    for result in results:
        try:
            criteria.update(result['scores'].keys())
        except Exception as e:
            print(f"Error extracting criteria: {e}")
    
    scores_data = []
    for result in results:
        scores = {
            'Name': result['name'],
            'Repository': result['repo_url']
        }
        # Add all criteria scores, using 0 for missing values
        for criterion in criteria:
            scores[criterion] = result.get('scores', {}).get(criterion, 0)
        scores_data.append(scores)
    
    df = pd.DataFrame(scores_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        
        # Format header
        for col in range(len(df.columns)):
            cell = worksheet.cell(row=1, column=col + 1)
            cell.fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
            cell.font = Font(color='FFFFFF', bold=True)
            
        # Auto-adjust columns
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    output.seek(0)
    return output

def validate_rubric(rubric_text):
    """
    Validate that the rubric is properly formatted.
    Returns (is_valid, error_message)
    """
    if not rubric_text or not rubric_text.strip():
        return False, "Rubric cannot be empty"
    
    # Check if the rubric has at least one valid criterion
    lines = [line.strip() for line in rubric_text.split('\n') if line.strip()]
    if len(lines) == 0:
        return False, "Rubric must contain at least one criterion"
    
    # Validate that each line is a proper criterion (not too short)
    for line in lines:
        if len(line) < 5:  # Arbitrary minimum length for a meaningful criterion
            return False, f"Criterion '{line}' is too short. Each criterion should be descriptive."
    
    return True, ""

def validate_csv_content(students):
    """
    Validate that the parsed CSV content has the required fields.
    Returns (is_valid, error_message)
    """
    if not students or len(students) == 0:
        return False, "No student data found in the CSV file"
    
    # Check if each student has the required fields
    for i, student in enumerate(students):
        if 'name' not in student or not student['name'].strip():
            return False, f"Student at row {i+1} is missing a name"
        
        if 'repo_url' not in student or not student['repo_url'].strip():
            return False, f"Student '{student.get('name', f'at row {i+1}')}' is missing a repository URL"
        
        # Validate GitHub URL format (basic check)
        if not student['repo_url'].startswith(('http://', 'https://')) or 'github.com' not in student['repo_url']:
            return False, f"Invalid GitHub URL for student '{student.get('name', f'at row {i+1}')}': {student['repo_url']}"
    
    return True, ""

routes_blueprint = Blueprint('routes', __name__)

@routes_blueprint.route("/assess", methods=["POST"])
def assess():
    code = request.form.get('code')
    rubric_file = request.files.get('rubric')
    if not rubric_file:
        return jsonify({"error": "No rubric file provided"}), 400
    rubric = rubric_file.read().decode('utf-8')
    
    # Validate rubric
    is_valid, error_msg = validate_rubric(rubric)
    if not is_valid:
        return jsonify({"error": error_msg}), 400
    
    result = assess_code(code, rubric, client)
    return jsonify({"result": result})

@routes_blueprint.route("/upload_csv", methods=["POST"])
def upload_csv():
    # Validate file exists
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No CSV file provided"}), 400
    
    # Validate file type
    filename = file.filename.lower()
    if not filename.endswith(('.csv', '.xlsx', '.xls', '.txt')):
        return jsonify({"error": "Invalid file format. Please upload a CSV, Excel, or text file."}), 400
    
    # Get assessment name
    assessment_name = request.form.get('name', '')
    if not assessment_name.strip():
        assessment_name = f"Assessment {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Validate rubric file exists
    rubric_file = request.files.get('rubric')
    if not rubric_file:
        return jsonify({"error": "No rubric file provided"}), 400
    
    # Get rubric file extension
    rubric_filename = rubric_file.filename.lower()
    
    # Process rubric based on file type
    try:
        if rubric_filename.endswith('.txt') or rubric_filename.endswith('.csv'):
            # Text files - read directly
            try:
                rubric = rubric_file.read().decode('utf-8')
            except UnicodeDecodeError:
                # Try different encodings if UTF-8 fails
                try:
                    rubric_file.seek(0)
                    rubric = rubric_file.read().decode('latin-1')
                except:
                    return jsonify({"error": "Could not decode rubric file. Please ensure it's a valid text file."}), 400
        elif rubric_filename.endswith(('.xlsx', '.xls')):
            # Excel files - extract text from first column
            try:
                import pandas as pd
                df = pd.read_excel(rubric_file)
                # Extract first column as rubric criteria
                if len(df.columns) > 0:
                    rubric = '\n'.join(df[df.columns[0]].dropna().astype(str).tolist())
                else:
                    return jsonify({"error": "Excel file has no columns"}), 400
            except Exception as e:
                return jsonify({"error": f"Error processing Excel rubric: {str(e)}"}), 400
        else:
            # Accept any file type but warn about potential issues
            try:
                rubric = rubric_file.read().decode('utf-8', errors='ignore')
                print(f"Warning: Processing non-standard rubric file type: {rubric_filename}")
            except Exception as e:
                return jsonify({"error": f"Unsupported rubric file format. Please use .txt, .csv, .xlsx, or .xls: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error processing rubric file: {str(e)}"}), 400
    
    # Validate rubric content
    is_valid, error_msg = validate_rubric(rubric)
    if not is_valid:
        return jsonify({"error": error_msg}), 400
    
    # Process CSV file
    try:
        students = process_csv(file)
    except Exception as e:
        return jsonify({"error": f"Error processing CSV file: {str(e)}"}), 400
    
    # Validate CSV content
    is_valid, error_msg = validate_csv_content(students)
    if not is_valid:
        return jsonify({"error": error_msg}), 400
    
    # Process each student
    results = []
    for student in students:
        name = student['name']
        repo_url = student['repo_url']
        
        # Find or create student record
        student_record = Student.query.filter_by(name=name).first()
        if not student_record:
            student_record = Student(name=name)
            db.session.add(student_record)
            db.session.flush()  # Get ID without committing
        
        # Analyze the repo and get code
        try:
            code_str = analyze_github_repo(repo_url)
            if not code_str:
                results.append({
                    "name": name,
                    "repo_url": repo_url,
                    "error": "No code found in repository",
                    "scores": {"Error": "No code found"}
                })
                continue
        except Exception as e:
            results.append({
                "name": name,
                "repo_url": repo_url,
                "error": f"Error analyzing repository: {str(e)}",
                "scores": {"Error": "Repository analysis failed"}
            })
            continue
            
        repo_analysis = code_str if isinstance(code_str, str) else str(code_str)
        
        # Assess the code
        try:
            assessment = assess_code(repo_analysis, rubric, client)
        except Exception as e:
            results.append({
                "name": name,
                "repo_url": repo_url,
                "error": f"Error assessing code: {str(e)}",
                "scores": {"Error": "Assessment failed"}
            })
            continue
        
        # Parse assessment results
        scores = {}
        if isinstance(assessment, dict):
            scores = assessment
        else:
            assessment_lines = [line.strip() for line in assessment.split('\n')]
            for line in assessment_lines:
                if ',' in line:
                    try:
                        criterion, score = line.split(',', 1)
                        scores[criterion.strip()] = int(score.strip())
                    except (ValueError, TypeError):
                        continue
        
        # Create student assessment record
        student_assessment = StudentAssessment(
            student_id=student_record.id,
            assessment_id=None,  # Will be set after assessment is saved
            scores=scores,
            repo_url=repo_url,
            submission=code_str
        )
        db.session.add(student_assessment)
        
        results.append({
            "name": name,
            "repo_url": repo_url,
            "scores": scores
        })
    
    # Store results in session for later download
    session['last_assessment'] = results
    
    # Save to database
    try:
        # Create a new assessment record
        new_assessment = Assessment(
            name=assessment_name,
            rubric=rubric,
            results=results
        )
        db.session.add(new_assessment)
        db.session.flush()  # Get ID without committing
        
        # Update student assessments with assessment ID
        for student_assessment in StudentAssessment.query.filter_by(assessment_id=None).all():
            student_assessment.assessment_id = new_assessment.id
            db.session.add(student_assessment)
        
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "results": results,
            "assessment": {
                "id": new_assessment.id,
                "name": new_assessment.name,
                "date": new_assessment.date.isoformat() if new_assessment.date else None,
                "created_at": new_assessment.created_at.isoformat()
            },
            "message": f"Successfully processed {len(results)} student submissions"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Error saving assessment to database: {str(e)}",
            "results": results  # Still return results even if DB save fails
        }), 500

@routes_blueprint.route("/assessments", methods=["GET"])
def get_assessments():
    """Get all assessments"""
    try:
        assessments = Assessment.query.order_by(Assessment.created_at.desc()).all()
        return jsonify({
            "success": True,
            "assessments": [assessment.to_dict() for assessment in assessments]
        })
    except Exception as e:
        return jsonify({"error": f"Error retrieving assessments: {str(e)}"}), 500

@routes_blueprint.route("/assessments/<int:assessment_id>", methods=["GET"])
def get_assessment(assessment_id):
    """Get a specific assessment by ID"""
    try:
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return jsonify({"error": f"Assessment with ID {assessment_id} not found"}), 404
        
        return jsonify({
            "success": True,
            "assessment": assessment.to_dict()
        })
    except Exception as e:
        return jsonify({"error": f"Error retrieving assessment: {str(e)}"}), 500

@routes_blueprint.route("/download_excel", methods=["GET"])
def download_excel():
    results = session.get('last_assessment')
    if not results:
        return jsonify({"error": "No assessment results found. Please run an assessment first."}), 404
    
    output = format_scores_results(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        output,
        as_attachment=True,
        download_name=f"assessment_scores_{timestamp}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@routes_blueprint.route("/download_excel/<int:assessment_id>", methods=["GET"])
def download_assessment_excel(assessment_id):
    """Download Excel for a specific assessment"""
    try:
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return jsonify({"error": f"Assessment with ID {assessment_id} not found"}), 404
        
        results = assessment.results
        output = format_scores_results(results)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f"assessment_{assessment_id}_{assessment.name.replace(' ', '_')}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"error": f"Error generating Excel file: {str(e)}"}), 500

@routes_blueprint.route("/upload_rubric", methods=["POST"])
def upload_rubric():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400
    
    try:
        rubric = file.read().decode('utf-8')
        
        # Validate rubric content
        is_valid, error_msg = validate_rubric(rubric)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
            
        return jsonify({"success": True, "rubric": rubric})
    except Exception as e:
        return jsonify({"error": f"Error processing rubric: {str(e)}"}), 400

@routes_blueprint.route("/upload_github_url", methods=["POST"])
def upload_github_url():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "No GitHub URL provided"}), 400
    
    # Validate GitHub URL format
    if not url.startswith(('http://', 'https://')) or 'github.com' not in url:
        return jsonify({"error": "Invalid GitHub URL format"}), 400
    
    try:
        code = analyze_github_repo(url)
        return jsonify({"success": True, "code": code})
    except Exception as e:
        return jsonify({"error": f"Error analyzing GitHub repository: {str(e)}"}), 400

# Analytics endpoint
@routes_blueprint.route("/analytics", methods=["GET"])
def get_analytics():
    """Get aggregate analytics: total students, total assessments, average score."""
    try:
        total_students = Student.query.count()
        total_assessments = Assessment.query.count()
        # Calculate average score across all student assessments
        avg_score = None
        total_scores = 0
        score_count = 0
        student_assessments = StudentAssessment.query.all()
        for sa in student_assessments:
            if sa.score is not None:
                total_scores += sa.score
                score_count += 1
        if score_count > 0:
            avg_score = round(total_scores / score_count, 2)
        return jsonify({
            "success": True,
            "total_students": total_students,
            "total_assessments": total_assessments,
            "average_score": avg_score
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Student routes
@routes_blueprint.route("/students", methods=["GET"])
def get_students():
    """Get all students with their assessment counts"""
    try:
        students = Student.query.all()
        return jsonify({
            "success": True,
            "students": [student.to_dict() for student in students]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    """Get a specific student with their assessment history"""
    try:
        student = Student.query.get_or_404(student_id)
        return jsonify({
            "success": True,
            "student": student.to_dict_with_assessments()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
