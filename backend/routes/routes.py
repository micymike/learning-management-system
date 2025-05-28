"""
This file defines the routes for the application
"""
from flask import Blueprint, request, jsonify, send_file, session, current_app
from flask_cors import CORS, cross_origin
from openpyxl.styles import PatternFill, Font, Alignment
import io
import pandas as pd
import os
import json
from datetime import datetime
from AI_assessor import assess_code
from repo_analyzer import analyze_github_repo
from csv_analyzer import process_csv
from rubric_handler import upload_rubric_file, calculate_percentage, is_passing_grade
import openai
from dotenv import load_dotenv
from models import Assessment, Student, StudentAssessment

load_dotenv()

# Initialize routes blueprint
routes_blueprint = Blueprint('routes', __name__)

@routes_blueprint.route("/upload_csv", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
def upload_csv():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = current_app.make_default_options_response()
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.set('Access-Control-Allow-Methods', 'POST')
        response.headers.set('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response
    """Handle CSV and rubric file upload"""
    try:
        print("\n=== Starting upload_csv request ===")
        print("Request headers:", dict(request.headers))
        print("Request form:", dict(request.form))
        print("Request files keys:", list(request.files.keys()))
        print("Content-Type:", request.headers.get('Content-Type', 'Not provided'))
        print("Content-Length:", request.headers.get('Content-Length', 'Not provided'))
        
        # Log detailed information about each file
        for key in request.files:
            file = request.files[key]
            print(f"File {key} details:", {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": file.tell() if hasattr(file, 'tell') else 'Unknown',
                "headers": dict(file.headers) if hasattr(file, 'headers') else None
            })
            # Reset file pointer if we used tell()
            if hasattr(file, 'tell') and hasattr(file, 'seek'):
                file.seek(0)

        # Get files from request
        file_keys = list(request.files.keys())
        print(f"Found {len(file_keys)} files with keys: {file_keys}")
        
        # Try to identify CSV and rubric files by name or content type
        csv_file = None
        rubric_file = None
        
        # First try to get files by expected keys
        if 'file' in request.files:
            csv_file = request.files.get('file')
            print(f"Found CSV file with key 'file': {csv_file.filename}")
        
        if 'rubric' in request.files:
            rubric_file = request.files.get('rubric')
            print(f"Found rubric file with key 'rubric': {rubric_file.filename}")
            
        # If not found, try to identify by content type or filename
        if not csv_file or not rubric_file:
            for key, file in request.files.items():
                if not csv_file and (
                    'csv' in file.filename.lower() or 
                    'text/csv' in file.content_type.lower() or
                    'spreadsheet' in file.content_type.lower()
                ):
                    csv_file = file
                    print(f"Identified CSV file by content: {key} -> {file.filename}")
                elif not rubric_file and (
                    'rubric' in file.filename.lower() or
                    'excel' in file.content_type.lower() or
                    'xlsx' in file.filename.lower() or
                    'spreadsheet' in file.content_type.lower()
                ):
                    rubric_file = file
                    print(f"Identified rubric file by content: {key} -> {file.filename}")
        
        # If still not found and we have exactly two files, use them in order
        if (not csv_file or not rubric_file) and len(file_keys) == 2:
            if not csv_file:
                csv_file = request.files.get(file_keys[0])
                print(f"Using first file as CSV: {file_keys[0]} -> {csv_file.filename}")
            if not rubric_file:
                rubric_file = request.files.get(file_keys[1])
                print(f"Using second file as rubric: {file_keys[1]} -> {rubric_file.filename}")
        
        # Detailed logging for debugging
        if csv_file:
            print(f"CSV file received: {csv_file.filename}, type: {csv_file.content_type}")
        else:
            print("No CSV file found in request")
            
        if rubric_file:
            print(f"Rubric file received: {rubric_file.filename}, type: {rubric_file.content_type}")
        else:
            print("No rubric file found in request")
            
        # Check for required files
        if not csv_file or not rubric_file:
            error_msg = f"Must provide both CSV and rubric files. Got: CSV={bool(csv_file)}, Rubric={bool(rubric_file)}"
            print("Error:", error_msg)
            print("Available files:", list(request.files.keys()))
            
            # Detailed debug information
            print("Request form data:", dict(request.form))
            print("Request content type:", request.content_type)
            print("Request mimetype:", request.mimetype)
            print("Request is multipart:", request.is_multipart)
            
            # Check if we have any files at all
            file_keys = list(request.files.keys())
            if len(file_keys) > 0:
                print(f"Found {len(file_keys)} files but not identified as 'file' and 'rubric'")
                print(f"Actual file keys: {file_keys}")
                
                # Try to use the available files
                if len(file_keys) >= 2:
                    print("Attempting to use the first two files as CSV and rubric")
                    if not csv_file:
                        csv_file = request.files.get(file_keys[0])
                        print(f"Using {file_keys[0]} as CSV file: {csv_file.filename}")
                    if not rubric_file:
                        rubric_file = request.files.get(file_keys[1])
                        print(f"Using {file_keys[1]} as rubric file: {rubric_file.filename}")
                    # Continue with processing
                elif len(file_keys) == 1:
                    # If we only have one file, try to determine which one it is
                    file = request.files.get(file_keys[0])
                    print(f"Only one file found: {file_keys[0]} -> {file.filename}")
                    
                    # No default rubric - both files are required
                    if not rubric_file:
                        return jsonify({
                            "error": "Rubric file is required. No default rubric will be used.", 
                            "available_files": list(request.files.keys()),
                            "form_data": dict(request.form)
                        }), 400
                        
                        # Assume the file we have is the CSV
                        csv_file = file
                        print(f"Using {file_keys[0]} as CSV file but rubric is required")
                    elif not csv_file:
                        # If we have a rubric but no CSV, we can't proceed
                        return jsonify({
                            "error": "CSV file is required", 
                            "available_files": list(request.files.keys()),
                            "form_data": dict(request.form)
                        }), 400
                else:
                    return jsonify({
                        "error": error_msg, 
                        "available_files": list(request.files.keys()),
                        "form_data": dict(request.form)
                    }), 400
            else:
                return jsonify({
                    "error": error_msg, 
                    "available_files": list(request.files.keys()),
                    "form_data": dict(request.form)
                }), 400
        
        # Get assessment name
        assessment_name = request.form.get('name', '') or f"Assessment {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        print(f"\nProcessing assessment: {assessment_name}")
        
        # Read rubric file content
        try:
            print("\nReading rubric file...")
            rubric_content = rubric_file.read()  # Read as binary
            print(f"Rubric content length: {len(rubric_content)} bytes")
            print("Rubric content type:", type(rubric_content))
            print(f"Rubric filename: {rubric_file.filename}")
            print(f"Rubric content type from file: {rubric_file.content_type}")

            try:
                # Add more detailed debug logging
                print(f"Rubric file type: {rubric_file.content_type}")
                print(f"Rubric file name: {rubric_file.filename}")
                print(f"First 100 bytes of rubric content: {rubric_content[:100]}")
                
                # Try to decode and print the content if it's text
                try:
                    if 'text' in rubric_file.content_type or '.txt' in rubric_file.filename.lower():
                        print(f"Rubric text content: {rubric_content.decode('utf-8')[:500]}")
                except Exception as decode_err:
                    print(f"Could not decode rubric content: {decode_err}")
                
                rubric_items = upload_rubric_file(rubric_content)
                if not rubric_items:
                    error_msg = "No valid criteria found in uploaded rubric. Please upload a valid rubric file."
                    print("Error:", error_msg)
                    return jsonify({"error": error_msg}), 400
            except Exception as e:
                error_msg = f"Error processing rubric: {str(e)}"
                print("Error:", error_msg)
                return jsonify({"error": error_msg}), 400
                
            print("\nParsed rubric items:")
            print(json.dumps(rubric_items, indent=2))
            
        except Exception as e:
            error_msg = f"Error reading rubric: {str(e)}"
            print("Error:", error_msg)
            return jsonify({"error": error_msg}), 400
        
        # Process student data
        try:
            print("\nProcessing CSV file...")
            students = process_csv(csv_file)
            if not students:
                error_msg = "No student data found in CSV"
                print("Error:", error_msg)
                return jsonify({"error": error_msg}), 400
                
            print(f"\nFound {len(students)} students")
                
        except Exception as e:
            error_msg = f"Error processing CSV: {str(e)}"
            print("Error:", error_msg)
            return jsonify({"error": error_msg}), 400
        
        results = []
        student_assessments = []
        
        # Process each studentnow 
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
                
                print(f"Retrieved code ({len(code_str)} chars)")
                
                # Assess code
                assessment = assess_code(code_str, rubric_items)
                print(f"\nAssessment results for {name}:")
                print(json.dumps(assessment, indent=2))
                
                # Store results
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
            # Save assessment
            print("\nSaving assessment to database...")
            new_assessment = Assessment(
                name=assessment_name,
                rubric=[rubric_items],
                results=results
            ).save()
            
            # Save student assessments
            print("\nSaving student assessments...")
            for data in student_assessments:
                StudentAssessment(
                    student=data["student"],
                    assessment=new_assessment,
                    scores=data["scores"],
                    repo_url=data["repo_url"],
                    submission=data["submission"]
                ).save()
            
            response_data = {
                "success": True,
                "results": results,
                "assessment": {
                    "id": str(new_assessment.id),
                    "name": new_assessment.name,
                    "date": new_assessment.date.isoformat() if new_assessment.date else None,
                    "created_at": new_assessment.created_at.isoformat()
                }
            }
            print("\nSending response:", json.dumps(response_data, indent=2))
            return jsonify(response_data)
            
        except Exception as e:
            error_msg = f"Database error: {str(e)}"
            print("Error:", error_msg)
            return jsonify({
                "error": "Database error",
                "message": str(e),
                "results": results  # Return results even if DB save fails
            }), 500
            
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print("Error:", error_msg)
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@routes_blueprint.route("/assessments", methods=["GET", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
def get_assessments():
    """Get all assessments"""
    if request.method == "OPTIONS":
        response = current_app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,X-Requested-With,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    try:
        print("Fetching all assessments")
        assessments = Assessment.objects().order_by('-created_at')
        assessment_list = []
        
        for assessment in assessments:
            assessment_dict = assessment.to_dict()
            # Add _id field for frontend compatibility
            assessment_dict['_id'] = assessment_dict['id']
            assessment_list.append(assessment_dict)
            
        print(f"Returning {len(assessment_list)} assessments")
        return jsonify({
            "success": True,
            "assessments": assessment_list
        })
    except Exception as e:
        print(f"Error in get_assessments: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/students", methods=["GET", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
def get_students():
    """Get all students"""
    if request.method == "OPTIONS":
        response = current_app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,X-Requested-With,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    try:
        print("Fetching all students")
        students = Student.objects().order_by('name')
        student_list = []
        
        for student in students:
            student_dict = {
                "id": str(student.id),
                "_id": str(student.id),
                "name": student.name,
                "email": student.email if hasattr(student, 'email') else None,
                "github_username": student.github_username if hasattr(student, 'github_username') else None
            }
            student_list.append(student_dict)
            
        print(f"Returning {len(student_list)} students")
        return jsonify({
            "success": True,
            "students": student_list
        })
    except Exception as e:
        print(f"Error in get_students: {str(e)}")
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route("/students/<student_id>", methods=["GET", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
def get_student(student_id):
    """Get a specific student by ID"""
    if request.method == "OPTIONS":
        response = current_app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,X-Requested-With,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    try:
        print(f"Fetching student with ID: {student_id}")
        student = Student.objects(id=student_id).first()
        
        if not student:
            print(f"Student with ID {student_id} not found")
            return jsonify({'error': 'Student not found'}), 404
        
        # Get student assessments
        student_assessments = StudentAssessment.objects(student=student).order_by('-created_at')
        assessments = []
        
        for sa in student_assessments:
            assessment_dict = {
                "id": str(sa.id),
                "assessment_id": str(sa.assessment.id) if sa.assessment else None,
                "assessment_name": sa.assessment.name if sa.assessment else "Unknown",
                "created_at": sa.created_at.isoformat() if sa.created_at else None,
                "repo_url": sa.repo_url,
                "scores": sa.scores
            }
            assessments.append(assessment_dict)
        
        student_dict = {
            "id": str(student.id),
            "_id": str(student.id),
            "name": student.name,
            "email": student.email if hasattr(student, 'email') else None,
            "github_username": student.github_username if hasattr(student, 'github_username') else None,
            "assessments": assessments
        }
        
        print(f"Returning student: {student.name}")
        return jsonify({
            "success": True,
            "student": student_dict
        })
    except Exception as e:
        print(f"Error fetching student: {str(e)}")
        return jsonify({'error': str(e)}), 500

@routes_blueprint.route("/assessments/<assessment_id>/excel", methods=["GET", "OPTIONS"])
def download_excel(assessment_id):
    if request.method == "OPTIONS":
        response = current_app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,Origin,X-Requested-With,Accept'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    """Download assessment results as Excel"""
    try:
        print(f"Excel download requested for assessment ID: {assessment_id}")
        
        # Validate ObjectId format
        if len(assessment_id) != 24:
            print(f"Invalid ObjectId format: {assessment_id}")
            return jsonify({"error": f"Invalid assessment ID format: {assessment_id}"}), 400
            
        # Get assessment by ID
        assessment = Assessment.objects(id=assessment_id).first()
        if not assessment:
            print(f"Assessment not found: {assessment_id}")
            return jsonify({"error": "Assessment not found"}), 404
            
        results = assessment.results
        if not results:
            print(f"No results found for assessment: {assessment_id}")
            return jsonify({"error": "No assessment results found"}), 404
        
        output = io.BytesIO()
        print(f"Processing Excel for assessment: {assessment.name}")

    except Exception as e:
        print(f"Error fetching assessment: {str(e)}")
        return jsonify({"error": "Failed to fetch assessment"}), 500
    
    try:
        # Use the improved Excel export from csv_analyzer
        from csv_analyzer import generate_scores_excel
        output = generate_scores_excel(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response = send_file(
            output,
            as_attachment=True,
            download_name=f"assessment_scores_{timestamp}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        print(f"Excel file created successfully for assessment: {assessment.name}")
        return response

    except Exception as e:
        print(f"Error creating Excel file: {str(e)}")
        return jsonify({"error": "Failed to create Excel file"}), 500
