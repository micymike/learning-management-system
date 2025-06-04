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
import re

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
    Handles real-world formats with 'First Name', 'Last Name', and long GitHub repo URL columns.
    """
    import re

    def normalize_header(header):
        # Remove punctuation, lower case, and extra spaces
        return re.sub(r'[\W_]+', '', header).lower()

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
            # Do not validate headers yet, allow flexible formats

            file_storage.seek(0)
            reader = csv.reader(StringIO(content))
            headers = next(reader, [])
            headers_norm = [normalize_header(h) for h in headers]

            # Find relevant columns
            first_name_idx = None
            last_name_idx = None
            name_idx = None
            repo_url_idx = None

            for i, h in enumerate(headers):
                h_norm = normalize_header(h)
                if h_norm in ["firstname"]:
                    first_name_idx = i
                elif h_norm in ["lastname"]:
                    last_name_idx = i
                elif h_norm in ["name"]:
                    name_idx = i
                # Look for github repo url column (robust)
                if ("github" in h_norm and "repo" in h_norm and "url" in h_norm) or (
                    "github" in h_norm and "repository" in h_norm
                ):
                    repo_url_idx = i
                # Also allow "repo_url"
                if h_norm == "repourl":
                    repo_url_idx = i

            for row in reader:
                if not any(row):
                    continue
                student_data = {}
                # Name logic
                if first_name_idx is not None and last_name_idx is not None:
                    first = row[first_name_idx].strip() if first_name_idx < len(row) else ""
                    last = row[last_name_idx].strip() if last_name_idx < len(row) else ""
                    student_data['name'] = f"{first} {last}".strip()
                elif name_idx is not None:
                    student_data['name'] = row[name_idx].strip() if name_idx < len(row) else ""
                # Repo URL logic
                if repo_url_idx is not None:
                    student_data['repo_url'] = row[repo_url_idx].strip() if repo_url_idx < len(row) else ""
                # Fallback: try to find repo url in any column by header
                if 'repo_url' not in student_data or not student_data['repo_url']:
                    for i, h in enumerate(headers):
                        h_norm = normalize_header(h)
                        if ("github" in h_norm and "repo" in h_norm and "url" in h_norm) or (
                            "github" in h_norm and "repository" in h_norm
                        ):
                            student_data['repo_url'] = row[i].strip() if i < len(row) else ""
                            break
                # Final fallback: scan all columns for a value containing 'github.com'
                if 'repo_url' not in student_data or not student_data['repo_url']:
                    for value in row:
                        if isinstance(value, str) and "github.com" in value:
                            student_data['repo_url'] = value.strip()
                            break
                # Only add if both fields present and repo_url looks like a GitHub URL
                if (
                    'name' in student_data
                    and 'repo_url' in student_data
                    and student_data['repo_url']
                    and "github.com" in student_data['repo_url']
                ):
                    results.append(student_data)
            if not results:
                raise ValueError('No student data found in CSV with required columns (First Name + Last Name, or Name, and GitHub Repo URL)')
            return results

        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_storage)
            headers = df.columns.tolist()
            # Do not validate headers yet, allow flexible formats
            headers_norm = [normalize_header(h) for h in headers]

            # Find relevant columns
            first_name_col = None
            last_name_col = None
            name_col = None
            repo_url_col = None

            for h in headers:
                h_norm = normalize_header(h)
                if h_norm in ["firstname"]:
                    first_name_col = h
                elif h_norm in ["lastname"]:
                    last_name_col = h
                elif h_norm in ["name"]:
                    name_col = h
                if ("github" in h_norm and "repo" in h_norm and "url" in h_norm) or (
                    "github" in h_norm and "repository" in h_norm
                ):
                    repo_url_col = h
                if h_norm == "repourl":
                    repo_url_col = h

            for _, row in df.iterrows():
                student_data = {}
                # Name logic
                if first_name_col and last_name_col:
                    first = str(row[first_name_col]).strip() if not pd.isnull(row[first_name_col]) else ""
                    last = str(row[last_name_col]).strip() if not pd.isnull(row[last_name_col]) else ""
                    student_data['name'] = f"{first} {last}".strip()
                elif name_col:
                    value = row[name_col]
                    student_data['name'] = str(value).strip() if not pd.isnull(value) else ""
                # Repo URL logic
                if repo_url_col:
                    value = row[repo_url_col]
                    student_data['repo_url'] = str(value).strip() if not pd.isnull(value) else ""
                # Fallback: try to find repo url in any column by header
                if 'repo_url' not in student_data or not student_data['repo_url']:
                    for h in headers:
                        h_norm = normalize_header(h)
                        if ("github" in h_norm and "repo" in h_norm and "url" in h_norm) or (
                            "github" in h_norm and "repository" in h_norm
                        ):
                            value = row[h]
                            student_data['repo_url'] = str(value).strip() if not pd.isnull(value) else ""
                            break
                # Final fallback: scan all columns for a value containing 'github.com'
                if 'repo_url' not in student_data or not student_data['repo_url']:
                    for h in headers:
                        value = row[h]
                        if isinstance(value, str) and "github.com" in value:
                            student_data['repo_url'] = value.strip()
                            break
                # Only add if both fields present and repo_url looks like a GitHub URL
                if (
                    'name' in student_data
                    and 'repo_url' in student_data
                    and student_data['repo_url']
                    and "github.com" in student_data['repo_url']
                ):
                    results.append(student_data)
            if not results:
                raise ValueError('No student data found in Excel or CSV with required columns (First Name + Last Name, or Name, and GitHub Repo URL)')
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
    Dynamically creates columns based on actual criteria found in the data.
    """
    
    # Helper function to extract criterion name from context
    def extract_criterion_name(context):
        """Extract clean criterion name from context string"""
        if not context or not isinstance(context, str):
            return None
            
        context = context.strip()
        
        # Skip noise data (contains code snippets, colors, etc.)
        if any(noise in context.lower() for noise in ['hsl(', 'rgb(', '": "', '\':', 'module.exports', '{', '}', 'console.', 'function']):
            return None
            
        # Skip duplicates that start with "-"
        if context.startswith("-"):
            return None
            
        # Extract criterion name from different patterns
        if ":" in context:
            parts = context.split(":")
            if len(parts) >= 2:
                # Handle "Main Criterion: Correctness of Code: 12/12"
                if parts[0].strip().lower() in ["main criterion", "criterion"]:
                    if len(parts) >= 3:
                        # Extract the middle part as criterion name
                        criterion = parts[1].strip()
                    else:
                        return None
                else:
                    # Handle "Code Structure: 8/8"
                    criterion = parts[0].strip()
                
                # Clean up the criterion name
                criterion = re.sub(r'\s*\d+/\d+\s*$', '', criterion)  # Remove score like "8/8"
                criterion = criterion.strip()
                
                # Validate criterion name (should be meaningful text)
                if len(criterion) > 1 and not criterion.isdigit() and criterion.lower() not in ['main', 'criterion']:
                    return criterion
                    
        return None
    
    # First pass: collect all unique criteria across all students
    all_criteria = set()
    for student in scores:
        scores_obj = student.get("scores", {})
        extracted = scores_obj.get("extracted_scores", []) if isinstance(scores_obj, dict) else []
        
        for score in extracted:
            context = score.get("context", "")
            criterion = extract_criterion_name(context)
            if criterion:
                all_criteria.add(criterion)
    
    # Sort criteria for consistent ordering
    sorted_criteria = sorted(all_criteria)
    print(f"Found criteria: {sorted_criteria}")  # Debug
    
    # Helper to flatten a single student's scores
    def flatten_student_score(student):
        row = {
            "Name": student.get("name", ""),
            "Repository": student.get("repo_url", ""),
        }
        
        # Initialize all criteria columns
        for criterion in sorted_criteria:
            row[f"{criterion} Score"] = ""
            row[f"{criterion} %"] = ""
        
        # Process scores data
        scores_obj = student.get("scores", {})
        extracted = scores_obj.get("extracted_scores", []) if isinstance(scores_obj, dict) else []
        raw_assessment = scores_obj.get("raw_assessment", "") if isinstance(scores_obj, dict) else ""
        
        # Track processed criteria to avoid duplicates
        processed_criteria = set()
        
        if extracted:
            for score in extracted:
                context = score.get("context", "")
                criterion = extract_criterion_name(context)
                
                if criterion and criterion not in processed_criteria:
                    processed_criteria.add(criterion)
                    
                    # Add score information
                    if "score" in score and "max_score" in score:
                        row[f"{criterion} Score"] = f"{score['score']}/{score['max_score']}"
                    
                    if "percentage" in score:
                        percentage = score.get('percentage', 0)
                        row[f"{criterion} %"] = f"{round(percentage, 1)}%"
            
            # Add overall summary
            summary = scores_obj.get("summary", "")
            if not summary:
                # Use raw_assessment as fallback if summary is missing
                if raw_assessment:
                    summary = str(raw_assessment).strip()
            if summary:
                # Limit summary length for better display
                if len(summary) > 400:
                    summary = summary[:400] + "..."
                row["Summary"] = summary
        
        return row

    # Flatten all students
    flat_rows = [flatten_student_score(s) for s in scores]
    
    # Create DataFrame
    df = pd.DataFrame(flat_rows)
    
    # Organize columns in a logical order
    ordered_cols = ["Name", "Repository"]
    
    # Add criteria columns (Score and % for each criterion)
    for criterion in sorted_criteria:
        score_col = f"{criterion} Score"
        percent_col = f"{criterion} %"
        if score_col in df.columns:
            ordered_cols.append(score_col)
        if percent_col in df.columns:
            ordered_cols.append(percent_col)
    
    # Add summary at the end
    if "Summary" in df.columns:
        ordered_cols.append("Summary")
    
    # Filter to only include columns that exist in the DataFrame
    ordered_cols = [col for col in ordered_cols if col in df.columns]
    
    # Reorder DataFrame
    df = df[ordered_cols]
    
    # Create Excel file
    output = io.BytesIO()
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Student Assessment Results'
    
    # Add data to worksheet
    for r in dataframe_to_rows(df, index=False, header=True):
        worksheet.append(r)
    
    # Define color scheme
    colors = {
        'header': PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid'),
        'name': PatternFill(start_color='D6EAF8', end_color='D6EAF8', fill_type='solid'),
        'score': PatternFill(start_color='D5F4E6', end_color='D5F4E6', fill_type='solid'),
        'percent': PatternFill(start_color='E8F6F3', end_color='E8F6F3', fill_type='solid'),
        'summary': PatternFill(start_color='FEF9E7', end_color='FEF9E7', fill_type='solid'),
        'light_row': PatternFill(start_color='F8F9FA', end_color='F8F9FA', fill_type='solid'),
        'white_row': PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
    }
    
    # Define fonts
    fonts = {
        'header': Font(color='FFFFFF', bold=True, size=11),
        'name': Font(bold=True, color='1B4F72', size=10),
        'score': Font(bold=True, color='0E6B2C', size=10),
        'percent': Font(color='117A65', size=10),
        'summary': Font(color='B7950B', size=9),
        'regular': Font(size=9)
    }
    
    # Border style
    thin_border = Border(
        left=Side(style='thin', color='BDC3C7'),
        right=Side(style='thin', color='BDC3C7'),
        top=Side(style='thin', color='BDC3C7'),
        bottom=Side(style='thin', color='BDC3C7')
    )
    
    # Format header row
    for col_num, col_name in enumerate(df.columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.fill = colors['header']
        cell.font = fonts['header']
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    
    # Format data rows
    for row_num in range(2, worksheet.max_row + 1):
        # Determine base row color (alternating)
        base_fill = colors['light_row'] if (row_num - 2) % 2 == 0 else colors['white_row']
        
        for col_num, col_name in enumerate(df.columns, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.border = thin_border
            
            # Apply column-specific formatting
            if col_name == "Name":
                cell.fill = colors['name']
                cell.font = fonts['name']
                cell.alignment = Alignment(horizontal="left", vertical="center")
                
            elif col_name == "Repository":
                cell.fill = colors['name']
                cell.font = Font(size=9, color='1B4F72', underline='single')
                cell.alignment = Alignment(horizontal="left", vertical="center")
                
            elif "Score" in col_name:
                cell.fill = colors['score']
                cell.font = fonts['score']
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            elif "%" in col_name:
                cell.fill = colors['percent']
                cell.font = fonts['percent']
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            elif col_name == "Summary":
                cell.fill = colors['summary']
                cell.font = fonts['summary']
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                
            else:
                cell.fill = base_fill
                cell.font = fonts['regular']
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    
    # Set column widths
    for col_num, col_name in enumerate(df.columns, 1):
        if col_name == "Name":
            width = 18
        elif col_name == "Repository":
            width = 45
        elif "Score" in col_name:
            width = 12
        elif "%" in col_name:
            width = 10
        elif col_name == "Summary":
            width = 50
        else:
            width = 20
        
        column_letter = worksheet.cell(row=1, column=col_num).column_letter
        worksheet.column_dimensions[column_letter].width = width
    
    # Set row heights
    worksheet.row_dimensions[1].height = 30  # Header row
    for row_num in range(2, worksheet.max_row + 1):
        worksheet.row_dimensions[row_num].height = 35  # Data rows
    
    # Freeze panes (header and first two columns)
    worksheet.freeze_panes = 'C2'
    
    # Remove auto-filter (don't add it)
    # worksheet.auto_filter is intentionally not set
    
    # Save workbook
    workbook.save(output)
    output.seek(0)
    
    return output

def format_scores_for_display(scores):
    """
    Format scores data for display in the web interface
    """
    display_data = []
    
    for student in scores:
        row = {
            "Name": student.get("name", ""),
            "Repository": student.get("repo_url", "")
        }
        
        scores_obj = student.get("scores", {})
        extracted = scores_obj.get("extracted_scores", []) if isinstance(scores_obj, dict) else []
        
        if extracted:
            # Calculate overall performance
            valid_percentages = []
            for score in extracted:
                context = score.get("context", "")
                # Only include valid criteria scores, not noise
                if (":" in context and 
                    not any(noise in context.lower() for noise in ['hsl(', 'rgb(', '": "', 'module.exports']) and
                    not context.strip().startswith("-") and
                    "percentage" in score):
                    valid_percentages.append(score.get('percentage', 0))
            
            if valid_percentages:
                avg_percentage = sum(valid_percentages) / len(valid_percentages)
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
