#!/usr/bin/env python3
import sys
import os
import json
from rubric_handler import upload_rubric_file

def debug_rubric_file(file_path):
    """Debug a rubric file by reading it and trying to parse it"""
    print(f"Debugging rubric file: {file_path}")
    
    try:
        # Read the file
        with open(file_path, 'rb') as f:
            content = f.read()
            
        print(f"File size: {len(content)} bytes")
        print(f"File type: {os.path.splitext(file_path)[1]}")
        print(f"First 100 bytes: {content[:100]}")
        
        # Try to decode as text
        try:
            text_content = content.decode('utf-8')
            print(f"Text content (first 500 chars): {text_content[:500]}")
        except UnicodeDecodeError:
            print("File is not UTF-8 text")
        
        # Try to parse with rubric handler
        rubric_items = upload_rubric_file(content)
        print(f"Parsed rubric items: {json.dumps(rubric_items, indent=2)}")
        
        return True
    except Exception as e:
        print(f"Error processing rubric: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_rubric.py <rubric_file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    success = debug_rubric_file(file_path)
    sys.exit(0 if success else 1)