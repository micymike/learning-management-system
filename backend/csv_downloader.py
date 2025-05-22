"""
Script to download rubrics and desired outputs from training_scripts.csv
"""
import os
import csv
import re
import requests
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

def extract_google_sheet_id(url):
    """Extract the Google Sheet ID from a URL"""
    pattern = r'/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def extract_gid(url):
    """Extract the GID (sheet tab) from a URL"""
    pattern = r'gid=(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return '0'  # Default to first sheet if not specified

def download_google_sheet(url, output_dir):
    """Download a Google Sheet as CSV"""
    sheet_id = extract_google_sheet_id(url)
    gid = extract_gid(url)
    
    if not sheet_id:
        print(f"Invalid Google Sheets URL: {url}")
        return None
    
    # Construct the export URL
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        response = requests.get(export_url)
        response.raise_for_status()
        
        # Determine file type and name
        if 'rubric' in url.lower():
            file_type = 'rubric'
        else:
            file_type = 'output'
        
        # Create a unique filename
        filename = f"{file_type}_{sheet_id}_{gid}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Save the file
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded {file_type} to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def process_training_csv(csv_path, output_dir='downloads'):
    """Process the training_scripts.csv file and download all sheets"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_files = []
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                label = row[0].strip()
                url = row[1].strip()
                
                if url.startswith('http'):
                    filepath = download_google_sheet(url, output_dir)
                    if filepath:
                        downloaded_files.append({
                            'label': label,
                            'url': url,
                            'filepath': filepath,
                            'type': 'rubric' if 'rubric' in label.lower() else 'output'
                        })
    
    return downloaded_files