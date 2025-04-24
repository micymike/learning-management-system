# This file is used in the backend to handle csv files, this csv file contains student names and their github urls.
import csv
from io import StringIO

def process_csv(file_storage):
    """
    Accepts a Flask file storage object, parses CSV, and returns a list of dicts with name and repo_url.
    Expects columns: name, repo_url (or github_url)
    """
    # Flask provides a file-like object, so decode bytes to string
    content = file_storage.read().decode('utf-8')
    file_storage.seek(0)  # Reset file pointer for any further use
    reader = csv.DictReader(StringIO(content))
    results = []
    for row in reader:
        name = row.get('name') or row.get('student')
        repo_url = row.get('repo_url') or row.get('github_url')
        if name and repo_url:
            results.append({'name': name.strip(), 'repo_url': repo_url.strip()})
    return results
