#this file is used to analyze repositories go through code by code in the github repo

import requests
import json
import os
import tempfile
import zipfile
import glob

def analyze_github_repo(url):
    """
    Downloads the GitHub repo as a zip, extracts it, and returns the concatenated code from all .py files.
    Tries both 'main' and 'master' branches for robustness.
    """
    try:
        if url.endswith('/'):
            url = url[:-1]
        if url.endswith('.git'):
            url = url[:-4]
        user_repo = '/'.join(url.split('/')[-2:])
        for branch in ['main', 'master']:
            zip_url = f"https://github.com/{user_repo}/archive/refs/heads/{branch}.zip"
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, 'repo.zip')
                r = requests.get(zip_url)
                if r.status_code != 200:
                    continue  # Try next branch
                with open(zip_path, 'wb') as f:
                    f.write(r.content)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                code = ""
                for ext in ['py', 'js', 'java', 'cpp', 'c', 'ts', 'rb', 'go', 'php']:
                    for file in glob.glob(os.path.join(tmpdir, '**', f'*.{ext}'), recursive=True):
                        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                            code += f.read() + '\n\n'
                if not code:
                    return "No code files found in repo."
                return code[:10000]  # Limit to 10,000 chars for safety
        return f"Failed to download repo zip for both 'main' and 'master' branches: https://github.com/{user_repo}/archive/refs/heads/main.zip"
    except Exception as e:
        return f"Error analyzing repo: {e}"

def analyze_repo(url):
    # For compatibility with AI_assessor.py
    return analyze_github_repo(url)
