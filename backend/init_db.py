from flask import Flask
from models import db
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    Migrate(app, db)
    
    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    print("Database initialized successfully.")
