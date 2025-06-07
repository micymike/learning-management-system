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
        user, repo = user_repo.split("/")
        # Get default branch from GitHub API
        default_branch = None
        try:
            repo_api_url = f"https://api.github.com/repos/{user}/{repo}"
            repo_info = requests.get(repo_api_url)
            if repo_info.status_code == 404:
                return f"Repository not found: {url}. Please check the URL."
            if repo_info.status_code == 403:
                return f"Repository is private or access is denied: {url}."
            if repo_info.status_code == 200:
                default_branch = repo_info.json().get("default_branch")
            elif repo_info.status_code != 200:
                return f"Failed to access repository metadata (status {repo_info.status_code}) for {url}."
        except Exception as e:
            return f"Error accessing repository metadata for {url}: {e}"
        branches_to_try = []
        if default_branch:
            branches_to_try.append(default_branch)
        # Always try main and master as fallback
        for fallback_branch in ['main', 'master']:
            if fallback_branch not in branches_to_try:
                branches_to_try.append(fallback_branch)
        # Try zip download for each branch
        for branch in branches_to_try:
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
                # --- NEW: CONCATENATE ALL FILES IN THE REPO (EXCEPT BINARIES & VERY LARGE FILES) ---
                code = ""
                # Only include likely source code and config files, exclude CSS/HTML/large non-source files
                allowed_exts = (
                    '.py', '.js', '.jsx', '.java', '.cpp', '.c', '.ts', '.rb', '.go', '.php', '.ipynb', '.sh', '.R', '.pl', '.swift', '.cs', '.scala', '.kt', '.dart', '.m', '.rs', '.erl', '.ex', '.exs', '.jl', '.lua', '.hs', '.clj', '.groovy', '.ps1', '.bat', '.vb', '.fs', '.fsx', '.sql', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env', '.md', '.txt', '.csv'
                )
                exclude_exts = ('.css', '.html', '.htm')
                code = ""
                for root, dirs, files in os.walk(tmpdir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Skip files >1MB
                        if os.path.getsize(file_path) > 1_000_000:
                            continue
                        # Skip common binary file types and excluded extensions
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.exe', '.dll', '.so', '.zip', '.tar', '.gz', '.pdf', '.mp4', '.mp3', '.ogg', '.mov', '.avi', '.wmv', '.flv', '.mkv') + exclude_exts):
                            continue
                        # Only include allowed extensions
                        if not file.lower().endswith(allowed_exts):
                            continue
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                code += f"\n\n# === FILE: {os.path.relpath(file_path, tmpdir)} ===\n"
                                code += f.read()
                        except Exception:
                            continue
                if code:
                    return code
        # Fallback: Try to fetch code files directly via GitHub API using default branch
        try:
            branch = default_branch or 'main'
            api_url = f"https://api.github.com/repos/{user}/{repo}/git/trees/{branch}?recursive=1"
            r = requests.get(api_url)
            if r.status_code != 200:
                # Try master branch
                api_url = f"https://api.github.com/repos/{user}/{repo}/git/trees/master?recursive=1"
                r = requests.get(api_url)
                branch = 'master'
            if r.status_code == 200:
                tree = r.json().get("tree", [])
                code = ""
                for item in tree:
                    path = item.get("path", "")
                    if any(path.endswith(f".{ext}") for ext in ['py', 'js', 'java', 'cpp', 'c', 'ts', 'rb', 'go', 'php']):
                        file_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"
                        file_r = requests.get(file_url)
                        if file_r.status_code != 200:
                            # Try main/master fallback for file
                            for alt_branch in branches_to_try:
                                if alt_branch == branch:
                                    continue
                                file_url_alt = f"https://raw.githubusercontent.com/{user}/{repo}/{alt_branch}/{path}"
                                file_r_alt = requests.get(file_url_alt)
                                if file_r_alt.status_code == 200:
                                    code += file_r_alt.text + "\n\n"
                                    break
                        else:
                            code += file_r.text + "\n\n"
                if code:
                    return code
                else:
                    return "No code files found in repo (via API fallback)."
            else:
                return f"Failed to download repo zip and fetch files via GitHub API for {url}"
        except Exception as e2:
            return f"Failed to download repo zip and fetch files via GitHub API for {url}: {e2}"
    except Exception as e:
        return f"Error analyzing repo: {e}"

def analyze_repo(url):
    # For compatibility with AI_assessor.py
    return analyze_github_repo(url)
