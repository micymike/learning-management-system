#!/usr/bin/env python3
"""
Simple MongoDB connection test
Run this first to ensure MongoDB is working
"""

import sys
from datetime import datetime

def test_mongodb_connection():
    """Test basic MongoDB connection"""
    print("🔍 Testing MongoDB Connection...")
    
    try:
        from pymongo import MongoClient
        print("✅ PyMongo imported successfully")
    except ImportError:
        print("❌ PyMongo not installed. Run: pip install pymongo")
        return False
    
    try:
        # Try to connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Get server info
        server_info = client.server_info()
        print(f"✅ MongoDB version: {server_info['version']}")
        
        # Test basic operations
        db = client.test_connection_db
        collection = db.test_collection
        
        # Insert a test document
        test_doc = {
            'message': 'Hello MongoDB!',
            'timestamp': datetime.utcnow(),
            'test': True
        }
        
        result = collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read the document back
        retrieved_doc = collection.find_one({'_id': result.inserted_id})
        if retrieved_doc and retrieved_doc['message'] == 'Hello MongoDB!':
            print("✅ Test document retrieved successfully")
        else:
            print("❌ Failed to retrieve test document")
            return False
        
        # Clean up
        collection.delete_one({'_id': result.inserted_id})
        client.drop_database('test_connection_db')
        print("✅ Test cleanup completed")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure MongoDB is running:")
        print("   - sudo systemctl start mongod (Linux)")
        print("   - brew services start mongodb/brew/mongodb-community (macOS)")
        print("   - Start MongoDB service (Windows)")
        print("2. Check if MongoDB is listening on port 27017:")
        print("   - netstat -an | grep 27017")
        print("3. Try connecting manually:")
        print("   - mongosh (or mongo for older versions)")
        return False

def test_pymongo_features():
    """Test PyMongo features we'll use"""
    print("\n🔧 Testing PyMongo Features...")
    
    try:
        from pymongo import MongoClient, ASCENDING
        from bson import ObjectId
        import json
        
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client.test_features_db
        
        # Test collections
        students = db.students
        assessments = db.assessments
        
        # Test ObjectId
        test_id = ObjectId()
        print(f"✅ ObjectId created: {test_id}")
        
        # Test JSON operations
        test_data = {
            '_id': test_id,
            'scores': {'math': 95, 'science': 87, 'english': 92},
            'metadata': {'attempts': 3, 'time_spent': 45}
        }
        
        # Insert and retrieve
        students.insert_one(test_data)
        retrieved = students.find_one({'_id': test_id})
        
        if retrieved and retrieved['scores']['math'] == 95:
            print("✅ JSON data storage and retrieval working")
        else:
            print("❌ JSON data operations failed")
            return False
        
        # Test indexing
        students.create_index([("email", ASCENDING)], unique=True, sparse=True)
        print("✅ Index creation working")
        
        # Test aggregation (calculate average)
        scores = retrieved['scores']
        avg_score = sum(score for score in scores.values() if isinstance(score, (int, float))) / len(scores)
        print(f"✅ Score calculation working: average = {avg_score}")
        
        # Cleanup
        client.drop_database('test_features_db')
        client.close()
        
        return True
        
    except Exception as e:
        print(f"❌ PyMongo features test failed: {e}")
        return False

def main():
    print("MongoDB Assessment System - Connection Test")
    print("=" * 50)
    
    # Test basic connection
    if not test_mongodb_connection():
        print("\n❌ Basic MongoDB connection failed. Fix connection issues before proceeding.")
        return False
    
    # Test PyMongo features
    if not test_pymongo_features():
        print("\n❌ PyMongo features test failed. Check your PyMongo installation.")
        return False
    
    print("\n🎉 All connection tests passed!")
    print("✅ MongoDB is ready for the Assessment System")
    print("\nNext steps:")
    print("1. Save the main assessment system code as 'assessment_system.py'")
    print("2. Save the test suite as 'test_assessment_system.py'")
    print("3. Run: python test_assessment_system.py")
    
    return True

if __name__ == "__main__":
    main()