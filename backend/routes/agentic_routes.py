agentic_routes = None  # placeholder to allow search/replace to work

from flask import Blueprint, request, jsonify
from agents.orchestrator import process_with_azure_openai, process_with_openai, AgentOrchestrator
import csv
import io
import asyncio

agentic_routes = Blueprint('agentic_routes', __name__)

@agentic_routes.route('/api/agentic/process', methods=['POST'])
def agentic_process():
    """
    Endpoint to process a repo/code using the double agentic system.
    Tries Azure OpenAI first; if a content policy error is encountered, falls back to OpenAI.
    Expects JSON: { "repo": ..., "prompt": ... }
    """
    data = request.get_json()
    repo = data.get('repo')
    prompt = data.get('prompt')

    # Try Azure OpenAI (primary)
    try:
        result = process_with_azure_openai(repo, prompt)
        if result.get('error') == 'content_policy':
            # Fallback to OpenAI (secondary)
            fallback_result = process_with_openai(repo, prompt)
            return jsonify({
                "llm_used": "openai",
                "result": fallback_result
            })
        return jsonify({
            "llm_used": "azure_openai",
            "result": result
        })
    except Exception as e:
        # Fallback to OpenAI on any error
        fallback_result = process_with_openai(repo, prompt)
        return jsonify({
            "llm_used": "openai",
            "result": fallback_result,
            "error": str(e)
        })

from flask import send_file
import io

@agentic_routes.route('/api/agentic/upload_csv', methods=['POST'])
def agentic_upload_csv():
    """
    Endpoint to process a batch of student repos from a CSV and a rubric.
    Accepts multipart/form-data with:
      - file: CSV file with columns 'name' and 'repo_url'
      - rubric: rubric file (text or JSON)
    Returns an Excel file with results for each student.
    """
    if 'file' not in request.files or 'rubric' not in request.files:
        return jsonify({"success": False, "error": "CSV file and rubric file are required."}), 400

    csv_file = request.files['file']
    rubric_file = request.files['rubric']

    # Read rubric content
    rubric_content = rubric_file.read().decode('utf-8')

    # Read CSV content as string
    csv_content = csv_file.read().decode('utf-8')
    csv_data = {
        'file_content': csv_content,
        'filename': csv_file.filename
    }

    # Use AgentOrchestrator for real assessment
    orchestrator = AgentOrchestrator()
    result = asyncio.run(orchestrator.process_assessment(csv_data, rubric_content))

    # Generate Excel file from results
    # The report_agent already generates the Excel file in _generate_excel_report
    # We'll call it directly here for download
    if 'results' in result and result['results']:
        from agents.report_agent import ReportAgent
        report_agent = ReportAgent()
        excel_bytes = asyncio.run(report_agent._generate_excel_report(result['results']))
        excel_bytes.seek(0)
        # Save to backend/result.xlsx
        import os
        os.makedirs("backend", exist_ok=True)
        with open("backend/result.xlsx", "wb") as f:
            f.write(excel_bytes.getbuffer())
        # Reset pointer for sending
        excel_bytes.seek(0)
        return send_file(
            excel_bytes,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='assessment_results.xlsx'
        )
    else:
        return jsonify(result)
