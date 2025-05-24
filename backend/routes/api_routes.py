"""
Combined API routes for both traditional and RAG-based assessment
"""
from flask import Blueprint, request, jsonify
from AI_assessor import assess_code, client
from rag_assessor import get_assessor
import os

api_routes = Blueprint('api', __name__)

@api_routes.route("/api/assess", methods=["POST"])
def assess():
    """Assess code using either traditional or RAG-based approach"""
    data = request.json
    code = data.get('code')
    rubric = data.get('rubric')
    use_rag = data.get('use_rag', False)
    
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    if not rubric:
        return jsonify({"error": "No rubric provided"}), 400
    
    try:
        if use_rag:
            # Use RAG-based assessment
            assessor = get_assessor()
            result = assessor.assess_code(code, rubric)
        else:
            # Use traditional assessment
            result = assess_code(code, rubric, client)
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_routes.route("/api/compare-assessment", methods=["POST"])
def compare_assessment():
    """Compare traditional and RAG-based assessment results"""
    data = request.json
    code = data.get('code')
    rubric = data.get('rubric')
    
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    if not rubric:
        return jsonify({"error": "No rubric provided"}), 400
    
    try:
        # Get traditional assessment
        traditional_result = assess_code(code, rubric, client)
        
        # Get RAG-based assessment
        assessor = get_assessor()
        rag_result = assessor.assess_code(code, rubric)
        
        return jsonify({
            "success": True, 
            "traditional": traditional_result,
            "rag": rag_result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500