from flask import Blueprint, request, jsonify
from agents.orchestrator import AgentOrchestrator
from agents.vector_agent import VectorAgent
from agents.graph_rag_agent import GraphRAGAgent

enhanced_routes = Blueprint('enhanced_routes', __name__)

@enhanced_routes.route('/api/enhanced-assessment', methods=['POST'])
def enhanced_assessment():
    """
    Enhanced assessment with vector DB, batch processing, and consistency checks
    """
    try:
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No CSV file provided'}), 400
        
        csv_file = request.files['csv_file']
        rubric_text = request.form.get('rubric')
        
        if not rubric_text:
            return jsonify({'error': 'No rubric provided'}), 400
        
        # Use enhanced orchestrator
        orchestrator = AgentOrchestrator()
        
        csv_data = {
            'file_content': csv_file.read().decode('utf-8'),
            'filename': csv_file.filename
        }
        
        import asyncio
        result = asyncio.run(orchestrator.process_assessment(csv_data, rubric_text))
        
        return jsonify({
            'message': 'Enhanced assessment completed',
            'results': result.get('results', []),
            'consistency_metrics': result.get('consistency_metrics', []),
            'summary': result.get('summary', {}),
            'token_savings': '~50% reduction through batch processing'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_routes.route('/api/query-context', methods=['POST'])
def query_context():
    """
    Query vector database for similar code patterns
    """
    try:
        data = request.get_json()
        query = data.get('query')
        
        vector_agent = VectorAgent()
        import asyncio
        result = asyncio.run(vector_agent.process({
            'action': 'retrieve',
            'query': query,
            'n_results': 5
        }))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_routes.route('/api/find-similar-students', methods=['POST'])
def find_similar_students():
    """
    Use Graph RAG to find students with similar code patterns
    """
    try:
        data = request.get_json()
        student_name = data.get('student_name')
        
        graph_agent = GraphRAGAgent()
        import asyncio
        result = asyncio.run(graph_agent.process({
            'action': 'query_graph',
            'student_name': student_name
        }))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500