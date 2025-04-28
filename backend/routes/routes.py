# this file defines the routes for the application
from flask import Blueprint, request, jsonify
from AI_assessor import assess_code, client
from csv_analyzer import process_csv
from rubric_handler import upload_rubric_file
from repo_analyzer import analyze_github_repo

def format_report(name, repo_url, assessment):
    """
    Returns a Markdown-formatted report for the assessment.
    """
    return f"""## Code Assessment Report for {name}

**Repository:** [{repo_url}]({repo_url})

---

### Assessment Summary
{assessment}

---
*Generated on request*
"""

routes_blueprint = Blueprint('routes', __name__)

@routes_blueprint.route("/assess", methods=["POST"])
def assess():
    code = request.form.get('code')
    rubric = request.form.get('rubric')
    result = assess_code(code, rubric, client)
    return jsonify({"result": result})

@routes_blueprint.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files['file']
    students = process_csv(file)
    results = []
    for student in students:
        name = student['name']
        repo_url = student['repo_url']
        # Analyze the repo (assuming analyze_github_repo returns code or analysis result)
        repo_analysis = analyze_github_repo(repo_url)
        # Assess the code (assuming assess_code can work with repo_analysis)
        assessment = assess_code(repo_analysis, None, client)  # Pass rubric if needed
        report = format_report(name, repo_url, assessment)
        results.append({
            "name": name,
            "repo_url": repo_url,
            "assessment": assessment,
            "report": report
        })
    return jsonify({"results": results})

@routes_blueprint.route("/upload_rubric", methods=["POST"])
def upload_rubric():
    file = request.files['file']
    content = file.read()
    result = upload_rubric_file(content)
    return jsonify({"result": result})

@routes_blueprint.route("/upload_github_url", methods=["POST"])
def upload_github_url():
    url = request.form.get('url')
    result = analyze_github_repo(url)
    return jsonify({"result": result})