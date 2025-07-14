from flask import Flask
from routes.agentic_routes import agentic_routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(agentic_routes)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
