#!/usr/bin/env python3
"""
Test script to verify the upload_csv endpoint using requests
"""
import requests
import os
import sys

def test_upload_csv():
    """Test the upload_csv endpoint with sample files"""
    url = "http://localhost:8000/upload_csv"
    
    # Check if files exist
    csv_path = "test_students.csv"
    rubric_path = "sample_rubric.xlsx"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return
    
    if not os.path.exists(rubric_path):
        print(f"Error: {rubric_path} not found")
        return
    
    # Prepare the files and form data
    files = {
        'file': (os.path.basename(csv_path), open(csv_path, 'rb'), 'text/csv'),
        'rubric': (os.path.basename(rubric_path), open(rubric_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    
    data = {
        'name': 'Test Upload from Python'
    }
    
    print(f"Sending request to {url}")
    print(f"Files: {files.keys()}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, files=files, data=data)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            print(f"Response JSON: {response.json()}")
        except:
            print(f"Response text: {response.text[:500]}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        # Close file handles
        for file_obj in files.values():
            file_obj[1].close()

if __name__ == "__main__":
    test_upload_csv()