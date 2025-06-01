# this will be the entry point of the app
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_session import Session
from routes.routes import routes_blueprint
from models import Assessment
import os
from mongoengine import connect
from mongoengine.errors import ValidationError, InvalidDocumentError
from bson.objectid import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure sessions
app.config.update(
    SESSION_TYPE='filesystem',
    SECRET_KEY=os.getenv('SECRET_KEY'),
    SESSION_COOKIE_SAMESITE='Strict',
    SESSION_COOKIE_SECURE=False  # Set to True in production with HTTPS
)

if not app.config['SECRET_KEY']:
    raise ValueError("No SECRET_KEY set for Flask application. Please configure environment variables.")

# Configure MongoDB connection
MONGODB_URL = os.getenv('MONGODB_URL')
if not MONGODB_URL:
    raise ValueError("No MONGODB_URI set for Flask application. Please configure environment variables.")
connect(host=MONGODB_URL)

# Initialize session
Session(app)

# Configure CORS with session support
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://codeanalyzer-bc.onrender.com",
            "https://directed-codeanalyzer.onrender.com"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Origin", "X-Requested-With", "Accept"],
        "expose_headers": ["Content-Type", "Content-Disposition"],
        "supports_credentials": True
    }
})

# Add OPTIONS method handler for all routes to handle CORS preflight requests
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = app.make_default_options_response()
    response.headers.set('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,X-Requested-With,Accept')
    response.headers.set('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.set('Access-Control-Allow-Credentials', 'true')
    return response
app.register_blueprint(routes_blueprint)

# Assessment routes with error handling
@app.route('/assessments/<assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    try:
        print(f"Fetching assessment with ID: {assessment_id}")
        
        # Validate ObjectId format before querying
        try:
            if not ObjectId.is_valid(assessment_id):
                print(f"Invalid ObjectId format: {assessment_id}")
                return jsonify({'error': f"'{assessment_id}' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string"}), 400
        except InvalidId:
            return jsonify({'error': f"'{assessment_id}' is not a valid ObjectId"}), 400
            
        assessment = Assessment.objects(id=assessment_id).first()
        
        if not assessment:
            print(f"Assessment with ID {assessment_id} not found")
            return jsonify({'error': 'Assessment not found'}), 404
        
        # Convert to dictionary and add _id field for frontend compatibility
        assessment_dict = assessment.to_dict()
        assessment_dict['_id'] = assessment_dict['id']  # Add _id field for frontend
        
        print(f"Returning assessment: {assessment.name}")
        return jsonify(assessment_dict)
    except ValidationError as e:
        print(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error fetching assessment: {str(e)}")
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
