# this will be the entry point of the app
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_session import Session
from routes.routes import routes_blueprint
from routes.rag_routes import rag_routes
from routes.api_routes import api_routes
from routes.agent_routes import agent_routes
from routes.enhanced_routes import enhanced_routes
from models import db, Assessment
import os

# Initialize Flask app
app = Flask(__name__)

# Configure sessions
app.config.update(
    SESSION_TYPE='filesystem',
    SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key'),
    SESSION_COOKIE_SAMESITE='Strict',
    SESSION_COOKIE_SECURE=False  # Set to True in production with HTTPS
)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///assessments.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Initialize session
Session(app)

# Configure CORS with session support
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "https://codeanalyzer-bc.onrender.com",
            "https://directed-codeanalyzer.onrender.com"
        ],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Register blueprints
app.register_blueprint(routes_blueprint)
app.register_blueprint(rag_routes)
app.register_blueprint(api_routes)
app.register_blueprint(agent_routes)
app.register_blueprint(enhanced_routes)
app.register_blueprint(enhanced_routes)

# Assessment routes with error handling
@app.route('/assessments/<int:assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    try:
        assessment = Assessment.query.get_or_404(assessment_id)
        return jsonify({
            'id': assessment.id,
            'name': assessment.name,
            'created_at': assessment.created_at
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route moved to routes.py to avoid duplication

# Global error handlers to ensure JSON responses
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": str(error)}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed", "message": str(error)}), 405

@app.errorhandler(Exception)
def handle_exception(error):
    # For debugging, include error string; in production, you may want to hide details
    return jsonify({"error": "Internal server error", "message": str(error)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
