import pandas as pd
from io import BytesIO
import re
import json
from openpyxl import load_workbook

def upload_rubric_file(content):
    """
    Process uploaded rubric file content - extracts EXACT content without modifications.
    Supports Excel files (.xlsx, .xls) and text files (.txt, .md)
    
    Returns the raw rubric content as a structured format for AI assessment
    Throws error if parsing fails - NO DEFAULT FALLBACKS
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
            bytes_io = BytesIO(content)
            
            # Try different pandas engines to read Excel
            engines = ['openpyxl', 'xlrd']
            df = None
            
            for engine in engines:
                try:
                    bytes_io.seek(0)
                    print(f"Trying with {engine} engine...")
                    df = pd.read_excel(bytes_io, engine=engine)
                    print(f"Excel content successfully parsed with {engine} engine:")
                    print(f"DataFrame shape: {df.shape}")
                    print(f"DataFrame columns: {df.columns.tolist()}")
                    print("Raw DataFrame content:")
                    print(df.to_string())
                    break
                except Exception as engine_error:
                    print(f"{engine} engine failed: {str(engine_error)}")
                    continue
            
            if df is None:
                raise ValueError("Failed to parse Excel file with any available engine")
            
            # Extract raw Excel content without interpretation
            return extract_raw_excel_content(df)
            
        except Exception as excel_error:
            print(f"Excel parsing failed: {str(excel_error)}")
            
            # Try as text file
            try:
                print("Attempting to parse as text file...")
                
                # Try different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                text_content = None
                
                for encoding in encodings:
                    try:
                        text_content = content.decode(encoding)
                        print(f"Successfully decoded with {encoding} encoding")
                        break
                    except UnicodeDecodeError as decode_error:
                        print(f"Failed with {encoding} encoding: {str(decode_error)}")
                        continue
                
                if text_content is None:
                    raise ValueError("Could not decode text file with any encoding")
                
                print(f"Raw text content preview: {text_content[:500]}...")
                
                # Extract raw text content without interpretation
                return extract_raw_text_content(text_content)
                
            except Exception as text_error:
                print(f"Text parsing failed: {str(text_error)}")
                raise ValueError(f"Could not process file as Excel or text: Excel error: {excel_error}, Text error: {text_error}")
                
    except Exception as e:
        print(f"Rubric processing failed with error: {str(e)}")
        raise ValueError(f"Failed to process rubric file: {str(e)}")

def extract_raw_excel_content(df):
    """
    Extract raw Excel content exactly as-is without any interpretation or modification
    """
    print("\nExtracting raw Excel content...")
    
    if df.empty:
        raise ValueError("Excel file is empty - no content to extract")
    
    # Convert the entire DataFrame to a structured format preserving all content
    raw_content = {
        'type': 'excel',
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'raw_data': []
    }
    
    # Extract every cell exactly as it appears
    for index, row in df.iterrows():
        row_data = {}
        for col in df.columns:
            cell_value = row[col]
            # Preserve exact cell content including NaN, numbers, strings
            if pd.isna(cell_value):
                row_data[col] = None
            else:
                row_data[col] = cell_value
        raw_content['raw_data'].append(row_data)
    
    # Also provide a raw text representation
    raw_content['raw_text'] = df.to_string(na_rep='', index=False)
    
    print("Raw Excel content extracted:")
    print(json.dumps(raw_content, indent=2, default=str))
    
    return raw_content

def extract_raw_text_content(text_content):
    """
    Extract raw text content exactly as-is without any interpretation or modification
    """
    print("\nExtracting raw text content...")
    
    if not text_content.strip():
        raise ValueError("Text file is empty - no content to extract")
    
    # Split into lines while preserving exact content
    lines = text_content.split('\n')
    
    raw_content = {
        'type': 'text',
        'total_lines': len(lines),
        'raw_lines': lines,
        'raw_text': text_content
    }
    
    print(f"Raw text content extracted: {len(lines)} lines")
    print("First 10 lines:")
    for i, line in enumerate(lines[:10]):
        print(f"Line {i+1}: {repr(line)}")
    
    return raw_content

def format_rubric_for_ai_assessment(raw_rubric_content):
    """
    Format the raw rubric content for AI assessment without any modifications
    Simply presents the content in a clean format for the AI to understand
    """
    print("\nFormatting rubric for AI assessment...")
    
    if raw_rubric_content['type'] == 'excel':
        # Present Excel content as-is
        formatted_content = f"""RUBRIC CONTENT (Excel Format):

Columns: {', '.join(raw_rubric_content['columns'])}
Total Rows: {raw_rubric_content['shape'][0]}
Total Columns: {raw_rubric_content['shape'][1]}

RAW DATA:
{raw_rubric_content['raw_text']}

STRUCTURED DATA:
"""
        for i, row_data in enumerate(raw_rubric_content['raw_data']):
            formatted_content += f"\nRow {i+1}:\n"
            for col, value in row_data.items():
                formatted_content += f"  {col}: {value}\n"
        
    elif raw_rubric_content['type'] == 'text':
        # Present text content as-is
        formatted_content = f"""RUBRIC CONTENT (Text Format):

Total Lines: {raw_rubric_content['total_lines']}

RAW CONTENT:
{raw_rubric_content['raw_text']}
"""
    else:
        raise ValueError(f"Unknown rubric content type: {raw_rubric_content['type']}")
    
    print("Formatted rubric content:")
    print(formatted_content[:1000] + "..." if len(formatted_content) > 1000 else formatted_content)
    
    return formatted_content

# Remove the old parsing functions that made assumptions about rubric structure
# No more parse_rubric_lines, parse_tabular_rubric with default fallbacks

# Global variable to store raw rubric (exact content)
raw_custom_rubric = None

def set_custom_rubric(raw_content):
    """Store the raw rubric content globally"""
    global raw_custom_rubric
    raw_custom_rubric = raw_content
    print("Custom rubric set successfully")

def get_custom_rubric():
    """Get the stored raw rubric content"""
    global raw_custom_rubric
    if raw_custom_rubric is None:
        raise ValueError("No custom rubric has been loaded. Please upload a rubric file first.")
    return raw_custom_rubric

def calculate_percentage(points, max_points):
    """Calculate percentage score from points"""
    if max_points <= 0:
        raise ValueError("Maximum points must be greater than 0")
    percentage = (points / max_points) * 100
    return round(percentage, 2)

def is_passing_grade(percentage, passing_threshold=80.0):
    """Check if percentage meets the passing threshold"""
    return percentage >= passing_threshold