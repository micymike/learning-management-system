#!/usr/bin/env python3
"""
Test suite for MongoDB Assessment System
This file tests all CRUD operations and functionality
"""

import json
import sys
from datetime import datetime
from typing import Dict, List

# Import the assessment system (assuming the main code is in assessment_system.py)
try:
    from assessment_system import AssessmentSystemMongoDB
except ImportError:
    print("❌ Could not import AssessmentSystemMongoDB")
    print("Make sure the main code is saved as 'assessment_system.py' in the same directory")
    sys.exit(1)


class TestAssessmentSystem:
    def __init__(self):
        self.system = None
        self.test_data = {
            'assessment_ids': [],
            'student_ids': [],
            'student_assessment_ids': []
        }
        self.passed = 0
        self.failed = 0
    
    def setup(self):
        """Initialize the test environment"""
        print("🔧 Setting up test environment...")
        try:
            self.system = AssessmentSystemMongoDB(database_name="test_assessment_system")
            print("✅ Connected to MongoDB test database")
            
            # Clear test data
            self.system.db.assessments.delete_many({})
            self.system.db.students.delete_many({})
            self.system.db.student_assessments.delete_many({})
            print("✅ Cleared existing test data")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
        return True
    
    def teardown(self):
        """Clean up test environment"""
        print("\n🧹 Cleaning up test environment...")
        try:
            if self.system:
                # Clean up test data
                self.system.db.assessments.delete_many({})
                self.system.db.students.delete_many({})
                self.system.db.student_assessments.delete_many({})
                self.system.close_connection()
                print("✅ Test environment cleaned up")
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
    
    def assert_test(self, condition, test_name):
        """Helper method to track test results"""
        if condition:
            print(f"✅ {test_name}")
            self.passed += 1
        else:
            print(f"❌ {test_name}")
            self.failed += 1
    
    def test_assessment_crud(self):
        """Test Assessment CRUD operations"""
        print("\n📝 Testing Assessment CRUD operations...")
        
        # Test Create
        assessment_id = self.system.assessments.create(
            name="Python Fundamentals Test",
            rubric="Syntax: 25pts, Logic: 25pts, Style: 25pts, Testing: 25pts",
            results={"total_submissions": 0}
        )
        self.test_data['assessment_ids'].append(assessment_id)
        self.assert_test(assessment_id is not None, "Assessment creation")
        
        # Test Read
        assessment_doc = self.system.assessments.find_by_id(assessment_id)
        self.assert_test(
            assessment_doc is not None and assessment_doc['name'] == "Python Fundamentals Test",
            "Assessment retrieval by ID"
        )
        
        # Test to_dict conversion
        assessment_dict = self.system.assessments.to_dict(assessment_doc)
        expected_keys = {'id', 'name', 'date', 'rubric', 'results', 'created_at', 'updated_at'}
        self.assert_test(
            set(assessment_dict.keys()) == expected_keys,
            "Assessment to_dict conversion"
        )
        
        # Test Update
        updated = self.system.assessments.update(
            assessment_id,
            name="Python Fundamentals Test - Updated",
            results={"total_submissions": 5}
        )
        self.assert_test(updated, "Assessment update")
        
        # Verify update
        updated_doc = self.system.assessments.find_by_id(assessment_id)
        self.assert_test(
            updated_doc['name'] == "Python Fundamentals Test - Updated",
            "Assessment update verification"
        )
        
        # Test find_all
        all_assessments = self.system.assessments.find_all()
        self.assert_test(len(all_assessments) >= 1, "Assessment find_all")
    
    def test_student_crud(self):
        """Test Student CRUD operations"""
        print("\n👨‍🎓 Testing Student CRUD operations...")
        
        # Test Create
        student_id = self.system.students.create(
            name="Alice Johnson",
            email="alice.johnson@example.com",
            github_username="alice_codes"
        )
        self.test_data['student_ids'].append(student_id)
        self.assert_test(student_id is not None, "Student creation")
        
        # Test Read by ID
        student_doc = self.system.students.find_by_id(student_id)
        self.assert_test(
            student_doc is not None and student_doc['name'] == "Alice Johnson",
            "Student retrieval by ID"
        )
        
        # Test Read by email
        student_by_email = self.system.students.find_by_email("alice.johnson@example.com")
        self.assert_test(
            student_by_email is not None and student_by_email['email'] == "alice.johnson@example.com",
            "Student retrieval by email"
        )
        
        # Test to_dict conversion
        student_dict = self.system.students.to_dict(student_doc)
        expected_keys = {'id', 'name', 'email', 'github_username', 'created_at', 'updated_at', 'assessment_count'}
        self.assert_test(
            set(student_dict.keys()) == expected_keys,
            "Student to_dict conversion"
        )
        
        # Test assessment_count (should be 0 initially)
        self.assert_test(
            student_dict['assessment_count'] == 0,
            "Student assessment count (initially 0)"
        )
        
        # Test Update
        updated = self.system.students.update(
            student_id,
            name="Alice Johnson-Smith",
            github_username="alice_codes_pro"
        )
        self.assert_test(updated, "Student update")
        
        # Create another student for testing
        student_id2 = self.system.students.create(
            name="Bob Wilson",
            email="bob.wilson@example.com"
        )
        self.test_data['student_ids'].append(student_id2)
        
        # Test find_all
        all_students = self.system.students.find_all()
        self.assert_test(len(all_students) >= 2, "Student find_all")
    
    def test_student_assessment_crud(self):
        """Test StudentAssessment CRUD operations"""
        print("\n📊 Testing StudentAssessment CRUD operations...")
        
        # Ensure we have test data
        if not self.test_data['assessment_ids'] or not self.test_data['student_ids']:
            print("❌ Missing test data for StudentAssessment tests")
            return
        
        assessment_id = self.test_data['assessment_ids'][0]
        student_id = self.test_data['student_ids'][0]
        
        # Test Create
        student_assessment_id = self.system.student_assessments.create(
            student_id=student_id,
            assessment_id=assessment_id,
            scores={
                "syntax": 23,
                "logic": 25,
                "style": 22,
                "testing": 24
            },
            repo_url="https://github.com/alice_codes/python-fundamentals",
            submission="Completed all requirements with excellent code quality."
        )
        self.test_data['student_assessment_ids'].append(student_assessment_id)
        self.assert_test(student_assessment_id is not None, "StudentAssessment creation")
        
        # Test Read by ID
        sa_doc = self.system.student_assessments.find_by_id(student_assessment_id)
        self.assert_test(
            sa_doc is not None and sa_doc['repo_url'] == "https://github.com/alice_codes/python-fundamentals",
            "StudentAssessment retrieval by ID"
        )
        
        # Test to_dict conversion
        sa_dict = self.system.student_assessments.to_dict(sa_doc, self.system.db)
        expected_keys = {'id', 'student_id', 'assessment_id', 'assessment_name', 'scores', 'repo_url', 'created_at', 'average_score'}
        self.assert_test(
            set(sa_dict.keys()) == expected_keys,
            "StudentAssessment to_dict conversion"
        )
        
        # Test average score calculation
        expected_avg = (23 + 25 + 22 + 24) / 4  # 23.5
        self.assert_test(
            abs(sa_dict['average_score'] - expected_avg) < 0.01,
            f"Average score calculation (expected {expected_avg}, got {sa_dict['average_score']})"
        )
        
        # Test assessment_name population
        self.assert_test(
            sa_dict['assessment_name'] is not None,
            "Assessment name population in StudentAssessment"
        )
        
        # Test find by student
        student_assessments = self.system.student_assessments.find_by_student_id(student_id)
        self.assert_test(len(student_assessments) >= 1, "Find StudentAssessments by student ID")
        
        # Test find by assessment
        assessment_submissions = self.system.student_assessments.find_by_assessment_id(assessment_id)
        self.assert_test(len(assessment_submissions) >= 1, "Find StudentAssessments by assessment ID")
        
        # Test find by student and assessment
        specific_sa = self.system.student_assessments.find_by_student_and_assessment(student_id, assessment_id)
        self.assert_test(specific_sa is not None, "Find specific StudentAssessment")
        
        # Test Update
        updated = self.system.student_assessments.update(
            student_assessment_id,
            scores={
                "syntax": 25,
                "logic": 25,
                "style": 24,
                "testing": 25
            }
        )
        self.assert_test(updated, "StudentAssessment update")
    
    def test_relationships(self):
        """Test relationship functionality"""
        print("\n🔗 Testing Relationship functionality...")
        
        if not self.test_data['student_ids']:
            print("❌ Missing student data for relationship tests")
            return
        
        student_id = self.test_data['student_ids'][0]
        
        # Test student assessment count after creating assessment
        student_doc = self.system.students.find_by_id(student_id)
        student_dict = self.system.students.to_dict(student_doc)
        self.assert_test(
            student_dict['assessment_count'] >= 1,
            f"Student assessment count after creating assessment (got {student_dict['assessment_count']})"
        )
        
        # Test to_dict_with_assessments
        student_with_assessments = self.system.students.to_dict_with_assessments(student_doc)
        self.assert_test(
            'assessments' in student_with_assessments and len(student_with_assessments['assessments']) >= 1,
            "Student to_dict_with_assessments"
        )
        
        # Verify assessment data in relationship
        assessment_data = student_with_assessments['assessments'][0]
        expected_assessment_keys = {'id', 'student_id', 'assessment_id', 'assessment_name', 'scores', 'repo_url', 'created_at', 'average_score'}
        self.assert_test(
            set(assessment_data.keys()) == expected_assessment_keys,
            "Assessment data completeness in relationship"
        )
    
    def test_cascade_delete(self):
        """Test cascade delete functionality"""
        print("\n🗑️ Testing Cascade delete functionality...")
        
        if not self.test_data['student_ids']:
            print("❌ Missing student data for cascade delete test")
            return
        
        # Create a new student for deletion test
        test_student_id = self.system.students.create(
            name="Test Student",
            email="test@example.com"
        )
        
        # Create an assessment for this student
        if self.test_data['assessment_ids']:
            assessment_id = self.test_data['assessment_ids'][0]
            sa_id = self.system.student_assessments.create(
                student_id=test_student_id,
                assessment_id=assessment_id,
                scores={"test": 100}
            )
            
            # Verify assessment was created
            sa_before = self.system.student_assessments.find_by_student_id(test_student_id)
            self.assert_test(len(sa_before) == 1, "StudentAssessment created before cascade delete")
            
            # Delete the student (should cascade delete assessments)
            deleted = self.system.students.delete(test_student_id)
            self.assert_test(deleted, "Student deletion")
            
            # Verify assessments were also deleted
            sa_after = self.system.student_assessments.find_by_student_id(test_student_id)
            self.assert_test(len(sa_after) == 0, "StudentAssessments cascade deleted")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n⚠️ Testing Edge cases and error handling...")
        
        # Test with invalid ObjectIds
        invalid_doc = self.system.students.find_by_id("invalid_id")
        self.assert_test(invalid_doc is None, "Handle invalid ObjectId gracefully")
        
        # Test average score with empty scores
        empty_scores_avg = self.system.student_assessments._calculate_average_score({})
        self.assert_test(empty_scores_avg == 0.0, "Handle empty scores in average calculation")
        
        # Test average score with mixed data types
        mixed_scores = {"numeric": 85, "text": "excellent", "another_numeric": 90}
        mixed_avg = self.system.student_assessments._calculate_average_score(mixed_scores)
        expected_mixed_avg = (85 + 90) / 2  # 87.5
        self.assert_test(
            abs(mixed_avg - expected_mixed_avg) < 0.01,
            f"Handle mixed data types in scores (expected {expected_mixed_avg}, got {mixed_avg})"
        )
        
        # Test to_dict with None document
        none_dict = self.system.assessments.to_dict(None)
        self.assert_test(none_dict == {}, "Handle None document in to_dict")
    
    def test_data_integrity(self):
        """Test data integrity and constraints"""
        print("\n🔒 Testing Data integrity...")
        
        # Test unique email constraint (should fail gracefully)
        try:
            student_id1 = self.system.students.create(
                name="First Student",
                email="duplicate@example.com"
            )
            
            # This should fail due to unique email constraint
            student_id2 = self.system.students.create(
                name="Second Student",
                email="duplicate@example.com"
            )
            
            # If we get here, the constraint didn't work as expected
            self.assert_test(False, "Unique email constraint enforcement")
            
        except Exception as e:
            # This is expected due to unique constraint
            self.assert_test(True, "Unique email constraint enforcement")
    
    def display_sample_data(self):
        """Display sample data to verify everything looks correct"""
        print("\n📋 Sample Data Display:")
        
        try:
            # Display an assessment
            if self.test_data['assessment_ids']:
                assessment_doc = self.system.assessments.find_by_id(self.test_data['assessment_ids'][0])
                assessment_dict = self.system.assessments.to_dict(assessment_doc)
                print("\n📝 Sample Assessment:")
                print(json.dumps(assessment_dict, indent=2))
            
            # Display a student with assessments
            if self.test_data['student_ids']:
                student_doc = self.system.students.find_by_id(self.test_data['student_ids'][0])
                student_dict = self.system.students.to_dict_with_assessments(student_doc)
                print("\n👨‍🎓 Sample Student with Assessments:")
                print(json.dumps(student_dict, indent=2))
                
        except Exception as e:
            print(f"❌ Error displaying sample data: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting MongoDB Assessment System Test Suite")
        print("=" * 60)
        
        if not self.setup():
            return
        
        try:
            # Run all test methods
            self.test_assessment_crud()
            self.test_student_crud()
            self.test_student_assessment_crud()
            self.test_relationships()
            self.test_cascade_delete()
            self.test_edge_cases()
            self.test_data_integrity()
            
            # Display sample data
            self.display_sample_data()
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.teardown()
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS:")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print("🎉 All tests passed! The MongoDB Assessment System is working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the implementation.")


if __name__ == "__main__":
    print("MongoDB Assessment System Test Suite")
    print("Make sure MongoDB is running before executing this test!")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        sys.exit(0)
    
    tester = TestAssessmentSystem()
    tester.run_all_tests()