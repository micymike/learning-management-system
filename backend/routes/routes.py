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

    scores_data = []
    for result in results:
        # Basic student info
        scores = {
            'Name': result['name'],
            'Repository': result['repo_url']
        }
        
        # Check if we have the new format with criteria_scores
        if 'scores' in result and isinstance(result['scores'], dict):
            if 'criteria_scores' in result['scores']:
                # New format with points
                criteria_scores = result['scores']['criteria_scores']
                for criterion, data in criteria_scores.items():
                    scores[f"{criterion} (Points)"] = f"{data.get('points', 0)}/{data.get('max_points', 0)}"
                    if 'justification' in data:
                        scores[f"{criterion} (Justification)"] = data['justification']
                
                # Add summary data
                scores['Total Points'] = f"{result['scores'].get('total_points', 0)}/{result['scores'].get('max_points', 0)}"
                scores['Percentage'] = f"{result['scores'].get('percentage', 0)}%"
                scores['Status'] = "PASS" if result['scores'].get('passing', False) else "FAIL"
            else:
                # Legacy format or simple scores
                for criterion, score_value in result['scores'].items():
                    # Check if this is a structured score with mark and justification
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
        
        # Format justification columns to wrap text
        for col in range(len(df.columns)):
            column_name = df.columns[col]
            if 'Justification' in column_name:
                for row in range(2, len(df) + 2):  # Start from row 2 (after header)
                    cell = worksheet.cell(row=row, column=col + 1)
                    cell.alignment = Alignment(wrap_text=True, vertical='top')
        
        # Auto-adjust columns
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            column_letter = column[0].column_letter
            
            # Special handling for justification columns - limit width
            if 'Justification' in str(worksheet.cell(row=1, column=column[0].column).value):
                worksheet.column_dimensions[column_letter].width = 50  # Fixed width for justifications
            else:
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 40)  # Cap width at 40 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
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

@routes_blueprint.route("/rubric_templates", methods=["GET"])
def get_rubric_templates():
    """Get available rubric templates"""
    templates = [
        {
            "name": "Standard Rubric",
            "path": "sample_rubric.txt",
            "description": "Basic rubric with points for each criterion"
        },
        {
            "name": "Structured Module Exam Rubric",
            "path": "structured_rubric_example.txt",
            "description": "Comprehensive rubric with detailed criteria and point allocation"
        }
    ]
    
    return jsonify({
        "success": True,
        "templates": templates
    })

@routes_blueprint.route("/rubric_templates/<template_name>", methods=["GET"])
def get_rubric_template(template_name):
    """Get a specific rubric template content"""
    template_path = None
    
    if template_name == "standard":
        template_path = "sample_rubric.txt"
    elif template_name == "structured":
        template_path = "structured_rubric_example.txt"
    else:
        return jsonify({"error": "Template not found"}), 404
    
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), template_path), 'r') as f:
            content = f.read()
        
        # Parse rubric to get points information
        try:
            rubric_items = parse_rubric_lines(content.strip().split('\n'))
            total_points = sum(item['max_points'] for item in rubric_items)
            passing_threshold = total_points * 0.8  # 80% passing threshold
            
            return jsonify({
                "success": True,
                "template_name": template_name,
                "content": content,
                "parsed_rubric": rubric_items,
                "total_points": total_points,
                "passing_threshold": passing_threshold
            })
        except:
            # If parsing fails, still return the content
            return jsonify({
                "success": True,
                "template_name": template_name,
                "content": content
            })
    except Exception as e:
        return jsonify({"error": f"Error reading template: {str(e)}"}), 500

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
    
    # Parse rubric to get criteria with points
    try:
        rubric_items = parse_rubric_lines(rubric.strip().split('\n'))
        result = assess_code(code, rubric_items, client)
    except Exception as e:
        # If parsing fails, use the raw rubric text
        result = assess_code(code, rubric, client)
    
    return jsonify({
        "result": result,
        "passing": result.get('passing', False),
        "percentage": result.get('percentage', 0),
        "total_points": result.get('total_points', 0),
        "max_points": result.get('max_points', 0)
    })

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
    student_assessments = []  # Store assessments to be added later
    for student in students:
        name = student['name']
        repo_url = student['repo_url']
        
        # Find or create student record
        student_record = Student.objects(name=name).first()
        if not student_record:
            student_record = Student(name=name)
            student_record.save()
        
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
        if isinstance(assessment, dict):
            scores = assessment
        else:
            # Legacy format handling
            assessment_lines = [line.strip() for line in assessment.split('\n')]
            scores = {
                'criteria_scores': {},
                'total_points': 0,
                'max_points': 0,
                'percentage': 0,
                'passing': False
            }
            
            for line in assessment_lines:
                if ',' in line:
                    try:
                        criterion, score = line.split(',', 1)
                        points = int(score.strip())
                        scores['criteria_scores'][criterion.strip()] = {
                            'points': points,
                            'max_points': 10  # Default max points
                        }
                        scores['total_points'] += points
                        scores['max_points'] += 10
                    except (ValueError, TypeError):
                        continue
            
            # Calculate percentage and passing status
            if scores['max_points'] > 0:
                from rubric_handler import calculate_percentage, is_passing_grade
                scores['percentage'] = calculate_percentage(scores['total_points'], scores['max_points'])
                scores['passing'] = is_passing_grade(scores['percentage'])
        
        # Store student assessment for later
        student_assessments.append({
            "student": student_record,
            "scores": scores,
            "repo_url": repo_url,
            "submission": code_str
        })
        
        # Add assessment to results with pass/fail status
        result_entry = {
            "name": name,
            "repo_url": repo_url,
            "scores": scores
        }
        
        # Add assessment data for frontend display
        if 'percentage' in scores:
            result_entry['assessment'] = {
                'total_points': scores.get('total_points', 0),
                'max_points': scores.get('max_points', 0),
                'percentage': scores.get('percentage', 0),
                'passing': scores.get('passing', False)
            }
        
        results.append(result_entry)
    
    # Store results in session for later download
    session['last_assessment'] = results
    
    # Save to database
    try:
        # Create a new assessment record first
        new_assessment = Assessment(
            name=assessment_name,
            rubric=rubric,
            results=results
        )
        new_assessment.save()
        
        # Now create student assessment records with the assessment ID
        for student_data in student_assessments:
            student_assessment = StudentAssessment(
                student=student_data["student"],
                assessment=new_assessment,
                scores=student_data["scores"],
                repo_url=student_data["repo_url"],
                submission=student_data["submission"]
            )
            student_assessment.save()
        
        return jsonify({
            "success": True, 
            "results": results,
            "assessment": {
                "id": str(new_assessment.id),
                "name": new_assessment.name,
                "date": new_assessment.date.isoformat() if new_assessment.date else None,
                "created_at": new_assessment.created_at.isoformat()
            },
            "message": f"Successfully processed {len(results)} student submissions"
        })
    except Exception as e:
        return jsonify({
            "error": f"Error saving assessment to database: {str(e)}",
            "results": results  # Still return results even if DB save fails
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
        return jsonify({"error": f"Error retrieving assessments: {str(e)}"}), 500

@routes_blueprint.route("/assessments/<assessment_id>", methods=["GET"])
def get_assessment(assessment_id):
    """Get a specific assessment by ID"""
    try:
        assessment = Assessment.objects(id=assessment_id).first()
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

@routes_blueprint.route("/download_excel/<assessment_id>", methods=["GET"])
def download_assessment_excel(assessment_id):
    """Download Excel for a specific assessment"""
    try:
        assessment = Assessment.objects(id=assessment_id).first()
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
        
        # Parse rubric to extract criteria and points
        try:
            rubric_items = parse_rubric_lines(rubric.strip().split('\n'))
            total_points = sum(item['max_points'] for item in rubric_items)
            passing_threshold = total_points * 0.8  # 80% passing threshold
            
            return jsonify({
                "success": True, 
                "rubric": rubric,
                "parsed_rubric": rubric_items,
                "total_points": total_points,
                "passing_threshold": passing_threshold
            })
        except Exception as e:
            # If parsing fails, still return the raw rubric
            return jsonify({
                "success": True, 
                "rubric": rubric,
                "warning": f"Could not parse rubric points: {str(e)}"
            })
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
        total_students = Student.objects().count()
        total_assessments = Assessment.objects().count()
        
        # Calculate average score across all student assessments
        avg_percentage = None
        total_percentage = 0
        passing_count = 0
        assessment_count = 0
        student_assessments = StudentAssessment.objects()
        
        for sa in student_assessments:
            if sa.scores:  # Check if scores dictionary exists
                assessment_count += 1
                
                # Check if we have the new format with percentage
                if isinstance(sa.scores, dict) and 'percentage' in sa.scores:
                    total_percentage += sa.scores['percentage']
                    if sa.scores.get('passing', False):
                        passing_count += 1
                # Legacy format
                else:
                    percentage = sa._calculate_average_score()
                    total_percentage += percentage
                    if percentage >= 80:  # 80% passing threshold
                        passing_count += 1
        
        if assessment_count > 0:
            avg_percentage = round(total_percentage / assessment_count, 2)
            passing_rate = round((passing_count / assessment_count) * 100, 2)
            
        return jsonify({
            "success": True,
            "total_students": total_students,
            "total_assessments": total_assessments,
            "average_percentage": avg_percentage,
            "passing_count": passing_count,
            "passing_rate": f"{passing_rate}%" if assessment_count > 0 else "N/A"
        })
    except Exception as e:
        print(f"Analytics error: {str(e)}")  # Add logging for debugging
        return jsonify({"success": False, "error": str(e)}), 500

# Student routes
@routes_blueprint.route("/students", methods=["GET"])
def get_students():
    """Get all students with their assessment counts"""
    try:
        students = Student.objects()
        return jsonify({
            "success": True,
            "students": [student.to_dict() for student in students]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/students/<student_id>", methods=["GET"])
def get_student(student_id):
    """Get a specific student with their assessment history"""
    try:
        student = Student.objects(id=student_id).first()
        if not student:
            return jsonify({"error": f"Student with ID {student_id} not found"}), 404
        
        return jsonify({
            "success": True,
            "student": student.to_dict_with_assessments()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500