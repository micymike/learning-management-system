# This file is used in the backend to handle csv files, this csv file contains student names and their github urls.
import csv
from io import StringIO
from datetime import datetime
import pandas as pd
import io
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from flask import send_file
import os
import json

def validate_csv_headers(headers):
    """
    Validates that the CSV headers contain 'name' and 'repo_url'.
    """
    headers_lower = [h.lower() for h in headers]
    if not ('name' in headers_lower and any(('github' in h or 'repo' in h) and 'url' in h for h in headers_lower)):
        raise ValueError('CSV file must contain columns for student name and repository URL (e.g., "name" and "repo_url")')

class ScoreManager:
    def __init__(self):
        self.scores = []
        self.next_id = 1

    def add_scores(self, new_scores):
        """Add scores with unique IDs"""
        for score in new_scores:
            score['id'] = self.next_id
            self.next_id += 1
            self.scores.append(score)
        return self.scores

    def delete_score(self, score_id):
        """Delete a single score by ID"""
        self.scores = [score for score in self.scores if score['id'] != score_id]
        return self.scores

    def delete_scores(self, score_ids):
        """Delete multiple scores by IDs"""
        self.scores = [score for score in self.scores if score['id'] not in score_ids]
        return self.scores

    def get_scores(self):
        """Get all scores"""
        return self.scores

    def clear_scores(self):
        """Clear all scores"""
        self.scores = []
        return self.scores

# Create a global instance of ScoreManager
score_manager = ScoreManager()

def process_csv(file_storage):
    """
    Accepts a Flask file storage object, parses CSV, Excel, or TXT, and returns a list of dicts with relevant student information.
    Supports multiple formats by detecting the file extension.
    """
    filename = file_storage.filename.lower()
    results = []
    print(f"Processing file: {filename}")  # Debug log

    try:
        if filename.endswith('.csv'):
            content = file_storage.read().decode('utf-8')
            print(f"CSV Content: {content}")  # Debug log
            file_storage.seek(0)
            reader = csv.reader(StringIO(content))
            headers = next(reader, [])
            validate_csv_headers(headers)

            file_storage.seek(0)
            reader = csv.reader(StringIO(content))
            headers = next(reader, [])
            headers_lower = [h.lower() for h in headers]
            for row in reader:
                if not any(row):
                    continue
                row_dict = {headers[i]: value for i, value in enumerate(row) if i < len(headers)}
                student_data = {}
                for header, value in row_dict.items():
                    if 'name' in header.lower():
                        student_data['name'] = value.strip()
                    elif any(x in header.lower() for x in ['github', 'repo']) and 'url' in header.lower():
                        student_data['repo_url'] = value.strip()
                    elif 'group' in header.lower():
                        student_data['group'] = value.strip()
                    elif 'project' in header.lower():
                        student_data['project_name'] = value.strip()
                    elif 'deployed' in header.lower() and 'url' in header.lower():
                        student_data['deployed_url'] = value.strip()
                if 'name' in student_data and 'repo_url' in student_data:
                    results.append(student_data)
            if not results:
                raise ValueError('No student data found in CSV with required columns (name, repo_url)')
            return results

        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_storage)
            headers = df.columns.tolist()
            validate_csv_headers(headers)
            for _, row in df.iterrows():
                student_data = {}
                for col in df.columns:
                    col_lower = col.lower()
                    value = str(row[col]) if not pd.isnull(row[col]) else ''
                    if 'name' in col_lower:
                        student_data['name'] = value.strip()
                    elif 'github' in col_lower and 'url' in col_lower:
                        student_data['repo_url'] = value.strip()
                    elif 'group' in col_lower:
                        student_data['group'] = value.strip()
                    elif 'project' in header.lower():
                        student_data['project_name'] = value.strip()
                    elif 'deployed' in header.lower() and 'url' in header.lower():
                        student_data['deployed_url'] = value.strip()
                if 'name' in student_data and 'repo_url' in student_data:
                    results.append(student_data)
            if not results:
                raise ValueError('No student data found in Excel with required columns (name, repo_url)')
            return results

        elif filename.endswith('.txt'):
            content = file_storage.read().decode('utf-8')
            file_storage.seek(0)
            reader = csv.reader(StringIO(content), delimiter='\t')
            try:
                headers = next(reader, [])
                validate_csv_headers(headers)
                if len(headers) < 2:
                    file_storage.seek(0)
                    reader = csv.reader(StringIO(content), delimiter=',')
                    headers = next(reader, [])
            except Exception:
                return []
            headers_lower = [h.lower() for h in headers]
            for row in reader:
                if not any(row):
                    continue
                row_dict = {headers[i]: value for i, value in enumerate(row) if i < len(headers)}
                student_data = {}
                for header, value in row_dict.items():
                    if 'name' in header.lower():
                        student_data['name'] = value.strip()
                    elif 'github' in header.lower() and 'url' in header.lower():
                        student_data['repo_url'] = value.strip()
                    elif 'group' in header.lower():
                        student_data['group'] = value.strip()
                    elif 'project' in header.lower():
                        student_data['project_name'] = value.strip()
                    elif 'deployed' in header.lower() and 'url' in header.lower():
                        student_data['deployed_url'] = value.strip()
                if 'name' in student_data and 'repo_url' in student_data:
                    results.append(student_data)
            if not results:
                raise ValueError('No student data found in TXT with required columns (name, repo_url)')
            return results
        else:
            raise ValueError('Unsupported file type. Please upload a .csv, .xlsx, .xls, or .txt file.')

    except Exception as e:
        raise ValueError(f"Error processing CSV file: {str(e)}")

def generate_scores_excel(scores):
    """
    Generate a highly presentable Excel file with student scores.
    Enhanced with better formatting, consistent styling, and improved readability.
    """
    
    # Helper to flatten a single student's scores
    def flatten_student_score(student):
        row = {
            "Name": student.get("name", ""),
            "Repository": student.get("repo_url", ""),
        }
        
        # Process scores data
        scores_obj = student.get("scores", {})
        extracted = scores_obj.get("extracted_scores", []) if isinstance(scores_obj, dict) else []
        
        criterion_count = 0
        other_details = []
        
        if extracted:
            for i, score in enumerate(extracted):
                context = score.get("context", "")
                
                # Check if this is a main criterion
                if (context.strip().lower().startswith("main criterion") or 
                    context.strip().lower().startswith("criterion")):

                    criterion_count += 1
                    # Extract the actual criterion name (e.g., "Correctness of Code", "Code Structure", etc.)
                    crit_name = None
                    # Try to extract between first colon and last colon (e.g., "Main Criterion: Correctness of Code: 8/12")
                    parts = context.split(":")
                    if len(parts) >= 3:
                        crit_name = parts[1].strip()
                    elif len(parts) == 2:
                        crit_name = parts[0].replace("Main Criterion", "").replace("Criterion", "").strip()
                    else:
                        crit_name = f"Criterion {criterion_count}"

                    # Fallback if extraction fails
                    if not crit_name or crit_name.isdigit():
                        crit_name = f"Criterion {criterion_count}"

                    # Add score information
                    if "score" in score and "max_score" in score:
                        row[f"{crit_name} Score"] = f"{score['score']}/{score['max_score']}"
                        percentage = score.get('percentage', 0)
                        row[f"{crit_name} %"] = f"{round(percentage, 1)}%"
                    elif "percentage" in score:
                        percentage = score.get('percentage', 0)
                        row[f"{crit_name} %"] = f"{round(percentage, 1)}%"

                    # Add justification
                    # Use the text after the last colon as justification, if available
                    if ":" in context:
                        justification = context.split(":")[-1].strip()
                        # Limit justification length for better display
                        if len(justification) > 200:
                            justification = justification[:200] + "..."
                        row[f"{crit_name} Notes"] = justification
                    
                else:
                    # Collect other details, but filter out code fragments and color values
                    ctx = context.strip()
                    if (
                        ctx
                        and not ctx.lower().startswith("mint:")
                        and not ctx.lower().startswith("'0%':")
                        and not ctx.lower().startswith("'80%':")
                        and not ctx.lower().startswith("'100%':")
                        and not ctx.lower().startswith("primary:")
                        and not ctx.lower().startswith("module.exports")
                        and not ctx.lower().startswith("plugins:")
                        and not ctx.lower().startswith("content:")
                        and not ctx.lower().startswith("dark:")
                        and not ctx.lower().startswith("deep-dark:")
                        and not ctx.lower().startswith("light-gray:")
                        and not ctx.lower().startswith("hsl(")
                        and not ctx.lower().startswith("#")
                        and not ctx.lower().startswith("{")
                        and not ctx.lower().startswith("}")
                        and not ctx.lower().startswith("[")
                        and not ctx.lower().startswith("]")
                    ):
                        other_details.append(ctx)
            
            # Always add summary: use summary if present, otherwise use raw_assessment
            summary = scores_obj.get("summary", "")
            if not summary:
                summary = scores_obj.get("raw_assessment", "")
            if summary is None:
                summary = ""
            if len(summary) > 300:
                summary = summary[:300] + "..."
            row["Summary"] = summary
            
            # Add other details if any
            
                
        else:
            # Fallback: use raw assessment
            raw = scores_obj.get("raw_assessment") if isinstance(scores_obj, dict) else None
            if raw:
                if len(raw) > 300:
                    raw = raw[:300] + "..."
                row["Assessment"] = raw
        
        return row

    # Flatten all students
    flat_rows = [flatten_student_score(s) for s in scores]
    
    # Create DataFrame
    df = pd.DataFrame(flat_rows)
    
    # Remove any unwanted columns
    unwanted = ["raw_assessment", "rubric_type", "extracted_scores", "total_assessment"]
    for col in unwanted:
        if col in df.columns:
            df = df.drop(col, axis=1)
    
    # Ensure Name and Repository are first, then organize other columns logically
    first_cols = ["Name", "Repository"]
    score_cols = [col for col in df.columns if "Score" in col]
    percent_cols = [col for col in df.columns if "%" in col]
    note_cols = [col for col in df.columns if "Notes" in col]
    summary_cols = [col for col in df.columns if col in ["Summary", "Assessment"]]
    
    # Reorder columns for better readability
    ordered_cols = []
    for col in first_cols:
        if col in df.columns:
            ordered_cols.append(col)
    
    # Group criteria columns together (Score, %, Notes for each criterion)
    criteria_names = set()
    for col in score_cols + percent_cols + note_cols:
        if "Score" in col:
            criteria_names.add(col.replace(" Score", ""))
        elif "%" in col:
            criteria_names.add(col.replace(" %", ""))
        elif "Notes" in col:
            criteria_names.add(col.replace(" Notes", ""))
    
    # Add criteria columns in logical order
    for crit in sorted(criteria_names):
        for suffix in [" Score", " %", " Notes"]:
            col_name = crit + suffix
            if col_name in df.columns:
                ordered_cols.append(col_name)
    
    # Add summary columns at the end
    for col in summary_cols:
        if col in df.columns:
            ordered_cols.append(col)
    
    # Reorder DataFrame
    df = df[ordered_cols]
    
    # Create Excel file
    output = io.BytesIO()
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Student Scores'
    
    # Add data to worksheet
    for r in dataframe_to_rows(df, index=False, header=True):
        worksheet.append(r)
    
    # Define styles
    header_fill = PatternFill(start_color='2E5984', end_color='2E5984', fill_type='solid')
    header_font = Font(color='FFFFFF', bold=True, size=11)
    
    # Alternating row colors
    light_fill = PatternFill(start_color='F8F9FA', end_color='F8F9FA', fill_type='solid')
    white_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
    
    # Special column fills
    name_fill = PatternFill(start_color='E3F2FD', end_color='E3F2FD', fill_type='solid')
    score_fill = PatternFill(start_color='E8F5E8', end_color='E8F5E8', fill_type='solid')
    summary_fill = PatternFill(start_color='FFF8E1', end_color='FFF8E1', fill_type='solid')
    
    # Fonts
    name_font = Font(bold=True, color='1565C0', size=10)
    score_font = Font(bold=True, color='2E7D32', size=10)
    summary_font = Font(color='F57C00', size=9)
    regular_font = Font(size=9)
    
    # Borders
    thin_border = Border(
        left=Side(style='thin', color='D1D5DB'),
        right=Side(style='thin', color='D1D5DB'),
        top=Side(style='thin', color='D1D5DB'),
        bottom=Side(style='thin', color='D1D5DB')
    )
    
    # Format header row
    for col_num, col_name in enumerate(df.columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    
    # Format data rows
    for row_num in range(2, worksheet.max_row + 1):
        # Determine row fill color
        row_fill = light_fill if (row_num - 2) % 2 == 0 else white_fill
        
        for col_num, col_name in enumerate(df.columns, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.border = thin_border
            
            # Column-specific formatting
            if col_name == "Name":
                cell.fill = name_fill
                cell.font = name_font
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif col_name == "Repository":
                cell.fill = name_fill
                cell.font = Font(size=9, color='1565C0')
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif "Score" in col_name or "%" in col_name:
                cell.fill = score_fill
                cell.font = score_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_name in ["Summary", "Additional Notes", "Assessment"]:
                cell.fill = summary_fill
                cell.font = summary_font
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            else:
                cell.fill = row_fill
                cell.font = regular_font
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    
    # Adjust column widths
    column_widths = {}
    for col_num, col_name in enumerate(df.columns, 1):
        if col_name == "Name":
            width = 20
        elif col_name == "Repository":
            width = 35
        elif "Score" in col_name or "%" in col_name:
            width = 12
        elif col_name in ["Summary", "Additional Notes", "Assessment"]:
            width = 40
        elif "Notes" in col_name:
            width = 35
        else:
            width = 25
        
        column_widths[col_num] = width
        worksheet.column_dimensions[worksheet.cell(row=1, column=col_num).column_letter].width = width
    
    # Set row heights for better readability
    worksheet.row_dimensions[1].height = 25  # Header row
    for row_num in range(2, worksheet.max_row + 1):
        worksheet.row_dimensions[row_num].height = 30  # Data rows
    
    # Freeze panes (header row and first two columns)
    worksheet.freeze_panes = 'C2'
    
    # Add auto-filter
    worksheet.auto_filter.ref = f"A1:{worksheet.cell(row=1, column=len(df.columns)).coordinate}"
    
    # Save workbook
    workbook.save(output)
    output.seek(0)
    
    return output

def format_scores_for_display(scores):
    """
    Format scores data for display in the web interface
    """
    # Create a simplified version for web display
    display_data = []
    
    for student in scores:
        row = {
            "Name": student.get("name", ""),
            "Repository": student.get("repo_url", "")
        }
        
        scores_obj = student.get("scores", {})
        extracted = scores_obj.get("extracted_scores", []) if isinstance(scores_obj, dict) else []
        
        if extracted:
            # Get overall percentage if available
            percentages = [s.get('percentage', 0) for s in extracted if 'percentage' in s]
            if percentages:
                avg_percentage = sum(percentages) / len(percentages)
                row["Overall Score"] = f"{round(avg_percentage, 1)}%"
            
            # Get summary
            summary = scores_obj.get("summary", "")
            if summary:
                row["Summary"] = summary[:100] + "..." if len(summary) > 100 else summary
        
        display_data.append(row)
    
    df = pd.DataFrame(display_data)
    return df.to_html(
        classes=['table', 'table-striped', 'table-bordered', 'table-hover'],
        index=False,
        escape=False,
        table_id='scores-table'
    )
