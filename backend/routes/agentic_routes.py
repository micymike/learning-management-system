from flask import Blueprint, request, jsonify
from agents.orchestrator import process_with_azure_openai, process_with_openai

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
