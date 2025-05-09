from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    noise_cancellation,
)

from flask import Flask, request, jsonify, send_file
from backend.csv_analyzer import process_csv, generate_scores_excel, format_scores_for_display, score_manager
import pandas as pd
import requests
import re
import os
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.\n\n named Mickey")


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="coral"
        )
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
     
        ),

    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        students_data = process_csv(file)
        # Example scores structure (replace with your actual scoring logic)
        scores = []
        for student in students_data:
            score = {
                'Name': student['name'],
                'Group': student.get('group', ''),
                'Project Name': student.get('project_name', ''),
                'Documentation': 5,  # Example scores
                'Code Quality': 4,
                'Functionality': 5,
                'Total Score': 14
            }
            scores.append(score)
        
        # Add scores to score manager
        updated_scores = score_manager.add_scores(scores)
        
        # Format scores for display
        html_table = format_scores_for_display(updated_scores)
        return jsonify({
            'html_table': html_table,
            'scores': updated_scores
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/analyze', methods=['POST'])
def analyze_repositories():
    """
    Analyze GitHub repositories based on the provided CSV and rubric.
    
    Expected form data:
    - csv_file: CSV file with student names and GitHub repository URLs
    - rubric: Text content of the rubric
    - assessment_name: Name of the assessment
    
    Returns:
    - JSON with analysis results
    """
    try:
        # Check authentication
        # This is a placeholder - implement actual authentication check
        is_authenticated = True
        if not is_authenticated:
            return jsonify({
                'error': 'Authentication required',
                'authenticated': False
            }), 401
        
        # Validate request data
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No CSV file provided'}), 400
        
        csv_file = request.files['csv_file']
        rubric_text = request.form.get('rubric', '')
        assessment_name = request.form.get('assessment_name', 'Unnamed Assessment')
        
        if not csv_file or csv_file.filename == '':
            return jsonify({'error': 'Empty CSV file'}), 400
        
        # Process the CSV file to get student data
        students_data = process_csv(csv_file)
        
        if not students_data:
            return jsonify({'error': 'No valid student data found in CSV'}), 400
        
        # Parse the rubric to extract criteria and scoring guidelines
        criteria = parse_rubric(rubric_text)
        
        # Analyze each repository based on the rubric
        results = []
        for student in students_data:
            # Get the GitHub repository URL
            repo_url = student.get('repo_url', '')
            if not repo_url:
                # Skip students without a repository URL
                continue
            
            # Analyze the repository
            analysis_result = analyze_repository(repo_url, criteria)
            
            # Calculate the total score
            total_score = sum(analysis_result.get('scores', {}).values())
            
            # Create the result object
            result = {
                'id': len(results),
                'name': student.get('name', 'Unknown'),
                'github': repo_url,
                'group': student.get('group', 'Unassigned'),
                'score': total_score,
                'details': analysis_result.get('details', {}),
                'scores': analysis_result.get('scores', {}),
                'report': analysis_result.get('report', '')
            }
            
            results.append(result)
        
        # Return the analysis results
        return jsonify({
            'assessment_name': assessment_name,
            'results': results,
            'criteria': criteria
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'An error occurred during analysis'
        }), 500


def parse_rubric(rubric_text):
    """
    Parse the rubric text to extract criteria and scoring guidelines.
    
    Args:
        rubric_text (str): The text content of the rubric
        
    Returns:
        dict: Dictionary of criteria and their weights
    """
    # Default criteria if parsing fails
    default_criteria = {
        'Code Quality': 30,
        'Functionality': 40,
        'Documentation': 20,
        'Best Practices': 10
    }
    
    if not rubric_text:
        return default_criteria
    
    try:
        # Try to extract criteria and weights using regex
        criteria = {}
        
        # Look for patterns like "Code Quality (30%)" or "Code Quality: 30 points"
        patterns = [
            r'([A-Za-z\s]+)\s*\((\d+)%\)',  # Matches "Code Quality (30%)"
            r'([A-Za-z\s]+)\s*:\s*(\d+)\s*points',  # Matches "Code Quality: 30 points"
            r'([A-Za-z\s]+)\s*-\s*(\d+)'  # Matches "Code Quality - 30"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, rubric_text)
            for match in matches:
                criteria_name = match[0].strip()
                weight = int(match[1])
                criteria[criteria_name] = weight
        
        # If no criteria were found, use the default
        if not criteria:
            return default_criteria
        
        return criteria
    
    except Exception as e:
        print(f"Error parsing rubric: {e}")
        return default_criteria


def analyze_repository(repo_url, criteria):
    """
    Analyze a GitHub repository based on the provided criteria.
    
    Args:
        repo_url (str): URL of the GitHub repository
        criteria (dict): Dictionary of criteria and their weights
        
    Returns:
        dict: Analysis results including scores and report
    """
    # This is a simplified implementation
    # In a real-world scenario, you would:
    # 1. Clone the repository
    # 2. Analyze the code (using static analysis tools, etc.)
    # 3. Generate a detailed report
    
    try:
        # Extract username and repo name from URL
        # Example: https://github.com/username/repo
        parts = repo_url.strip('/').split('/')
        if len(parts) < 5 or 'github.com' not in parts:
            return {
                'scores': {criteria: 0 for criteria in criteria},
                'details': {'error': 'Invalid GitHub URL'},
                'report': 'Could not analyze repository: Invalid GitHub URL'
            }
        
        username = parts[-2]
        repo_name = parts[-1]
        
        # Use GitHub API to get repository information
        api_url = f"https://api.github.com/repos/{username}/{repo_name}"
        
        # Add GitHub token if available
        headers = {}
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        response = requests.get(api_url, headers=headers)
        
        if response.status_code != 200:
            return {
                'scores': {criteria: 0 for criteria in criteria},
                'details': {'error': f'GitHub API error: {response.status_code}'},
                'report': f'Could not analyze repository: GitHub API returned status code {response.status_code}'
            }
        
        repo_data = response.json()
        
        # Get repository languages
        languages_url = repo_data['languages_url']
        languages_response = requests.get(languages_url, headers=headers)
        languages = languages_response.json() if languages_response.status_code == 200 else {}
        
        # Get commit count
        commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
        commits_response = requests.get(commits_url, headers=headers)
        commit_count = len(commits_response.json()) if commits_response.status_code == 200 else 0
        
        # Calculate scores based on repository metrics
        scores = {}
        details = {}
        
        # Code Quality (based on languages, stars, forks)
        code_quality_score = min(10, repo_data.get('stargazers_count', 0)) + min(5, repo_data.get('forks_count', 0))
        code_quality_score = min(criteria.get('Code Quality', 30), code_quality_score * 3)
        scores['Code Quality'] = code_quality_score
        details['Code Quality'] = {
            'languages': languages,
            'stars': repo_data.get('stargazers_count', 0),
            'forks': repo_data.get('forks_count', 0)
        }
        
        # Functionality (based on commit count, open issues)
        functionality_score = min(10, commit_count // 5) + min(5, repo_data.get('open_issues_count', 0))
        functionality_score = min(criteria.get('Functionality', 40), functionality_score * 4)
        scores['Functionality'] = functionality_score
        details['Functionality'] = {
            'commit_count': commit_count,
            'open_issues': repo_data.get('open_issues_count', 0)
        }
        
        # Documentation (based on README size, wiki)
        has_wiki = repo_data.get('has_wiki', False)
        readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
        readme_response = requests.get(readme_url, headers=headers)
        readme_size = len(readme_response.json().get('content', '')) if readme_response.status_code == 200 else 0
        
        documentation_score = min(15, readme_size // 100) + (5 if has_wiki else 0)
        documentation_score = min(criteria.get('Documentation', 20), documentation_score)
        scores['Documentation'] = documentation_score
        details['Documentation'] = {
            'readme_size': readme_size,
            'has_wiki': has_wiki
        }
        
        # Best Practices (based on branch protection, license)
        has_license = repo_data.get('license', None) is not None
        best_practices_score = 5 if has_license else 0
        best_practices_score = min(criteria.get('Best Practices', 10), best_practices_score)
        scores['Best Practices'] = best_practices_score
        details['Best Practices'] = {
            'has_license': has_license
        }
        
        # Generate a report
        report = generate_report(repo_data, scores, details)
        
        return {
            'scores': scores,
            'details': details,
            'report': report
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'scores': {criteria: 0 for criteria in criteria},
            'details': {'error': str(e)},
            'report': f'Error analyzing repository: {str(e)}'
        }


def generate_report(repo_data, scores, details):
    """
    Generate a detailed report based on the analysis results.
    
    Args:
        repo_data (dict): Repository data from GitHub API
        scores (dict): Scores for each criterion
        details (dict): Details of the analysis
        
    Returns:
        str: Markdown-formatted report
    """
    total_score = sum(scores.values())
    
    report = f"# Repository Analysis Report\n\n"
    report += f"## Repository: {repo_data.get('full_name', 'Unknown')}\n\n"
    report += f"**Total Score: {total_score}**\n\n"
    
    report += "## Scores by Criterion\n\n"
    for criterion, score in scores.items():
        report += f"- **{criterion}**: {score}\n"
    
    report += "\n## Detailed Analysis\n\n"
    
    # Code Quality
    report += "### Code Quality\n\n"
    languages = details.get('Code Quality', {}).get('languages', {})
    if languages:
        report += "**Languages Used:**\n\n"
        for language, bytes_count in languages.items():
            report += f"- {language}: {bytes_count} bytes\n"
    
    stars = details.get('Code Quality', {}).get('stars', 0)
    forks = details.get('Code Quality', {}).get('forks', 0)
    report += f"\n**Stars:** {stars}\n"
    report += f"**Forks:** {forks}\n\n"
    
    # Functionality
    report += "### Functionality\n\n"
    commit_count = details.get('Functionality', {}).get('commit_count', 0)
    open_issues = details.get('Functionality', {}).get('open_issues', 0)
    report += f"**Commit Count:** {commit_count}\n"
    report += f"**Open Issues:** {open_issues}\n\n"
    
    # Documentation
    report += "### Documentation\n\n"
    readme_size = details.get('Documentation', {}).get('readme_size', 0)
    has_wiki = details.get('Documentation', {}).get('has_wiki', False)
    report += f"**README Size:** {readme_size} bytes\n"
    report += f"**Has Wiki:** {'Yes' if has_wiki else 'No'}\n\n"
    
    # Best Practices
    report += "### Best Practices\n\n"
    has_license = details.get('Best Practices', {}).get('has_license', False)
    report += f"**Has License:** {'Yes' if has_license else 'No'}\n\n"
    
    report += "## Recommendations\n\n"
    
    if scores.get('Code Quality', 0) < 20:
        report += "- Consider improving code quality by adding more comprehensive tests and refactoring complex functions.\n"
    
    if scores.get('Functionality', 0) < 30:
        report += "- Add more features or improve existing functionality to enhance the project.\n"
    
    if scores.get('Documentation', 0) < 15:
        report += "- Improve documentation by adding more details to the README and creating a wiki.\n"
    
    if scores.get('Best Practices', 0) < 8:
        report += "- Follow best practices by adding a license and setting up branch protection rules.\n"
    
    return report


@app.route('/download-scores', methods=['POST'])
def download_scores():
    try:
        scores = score_manager.get_scores()
        if not scores:
            return jsonify({'error': 'No scores available'}), 400
        
        excel_file = generate_scores_excel(scores)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='student_scores.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/delete-score/<int:score_id>', methods=['DELETE'])
def delete_score(score_id):
    try:
        updated_scores = score_manager.delete_score(score_id)
        html_table = format_scores_for_display(updated_scores)
        return jsonify({
            'html_table': html_table,
            'scores': updated_scores,
            'message': 'Score deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/delete-scores', methods=['POST'])
def delete_scores():
    try:
        score_ids = request.json.get('score_ids', [])
        if not score_ids:
            return jsonify({'error': 'No score IDs provided'}), 400
        
        updated_scores = score_manager.delete_scores(score_ids)
        html_table = format_scores_for_display(updated_scores)
        return jsonify({
            'html_table': html_table,
            'scores': updated_scores,
            'message': f'Successfully deleted {len(score_ids)} scores'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/clear-scores', methods=['POST'])
def clear_scores():
    try:
        updated_scores = score_manager.clear_scores()
        html_table = format_scores_for_display(updated_scores)
        return jsonify({
            'html_table': html_table,
            'scores': updated_scores,
            'message': 'All scores cleared successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    app.run(debug=True)