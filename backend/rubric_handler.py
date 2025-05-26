import pandas as pd
from io import BytesIO
import re
import json

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

def parse_rubric_lines(lines):
    """
    Parse rubric lines with format:
    Criterion Name [X points]
    - Level 1 (0-2): Description
    - Level 2 (3-5): Description
    etc.
    """
    try:
        print("\nParsing rubric lines:")
        print("\n".join(lines))
        
        criteria = []
        current_criterion = None
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Check if this is a criterion header (contains [X points])
            points_match = re.search(r'\[(\d+)\s*points?\]', line, re.IGNORECASE)
            if points_match:
                # If we were processing a previous criterion, add it
                if current_criterion:
                    criteria.append(current_criterion)
                    print(f"Added criterion: {json.dumps(current_criterion, indent=2)}")
                
                # Start new criterion
                max_points = float(points_match.group(1))
                criterion_name = line.split('[')[0].strip()
                
                print(f"\nFound criterion: {criterion_name}")
                print(f"Max points: {max_points}")
                
                current_criterion = {
                    'criterion': criterion_name,
                    'max_points': max_points,
                    'levels': []
                }
            
            # Check if this is a level description
            elif line.startswith('-') and current_criterion:
                # Extract level ranges like (0-2) or (9-10)
                range_match = re.search(r'\((\d+)-(\d+)\)', line)
                if range_match:
                    min_points = float(range_match.group(1))
                    max_points = float(range_match.group(2))
                    
                    # Get description (everything after the :)
                    desc_parts = line.split(':')
                    description = desc_parts[1].strip() if len(desc_parts) > 1 else ""
                    
                    level_info = {
                        'min_points': min_points,
                        'max_points': max_points,
                        'description': description
                    }
                    
                    print(f"Added level: {json.dumps(level_info, indent=2)}")
                    current_criterion['levels'].append(level_info)
        
        # Add the last criterion if exists
        if current_criterion:
            criteria.append(current_criterion)
            print(f"Added final criterion: {json.dumps(current_criterion, indent=2)}")
        
        # Sort levels by min_points for each criterion
        for criterion in criteria:
            if 'levels' in criterion:
                criterion['levels'].sort(key=lambda x: x['min_points'])
        
        print("\nFinal parsed rubric:")
        print(json.dumps(criteria, indent=2))
        return criteria
        
    except Exception as e:
        print(f"Error parsing rubric: {str(e)}")
        # Return a simple format as fallback
        return [{"criterion": line.strip(), "max_points": 10.0} for line in lines if line.strip()]

def load_rubric():
    """
    Load default rubric criteria with points
    """
    return [
        {"criterion": "Code Correctness", "max_points": 10},
        {"criterion": "Code Readability", "max_points": 10},
        {"criterion": "Code Efficiency", "max_points": 10},
        {"criterion": "Error Handling", "max_points": 10}
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
