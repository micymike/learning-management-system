# this will be the entry point of the app
from flask import Flask, jsonify
from routes.routes import routes_blueprint

app = Flask(__name__)
app.register_blueprint(routes_blueprint)

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