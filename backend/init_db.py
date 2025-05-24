from flask import Flask
from mongoengine import connect
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/learning_management_system')
    connect(host=MONGODB_URI)
    
    return app

if __name__ == "__main__":
    app = create_app()
    print("MongoDB connection initialized successfully.")