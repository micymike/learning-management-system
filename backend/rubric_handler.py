import pandas as pd
from io import BytesIO
import re
import json
from openpyxl import load_workbook

def upload_rubric_file(content):
    """
    Process uploaded rubric file content.
    Supports Excel files (.xlsx, .xls) and text files (.txt, .md)
    
    Returns a list of dictionaries with criteria and max_points
    """
    print("\nProcessing rubric file...")
    print(f"Content type: {type(content)}")
    print(f"Content length: {len(content)} bytes")
    
    # For debugging, print first 100 bytes as hex
    print(f"Content preview (hex): {content[:100].hex()[:100]}...")
    
    try:
        # Try to read as Excel first
        try:
            print("Attempting to parse as Excel...")
            # Create BytesIO object from binary content
            bytes_io = BytesIO(content)
            
            # Try to detect Excel format
            try:
                # Try to load with openpyxl first (for debugging)
                print("Trying to load with openpyxl...")
                workbook = load_workbook(bytes_io)
                print(f"Excel file loaded with openpyxl. Sheets: {workbook.sheetnames}")
                
                # Reset the BytesIO object
                bytes_io.seek(0)
            except Exception as openpyxl_error:
                print(f"openpyxl loading failed: {str(openpyxl_error)}")
                # Reset the BytesIO object
                bytes_io.seek(0)
            
            # Now try with pandas
            try:
                print("Trying to load with pandas...")
                df = pd.read_excel(bytes_io)
                print("\nExcel content successfully parsed with pandas:")
                print(f"DataFrame shape: {df.shape}")
                print(f"DataFrame columns: {df.columns.tolist()}")
                print(df.head())
                
                # Check if this is a tabular rubric format with scoring levels in columns
                if df.shape[1] >= 2:
                    # Try to detect if first row contains scoring levels
                    first_row = df.iloc[0]
                    has_scoring_levels = False
                    
                    # Check if first row contains text like "marks", "points", or scoring patterns
                    for col in range(1, len(first_row)):
                        cell_value = str(first_row.iloc[col]).lower() if pd.notna(first_row.iloc[col]) else ""
                        if any(term in cell_value.lower() for term in ["mark", "point", "score", "correct", "partial"]):
                            has_scoring_levels = True
                            break
                    
                    if has_scoring_levels:
                        print("Detected tabular rubric with scoring levels in columns")
                        return parse_tabular_rubric(df)
                
            except Exception as pandas_error:
                print(f"pandas Excel reading failed: {str(pandas_error)}")
                # Try with different Excel engine
                bytes_io.seek(0)
                try:
                    print("Trying with xlrd engine...")
                    df = pd.read_excel(bytes_io, engine='xlrd')
                    print("Excel content successfully parsed with xlrd engine")
                    
                    # Check if this is a tabular rubric format with scoring levels in columns
                    if df.shape[1] >= 2:
                        # Try to detect if first row contains scoring levels
                        first_row = df.iloc[0]
                        has_scoring_levels = False
                        
                        # Check if first row contains text like "marks", "points", or scoring patterns
                        for col in range(1, len(first_row)):
                            cell_value = str(first_row.iloc[col]).lower() if pd.notna(first_row.iloc[col]) else ""
                            if any(term in cell_value.lower() for term in ["mark", "point", "score", "correct", "partial"]):
                                has_scoring_levels = True
                                break
                        
                        if has_scoring_levels:
                            print("Detected tabular rubric with scoring levels in columns")
                            return parse_tabular_rubric(df)
                    
                except Exception as xlrd_error:
                    print(f"xlrd engine failed: {str(xlrd_error)}")
                    # Try with openpyxl engine explicitly
                    bytes_io.seek(0)
                    try:
                        print("Trying with openpyxl engine...")
                        df = pd.read_excel(bytes_io, engine='openpyxl')
                        print("Excel content successfully parsed with openpyxl engine")
                        
                        # Check if this is a tabular rubric format with scoring levels in columns
                        if df.shape[1] >= 2:
                            # Try to detect if first row contains scoring levels
                            first_row = df.iloc[0]
                            has_scoring_levels = False
                            
                            # Check if first row contains text like "marks", "points", or scoring patterns
                            for col in range(1, len(first_row)):
                                cell_value = str(first_row.iloc[col]).lower() if pd.notna(first_row.iloc[col]) else ""
                                if any(term in cell_value.lower() for term in ["mark", "point", "score", "correct", "partial"]):
                                    has_scoring_levels = True
                                    break
                            
                            if has_scoring_levels:
                                print("Detected tabular rubric with scoring levels in columns")
                                return parse_tabular_rubric(df)
                        
                    except Exception as openpyxl_engine_error:
                        print(f"openpyxl engine failed: {str(openpyxl_engine_error)}")
                        raise
            
            # Convert Excel to text format
            lines = []
            current_criterion = None
            
            for _, row in df.iterrows():
                # Convert row to string, handling NaN values
                text = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                points = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else None
                
                if not text:
                    continue
                    
                # If it's a main criterion (contains points in second column)
                if points is not None and isinstance(points, (int, float)):
                    lines.append(f"{text} [{int(points)} points]")
                    current_criterion = text
                # If it's a level description (starts with - or *)
                elif text.startswith(('-', '*')) and current_criterion:
                    lines.append(text)
            
            print("\nConverted Excel to lines:")
            print("\n".join(lines))
            
            return parse_rubric_lines(lines)
            
        except Exception as excel_error:
            print(f"Excel parsing failed: {str(excel_error)}")
            
            # Try as text file
            try:
                print("Attempting to parse as text file...")
                text_content = content.decode('utf-8')
                print(f"Text content preview: {text_content[:200]}...")
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                print(f"Parsed {len(lines)} lines from text content")
                return parse_rubric_lines(lines)
            except UnicodeDecodeError as decode_error:
                print(f"Text parsing failed: {str(decode_error)}")
                
                # Try with different encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        print(f"Trying with {encoding} encoding...")
                        text_content = content.decode(encoding)
                        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                        print(f"Successfully parsed with {encoding} encoding")
                        return parse_rubric_lines(lines)
                    except Exception as e:
                        print(f"Failed with {encoding} encoding: {str(e)}")
                
                # If we get here, all parsing attempts failed
                raise ValueError("Could not process file as Excel or text with any encoding")
                
    except Exception as e:
        print(f"Rubric processing failed with error: {str(e)}")
        raise ValueError(f"Could not process rubric file: {str(e)}")

def parse_rubric_lines(lines):
    """
    Parse rubric lines with format:
    Criterion Name [X points]
    - Level 1 (0-2): Description
    - Level 2 (3-5): Description
    etc.
    
    Also supports Excel-style format where the criterion is in the first column
    and the points are in the second column.
    
    If no valid criteria are found, returns a default rubric.
    """
    try:
        print("\nParsing rubric lines:")
        print("\n".join(lines[:20]))  # Print first 20 lines to avoid overwhelming logs
        if len(lines) > 20:
            print(f"... and {len(lines) - 20} more lines")
        
        criteria = []
        current_criterion = None
        
        # First pass: try to identify if this is an Excel-style export
        is_excel_format = False
        has_points_column = False
        
        # Check if any line contains a tab or multiple spaces that might indicate columns
        for line in lines[:10]:  # Check first 10 lines
            if '\t' in line or '    ' in line:
                is_excel_format = True
                print("Detected possible Excel-style format (tab or multiple spaces)")
                break
        
        # If it looks like Excel format, try to parse it differently
        if is_excel_format:
            print("Parsing as Excel-style format")
            for line in lines:
                if not line.strip():
                    continue
                
                # Split by tab or multiple spaces
                parts = re.split(r'\t|    +', line)
                if len(parts) >= 2:
                    criterion_name = parts[0].strip()
                    # Try to extract points from second column
                    points_match = re.search(r'(\d+)', parts[1])
                    
                    if points_match and criterion_name:
                        if current_criterion:
                            criteria.append(current_criterion)
                            print(f"Added criterion: {json.dumps(current_criterion, indent=2)}")
                        
                        max_points = float(points_match.group(1))
                        print(f"\nFound criterion: {criterion_name}")
                        print(f"Max points: {max_points}")
                        
                        current_criterion = {
                            'criterion': criterion_name,
                            'max_points': max_points,
                            'levels': []
                        }
                        has_points_column = True
            
            # If we found criteria with points column, return them
            if has_points_column and criteria:
                if current_criterion:
                    criteria.append(current_criterion)
                    print(f"Added final criterion: {json.dumps(current_criterion, indent=2)}")
                return criteria
        
        # If Excel format didn't work or wasn't detected, try standard format
        print("Parsing as standard format")
        criteria = []
        current_criterion = None
        
        for line in lines:
            if not line.strip():
                continue
                
            # Check if this is a criterion header (contains [X points])
            points_match = re.search(r'\[(\d+)\s*points?\]', line, re.IGNORECASE)
            if points_match:
                if current_criterion:
                    criteria.append(current_criterion)
                    print(f"Added criterion: {json.dumps(current_criterion, indent=2)}")
                
                max_points = float(points_match.group(1))
                criterion_name = line.split('[')[0].strip()
                
                print(f"\nFound criterion: {criterion_name}")
                print(f"Max points: {max_points}")
                
                current_criterion = {
                    'criterion': criterion_name,
                    'max_points': max_points,
                    'levels': []
                }
            
            # If no criteria found yet, try to extract from the line itself
            elif not criteria and not current_criterion:
                # Try to find a number that might be points
                points_match = re.search(r'(\d+)\s*points?', line, re.IGNORECASE)
                if points_match:
                    max_points = float(points_match.group(1))
                    # Use the rest of the line as criterion name
                    criterion_name = re.sub(r'\d+\s*points?', '', line, flags=re.IGNORECASE).strip()
                    
                    if criterion_name:
                        print(f"\nFound criterion from line: {criterion_name}")
                        print(f"Max points: {max_points}")
                        
                        current_criterion = {
                            'criterion': criterion_name,
                            'max_points': max_points,
                            'levels': []
                        }
            
            # Check if this is a level description
            elif line.startswith('-') and current_criterion:
                range_match = re.search(r'\((\d+)-(\d+)\)', line)
                if range_match:
                    min_points = float(range_match.group(1))
                    max_points = float(range_match.group(2))
                    desc_parts = line.split(':')
                    description = desc_parts[1].strip() if len(desc_parts) > 1 else ""
                    
                    level_info = {
                        'min_points': min_points,
                        'max_points': max_points,
                        'description': description
                    }
                    
                    print(f"Added level: {json.dumps(level_info, indent=2)}")
                    current_criterion['levels'].append(level_info)
        
        if current_criterion:
            criteria.append(current_criterion)
            print(f"Added final criterion: {json.dumps(current_criterion, indent=2)}")
        
        print("\nFinal parsed rubric:")
        print(json.dumps(criteria, indent=2))
        
        # If no criteria were found, use the default rubric
        if not criteria:
            print("No criteria found in rubric, using default rubric")
            return []
            
        return criteria
        
    except Exception as e:
        print(f"Error parsing rubric: {str(e)}")
        # Return default rubric on error
        print("Error parsing rubric, using default criteria")
        return []

# Global variable to store custom rubric
custom_rubric = None

def parse_tabular_rubric(df):
    """
    Parse a tabular rubric where:
    - First row contains scoring levels (e.g., "0 (No Mark)", "1-3 Marks", etc.)
    - First column contains criteria names
    - Cells contain descriptions for each criterion at each level
    
    Returns a list of dictionaries with criteria and max_points
    """
    global custom_rubric
    try:
        print("\nParsing tabular rubric format...")
        
        # Get scoring levels from first row
        scoring_levels = []
        max_points_per_criterion = {}
        
        # Skip first cell (usually empty or contains "Criteria")
        for col in range(1, df.shape[1]):
            cell_value = str(df.iloc[0, col]) if pd.notna(df.iloc[0, col]) else ""
            if cell_value:
                # Extract point values using regex
                points_match = re.search(r'(\d+)(?:\s*-\s*(\d+))?\s*(?:Marks|Mark|Points|Point)', cell_value, re.IGNORECASE)
                if points_match:
                    # If range like "1-3 Marks", use the higher value
                    if points_match.group(2):
                        points = float(points_match.group(2))
                    else:
                        points = float(points_match.group(1))
                    
                    scoring_levels.append({
                        'text': cell_value,
                        'points': points
                    })
                    print(f"Found scoring level: {cell_value} -> {points} points")
                else:
                    # If no explicit points, try to find any number
                    number_match = re.search(r'(\d+)', cell_value)
                    if number_match:
                        points = float(number_match.group(1))
                        scoring_levels.append({
                            'text': cell_value,
                            'points': points
                        })
                        print(f"Found scoring level with number: {cell_value} -> {points} points")
                    else:
                        # If no numbers, use position as points (1-based)
                        points = col
                        scoring_levels.append({
                            'text': cell_value,
                            'points': points
                        })
                        print(f"No points found, using position: {cell_value} -> {points} points")
        
        # If no scoring levels found, return default rubric
        if not scoring_levels:
            print("No scoring levels found in tabular rubric")
            return load_rubric()
        
        # Get maximum points for each criterion (highest value in scoring levels)
        max_points = max(level['points'] for level in scoring_levels)
        print(f"Maximum points per criterion: {max_points}")
        
        # Parse criteria from first column (starting from second row)
        criteria = []
        for row in range(1, df.shape[0]):
            criterion_name = str(df.iloc[row, 0]) if pd.notna(df.iloc[row, 0]) else ""
            if not criterion_name:
                continue
                
            # Clean up criterion name (remove any trailing colons)
            criterion_name = criterion_name.strip().rstrip(':')
            
            # If criterion name starts with "Main Criterion:" or similar, keep the full name
            # This is important for matching the exact criterion name in the assessment
            
            print(f"\nFound criterion: {criterion_name}")
            
            # Create criterion object
            criterion = {
                'criterion': criterion_name,
                'max_points': max_points,
                'levels': []
            }
            
            # Add descriptions for each scoring level
            for col, level in enumerate(scoring_levels, start=1):
                if col < df.shape[1]:
                    description = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                    if description:
                        level_info = {
                            'points': level['points'],
                            'description': description
                        }
                        criterion['levels'].append(level_info)
                        print(f"  Level {level['text']}: {description[:50]}...")
            
            criteria.append(criterion)
        
        # If no criteria found, return default rubric
        if not criteria:
            print("No criteria found in tabular rubric")
            return load_rubric()
            
        print(f"\nParsed {len(criteria)} criteria from tabular rubric")
        # Store the custom rubric in the global variable
        global custom_rubric
        custom_rubric = criteria
        return criteria
        
    except Exception as e:
        print(f"Error parsing tabular rubric: {str(e)}")
        return []

def load_rubric(file_path):
    """Load rubric from either Excel or text file"""
    if file_path.endswith('.xlsx'):
        # Read Excel file
        df = pd.read_excel(file_path)
        rubric = []
        for _, row in df.iterrows():
            criterion = {
                'criterion': row['Criterion'],
                'max_points': float(row['Max Points']),
                'levels': []
            }
            # Assuming levels are in columns named Level1, Level2, etc.
            level_cols = [col for col in df.columns if col.startswith('Level')]
            for i, level_col in enumerate(level_cols, 1):
                if pd.notna(row[level_col]):
                    criterion['levels'].append({
                        'level': i,
                        'description': row[level_col],
                        'min_points': float(row[f'Level{i}_Min']),
                        'max_points': float(row[f'Level{i}_Max'])
                    })
            rubric.append(criterion)
        return rubric
    else:
        # Existing text file handling
        with open(file_path, 'r') as f:
            return json.load(f)

def calculate_percentage(points, max_points):
    """Calculate percentage score from points"""
    if max_points <= 0:
        return 0
    percentage = (points / max_points) * 100
    return round(percentage, 2)

def is_passing_grade(percentage):
    """Check if percentage is passing grade (≥80%)"""
    return percentage >= 80.0
