from flask import Flask
from routes.routes import routes_blueprint
import os
from dotenv import load_dotenv
import mongoengine

def create_app():
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        raise RuntimeError("MONGODB_URL not set in environment")
    mongoengine.connect(host=mongodb_url)
    app = Flask(__name__)
    app.register_blueprint(routes_blueprint)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")
    return app

app = create_app()
