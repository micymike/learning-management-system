"""
This file defines the routes for the application
"""
from flask import Blueprint, request, jsonify, send_file, session
from flask_cors import CORS
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
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
import hashlib
import colorsys

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

def generate_color_for_criterion(criterion_name):
    """Generate a consistent color for a criterion based on its name"""
    # Create a hash of the criterion name for consistency
    hash_obj = hashlib.md5(criterion_name.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Use the first 6 characters as RGB values
    r = int(hash_hex[0:2], 16)
    g = int(hash_hex[2:4], 16)
    b = int(hash_hex[4:6], 16)
    
    # Adjust saturation and lightness for better appearance
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    s = max(0.4, min(0.8, s))  # Ensure reasonable saturation
    v = max(0.7, min(0.9, v))  # Ensure reasonable brightness
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    
    # Convert back to hex
    return f"{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"

def format_scores_results(results):
    """
    Format scores into a beautifully styled pandas DataFrame and save as Excel
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

    # Generate colors for each criterion
    criterion_colors = {}
    for criterion in criteria:
        criterion_colors[criterion] = generate_color_for_criterion(criterion)

    scores_data = []
    for result in results:
        student_data = {
            'Name': result['name'],
            'Repository': result['repo_url'],
            'Average Score': 'N/A',
            'Percentage': 'N/A',
            'Pass/Fail': 'N/A'
        }

        total_score = 0
        valid_criteria_count = 0
        criterion_scores = {}

        # Add all criteria scores, properly formatting structured scores
        for criterion in criteria:
            score_value = result.get('scores', {}).get(criterion, 0)

            # Check if this is a structured score with mark and justification
            if isinstance(score_value, dict) and 'mark' in score_value:
                mark = score_value.get('mark', 'N/A')
                justification = score_value.get('justification', '')
                criterion_scores[criterion] = mark
                criterion_scores[f'{criterion} (Justification)'] = justification

                # Try to convert mark to a number for averaging
                try:
                    numeric_mark = float(mark)
                    total_score += numeric_mark
                    valid_criteria_count += 1
                except ValueError:
                    print(f"Warning: Could not convert mark '{mark}' for criterion '{criterion}' to a number for averaging.")
            else:
                criterion_scores[criterion] = score_value
                # Try to convert score_value to a number for averaging
                try:
                    numeric_score = float(score_value)
                    total_score += numeric_score
                    valid_criteria_count += 1
                except ValueError:
                    print(f"Warning: Could not convert score '{score_value}' for criterion '{criterion}' to a number for averaging.")

        # Calculate average score and percentage
        if valid_criteria_count > 0:
            average_score = total_score / valid_criteria_count
            percentage = (average_score / 5) * 100  # Assuming max score is 5
            student_data['Average Score'] = round(average_score, 2)
            student_data['Percentage'] = round(percentage, 2)
            student_data['Pass/Fail'] = 'Pass' if percentage >= 80 else 'Fail'

        # Combine student data and criterion scores
        combined_data = {**student_data, **criterion_scores}
        scores_data.append(combined_data)

    df = pd.DataFrame(scores_data)
    
    # Define column order
    column_order = ['Name', 'Repository', 'Average Score', 'Percentage', 'Pass/Fail'] + [
        col for col in df.columns if col not in ['Name', 'Repository', 'Average Score', 'Percentage', 'Pass/Fail']
    ]
    df = df[column_order]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Assessment Results')
        worksheet = writer.sheets['Assessment Results']

        # Apply beautiful styling
        style_assessment_sheet(worksheet, df, criteria, criterion_colors)

    output.seek(0)
    return output

def style_assessment_sheet(worksheet, df, criteria, criterion_colors):
    """Apply beautiful styling to the assessment results sheet"""
    
    # Define styles
    header_font = Font(bold=True, color='FFFFFF', size=11)
    data_font = Font(size=10)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_alignment = Alignment(horizontal='center', vertical='center')
    wrap_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_wrap_alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    
    # Style basic info headers
    basic_info_fill = PatternFill(start_color='4A90E2', end_color='4A90E2', fill_type='solid')
    basic_columns = 5  # Name, Repository, Average Score, Percentage, Pass/Fail
    
    # Style basic info headers
    for col in range(1, basic_columns + 1):
        cell = worksheet.cell(row=1, column=col)
        cell.font = header_font
        cell.fill = basic_info_fill
        cell.border = thin_border
        cell.alignment = wrap_alignment
    
    # Style criterion headers with their respective colors
    col_index = basic_columns + 1
    for col in range(basic_columns + 1, len(df.columns) + 1):
        cell = worksheet.cell(row=1, column=col)
        column_name = df.columns[col - 1]
        
        # Find the criterion this column belongs to
        criterion_found = None
        for criterion in criteria:
            if criterion in column_name:
                criterion_found = criterion
                break
        
        if criterion_found and criterion_found in criterion_colors:
            color = criterion_colors[criterion_found]
            criterion_fill = PatternFill(start_color=color, end_color=color, fill_type='solid')
            cell.fill = criterion_fill
        else:
            # Default color for unmatched columns
            cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
        
        cell.font = header_font
        cell.border = thin_border
        cell.alignment = wrap_alignment
    
    # Style data rows
    for row in range(2, len(df) + 2):
        for col in range(1, len(df.columns) + 1):
            cell = worksheet.cell(row=row, column=col)
            cell.font = data_font
            cell.border = thin_border
            
            column_name = df.columns[col - 1]
            
            # Special alignment for justification columns
            if 'Justification' in column_name:
                cell.alignment = left_wrap_alignment
            else:
                cell.alignment = center_alignment
            
            # Add alternating row colors for better readability
            if row % 2 == 0:
                cell.fill = PatternFill(start_color='F8F9FA', end_color='F8F9FA', fill_type='solid')
    
    # Set column widths
    for col in range(1, len(df.columns) + 1):
        column_letter = get_column_letter(col)
        column_name = df.columns[col - 1]
        
        if column_name in ['Name', 'Repository']:
            worksheet.column_dimensions[column_letter].width = 30
        elif column_name in ['Average Score', 'Percentage', 'Pass/Fail']:
            worksheet.column_dimensions[column_letter].width = 15
        elif 'Justification' in column_name:
            worksheet.column_dimensions[column_letter].width = 50
        else:
            # For criterion score columns
            worksheet.column_dimensions[column_letter].width = 12
    
    # Set row height for header
    worksheet.row_dimensions[1].height = 25

# Add routes to the blueprint
@routes_blueprint.route('/api/assess', methods=['POST'])
def assess():
    """Assess code using the AI model"""
    try:
        data = request.json
        code = data.get('code')
        rubric = data.get('rubric')
        use_rag = data.get('use_rag', False)
        
        if not code:
            return jsonify({"error": "No code provided"}), 400
        
        if not rubric:
            return jsonify({"error": "No rubric provided"}), 400
        
        # Assess the code
        result = assess_code(code, rubric, client, use_rag=use_rag)
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/api/analyze-repo', methods=['POST'])
def analyze_repo():
    """Analyze a GitHub repository"""
    try:
        data = request.json
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({"error": "No repository URL provided"}), 400
        
        # Analyze the repository
        code = analyze_github_repo(repo_url)
        
        return jsonify({"success": True, "code": code})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/api/process-csv', methods=['POST'])
def process_csv_route():
    """Process a CSV file with student data"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save the file temporarily
        temp_path = f"temp_{datetime.now().timestamp()}.csv"
        file.save(temp_path)
        
        # Process the CSV
        students = process_csv(temp_path)
        
        # Remove the temporary file
        os.remove(temp_path)
        
        return jsonify({"success": True, "students": students})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/api/rubric', methods=['GET'])
def get_rubric():
    """Get the current rubric"""
    try:
        rubric = load_rubric()
        return jsonify({"success": True, "rubric": rubric})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/api/export-results', methods=['POST'])
def export_results():
    """Export assessment results as Excel"""
    try:
        data = request.json
        results = data.get('results')
        
        if not results:
            return jsonify({"error": "No results provided"}), 400
        
        # Format the results
        output = format_scores_results(results)
        
        # Return the Excel file
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='assessment_results.xlsx'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500