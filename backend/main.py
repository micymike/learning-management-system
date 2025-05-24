# this will be the entry point of the app
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_session import Session
from routes.routes import routes_blueprint
from models import Assessment
import os
from mongoengine import connect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure sessions
app.config.update(
    SESSION_TYPE='filesystem',
    SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key'),
    SESSION_COOKIE_SAMESITE='Strict',
    SESSION_COOKIE_SECURE=False  # Set to True in production with HTTPS
)

# Configure MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/learning_management_system')
connect(host=MONGODB_URI)

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
app.register_blueprint(routes_blueprint)

# Assessment routes with error handling
@app.route('/assessments/<assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    try:
        assessment = Assessment.objects(id=assessment_id).first()
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        return jsonify(assessment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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