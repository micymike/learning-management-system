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
from rubric_handler import load_rubric, parse_rubric_lines, calculate_percentage, is_passing_grade
import openai
from dotenv import load_dotenv
from models import Assessment, Student, StudentAssessment

# Initialize blueprint
routes_blueprint = Blueprint('routes', __name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
try:
    openai.api_key = OPENAI_API_KEY
except Exception as e:
    print(f"OpenAI API Error: {e}")

def validate_rubric(rubric_text):
    """
    Validate that the rubric is properly formatted.
    Returns (is_valid, error_message)
    """
    print(f"\nValidating rubric:\n{rubric_text}")
    
    if not rubric_text or not rubric_text.strip():
        return False, "Rubric cannot be empty"
    
    lines = [line.strip() for line in rubric_text.split('\n') if line.strip()]
    if len(lines) == 0:
        return False, "Rubric must contain at least one criterion"
    
    for line in lines:
        if len(line) < 5:
            return False, f"Criterion '{line}' is too short. Each criterion should be descriptive."
    
    print("Rubric validation successful")
    return True, ""

def validate_csv_content(students):
    """
    Validate that the parsed CSV content has the required fields.
    Returns (is_valid, error_message)
    """
    if not students or len(students) == 0:
        return False, "No student data found in the CSV file"
    
    for i, student in enumerate(students):
        if 'name' not in student or not student['name'].strip():
            return False, f"Student at row {i+1} is missing a name"
        
        if 'repo_url' not in student or not student['repo_url'].strip():
            return False, f"Student '{student.get('name', f'at row {i+1}')}' is missing a repository URL"
        
        if not student['repo_url'].startswith(('http://', 'https://')) or 'github.com' not in student['repo_url']:
            return False, f"Invalid GitHub URL for student '{student.get('name', f'at row {i+1}')}': {student['repo_url']}"
    
    return True, ""

def format_scores_results(results):
    """Format scores into a pandas DataFrame and save as Excel"""
    if not results:
        return io.BytesIO()

    scores_data = []
    for result in results:
        scores = {
            'Name': result['name'],
            'Repository': result['repo_url']
        }
        
        if 'scores' in result and isinstance(result['scores'], dict):
            if 'criteria_scores' in result['scores']:
                criteria_scores = result['scores']['criteria_scores']
                for criterion, data in criteria_scores.items():
                    scores[f"{criterion} (Points)"] = f"{data.get('points', 0)}/{data.get('max_points', 0)}"
                    if 'justification' in data:
                        scores[f"{criterion} (Justification)"] = data['justification']
                
                scores['Total Points'] = f"{result['scores'].get('total_points', 0)}/{result['scores'].get('max_points', 0)}"
                scores['Percentage'] = f"{result['scores'].get('percentage', 0)}%"
                scores['Status'] = "PASS" if result['scores'].get('passing', False) else "FAIL"
            else:
                for criterion, score_value in result['scores'].items():
                    if isinstance(score_value, dict) and 'mark' in score_value:
                        scores[f"{criterion} (Mark)"] = score_value.get('mark', 'N/A')
                        scores[f"{criterion} (Justification)"] = score_value.get('justification', '')
                    else:
                        scores[criterion] = score_value
        
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
            
            # Format justification columns
            if 'Justification' in df.columns[col]:
                worksheet.column_dimensions[cell.column_letter].width = 50
                for row in range(2, len(df) + 2):
                    cell = worksheet.cell(row=row, column=col + 1)
                    cell.alignment = Alignment(wrap_text=True, vertical='top')
            else:
                max_length = max(len(str(cell.value)) for cell in worksheet[cell.column_letter][1:])
                worksheet.column_dimensions[cell.column_letter].width = min(max_length + 2, 40)
    
    output.seek(0)
    return output

@routes_blueprint.route("/assess", methods=["POST"])
def assess():
    """Handle individual code assessment"""
    code = request.form.get('code')
    rubric_file = request.files.get('rubric')
    
    if not rubric_file:
        return jsonify({"error": "No rubric file provided"}), 400
        
    try:
        rubric = rubric_file.read().decode('utf-8')
        print(f"\nProcessing assessment with rubric:\n{rubric}")
        
        is_valid, error_msg = validate_rubric(rubric)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        rubric_items = parse_rubric_lines(rubric.strip().split('\n'))
        print("\nParsed rubric items:")
        print(json.dumps(rubric_items, indent=2))
        
        result = assess_code(code, rubric_items, client)
        print("\nAssessment results:")
        print(json.dumps(result, indent=2))
        
        return jsonify({
            "result": result,
            "passing": result.get('passing', False),
            "percentage": result.get('percentage', 0),
            "total_points": result.get('total_points', 0),
            "max_points": result.get('max_points', 0)
        })
    except Exception as e:
        print(f"Error in assessment: {str(e)}")
        return jsonify({"error": f"Assessment failed: {str(e)}"}), 500

@routes_blueprint.route("/upload_csv", methods=["POST"])
def upload_csv():
    """Handle batch assessment from CSV"""
    file = request.files.get('file')
    rubric_file = request.files.get('rubric')
    
    if not file or not rubric_file:
        return jsonify({"error": "Must provide both CSV file and rubric file"}), 400
    
    assessment_name = request.form.get('name', '') or f"Assessment {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    print(f"\nProcessing assessment: {assessment_name}")
    
    # Read and validate rubric
    try:
        rubric = rubric_file.read().decode('utf-8')
        print("\nRubric content:")
        print(rubric)
        
        is_valid, error_msg = validate_rubric(rubric)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
    except Exception as e:
        return jsonify({"error": f"Error reading rubric: {str(e)}"}), 400
    
    # Process student data
    try:
        students = process_csv(file)
        is_valid, error_msg = validate_csv_content(students)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
    except Exception as e:
        return jsonify({"error": f"Error processing CSV: {str(e)}"}), 400
    
    results = []
    student_assessments = []
    rubric_items = parse_rubric_lines(rubric.strip().split('\n'))
    
    print("\nParsed rubric items:")
    print(json.dumps(rubric_items, indent=2))
    
    for student in students:
        name = student['name']
        repo_url = student['repo_url']
        print(f"\nProcessing student: {name}")
        print(f"Repository: {repo_url}")
        
        try:
            # Get or create student record
            student_record = Student.objects(name=name).first()
            if not student_record:
                student_record = Student(name=name)
                student_record.save()
            
            # Analyze repository
            code_str = analyze_github_repo(repo_url)
            if not code_str:
                print(f"No code found for {name}")
                results.append({
                    "name": name,
                    "repo_url": repo_url,
                    "error": "No code found",
                    "scores": {"Error": "No code found"}
                })
                continue
            
            print(f"Code retrieved for {name} ({len(code_str)} characters)")
            
            # Assess code
            assessment = assess_code(code_str, rubric_items, client)
            print(f"\nAssessment results for {name}:")
            print(json.dumps(assessment, indent=2))
            
            student_assessments.append({
                "student": student_record,
                "scores": assessment,
                "repo_url": repo_url,
                "submission": code_str
            })
            
            results.append({
                "name": name,
                "repo_url": repo_url,
                "scores": assessment,
                "assessment": {
                    'total_points': assessment.get('total_points', 0),
                    'max_points': assessment.get('max_points', 0),
                    'percentage': assessment.get('percentage', 0),
                    'passing': assessment.get('passing', False)
                }
            })
            
        except Exception as e:
            print(f"Error processing {name}: {str(e)}")
            results.append({
                "name": name,
                "repo_url": repo_url,
                "error": str(e),
                "scores": {"Error": "Processing failed"}
            })
    
    session['last_assessment'] = results
    
    try:
        # Save assessment record
        new_assessment = Assessment(
            name=assessment_name,
            rubric=rubric,
            results=results
        ).save()
        
        # Save individual student assessments
        for data in student_assessments:
            StudentAssessment(
                student=data["student"],
                assessment=new_assessment,
                scores=data["scores"],
                repo_url=data["repo_url"],
                submission=data["submission"]
            ).save()
        
        return jsonify({
            "success": True,
            "results": results,
            "assessment": {
                "id": str(new_assessment.id),
                "name": new_assessment.name,
                "date": new_assessment.date.isoformat() if new_assessment.date else None,
                "created_at": new_assessment.created_at.isoformat()
            }
        })
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({
            "error": "Database error",
            "message": str(e),
            "results": results
        }), 500

@routes_blueprint.route("/assessments", methods=["GET"])
def get_assessments():
    """Get all assessments"""
    try:
        assessments = Assessment.objects().order_by('-created_at')
        return jsonify({
            "success": True,
            "assessments": [assessment.to_dict() for assessment in assessments]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/students", methods=["GET"])
def get_students():
    """Get all students"""
    try:
        students = Student.objects()
        return jsonify({
            "success": True,
            "students": [student.to_dict() for student in students]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/download_excel", methods=["GET"])
def download_excel():
    """Download last assessment results as Excel"""
    results = session.get('last_assessment')
    if not results:
        return jsonify({"error": "No assessment results found"}), 404
    
    output = format_scores_results(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f"assessment_scores_{timestamp}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
