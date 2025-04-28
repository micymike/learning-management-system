import pandas as pd
from io import BytesIO

def upload_rubric_file(content):
    """
    Process uploaded rubric file content.
    Supports both Excel files and text files (.txt, .md)
    """
    try:
        # Try to read as text file first
        try:
            text_content = content.decode('utf-8')
            # Split by newlines and filter out empty lines
            return [line.strip() for line in text_content.split('\n') if line.strip()]
        except UnicodeDecodeError:
            # If not text, try as Excel
            try:
                df = pd.read_excel(BytesIO(content))
                # Get first column, skip empty cells, convert to list
                return [str(x) for x in df.iloc[:, 0].dropna().tolist()]
            except Exception as e:
                raise ValueError("Could not process file as Excel: " + str(e))
    except Exception as e:
        raise ValueError("Could not process rubric file: " + str(e))

def load_rubric():
    """
    Load default rubric criteria
    """
    return [
        "Code quality and organization",
        "Documentation and comments",
        "Proper use of version control",
        "Implementation of required features",
        "Testing and error handling"
    ]
