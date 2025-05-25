import pandas as pd
from io import BytesIO

def upload_rubric_file(content):
    """
    Process uploaded rubric file content.
    Supports both Excel files and text files (.txt, .md)
    
    Returns a list of dictionaries with criteria and max_points
    """
    try:
        # Try to read as text file first
        try:
            text_content = content.decode('utf-8')
            # Split by newlines and filter out empty lines
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            # Parse the rubric lines to extract criteria and max points
            return parse_rubric_lines(lines)
            
        except UnicodeDecodeError:
            # If not text, try as Excel
            try:
                df = pd.read_excel(BytesIO(content))
                # Check if we have at least two columns (criteria and points)
                if len(df.columns) >= 2:
                    criteria = []
                    for _, row in df.iterrows():
                        if pd.notna(row[0]) and pd.notna(row[1]):
                            criteria.append({
                                'criterion': str(row[0]),
                                'max_points': float(row[1])
                            })
                    return criteria
                else:
                    # Only one column, assume default points
                    return [{'criterion': str(x), 'max_points': 10.0} for x in df.iloc[:, 0].dropna().tolist()]
            except Exception as e:
                raise ValueError("Could not process file as Excel: " + str(e))
    except Exception as e:
        raise ValueError("Could not process rubric file: " + str(e))

import re

def parse_rubric_lines(lines, default_points=10.0):
    """Parses rubric lines from various formats."""
    criteria = []
    if len(lines) < 2:
        return criteria

    try:
        # First line: Score descriptions
        score_descriptions = [s.strip() for s in lines[0].split('\t')]

        # Second line: Main criterion and descriptions
        parts = lines[1].split('\t')
        main_criterion = parts[0].split(':')[1].strip()
        descriptions = [d.strip() for d in parts[1:]]

        # Create a single criterion with descriptions
        criterion = {
            'criterion': main_criterion,
            'max_points': default_points,
            'score_mapping': dict(zip(score_descriptions, range(0, 11, 10 // (len(score_descriptions) -1 )))) if len(score_descriptions) > 1 else {score_descriptions[0]: default_points},
            'descriptions': dict(zip(score_descriptions, descriptions))
        }
        criteria.append(criterion)
    except Exception as e:
        print(f"Error parsing rubric: {e}")
        return []

    return criteria


def load_rubric():
    """
    Load default rubric criteria with points
    """
    return [
        {"criterion": "Code quality and organization", "max_points": 10},
        {"criterion": "Documentation and comments", "max_points": 10},
        {"criterion": "Proper use of version control", "max_points": 10},
        {"criterion": "Implementation of required features", "max_points": 15},
        {"criterion": "Testing and error handling", "max_points": 5}
    ]

def calculate_percentage(points, max_points):
    """
    Calculate percentage score from points
    """
    if max_points <= 0:
        return 0
    
    percentage = (points / max_points) * 100
    return round(percentage, 2)

def is_passing_grade(percentage):
    """
    Check if the percentage is a passing grade (80% or higher)
    """
    return percentage >= 80.0
