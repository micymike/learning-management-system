import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from config.settings import (
    STUDENT_NAME_COL, GITHUB_URL_COL, GRADE_COL, FEEDBACK_COL,
    INPUT_EXCEL, OUTPUT_EXCEL
)

class ExcelTools:
    def __init__(self):
        self.input_path = INPUT_EXCEL
        self.output_path = OUTPUT_EXCEL
    
    def read_student_data(self) -> List[Dict]:
        """Read student data from input Excel file."""
        try:
            df = pd.read_excel(self.input_path)
            
            # Validate required columns
            required_cols = [STUDENT_NAME_COL, GITHUB_URL_COL]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Convert to list of dictionaries
            students = []
            for _, row in df.iterrows():
                student = {
                    "name": str(row[STUDENT_NAME_COL]).strip(),
                    "github_url": str(row[GITHUB_URL_COL]).strip()
                }
                
                # Skip empty rows
                if student["name"] and student["github_url"]:
                    students.append(student)
            
            return students
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {self.input_path}")
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def initialize_output_file(self):
        """Initialize the output Excel file with headers."""
        try:
            # Create DataFrame with headers
            df = pd.DataFrame(columns=[
                STUDENT_NAME_COL,
                GRADE_COL,
                FEEDBACK_COL
            ])
            
            # Save to Excel
            df.to_excel(self.output_path, index=False)
            
        except Exception as e:
            raise Exception(f"Error initializing output file: {str(e)}")
    
    def append_results(self, results: List[Dict]):
        """Append batch results to the output Excel file."""
        try:
            # Read existing data if file exists
            if self.output_path.exists():
                existing_df = pd.read_excel(self.output_path)
            else:
                existing_df = pd.DataFrame(columns=[
                    STUDENT_NAME_COL, GRADE_COL, FEEDBACK_COL
                ])
            
            # Create DataFrame from new results
            new_data = []
            for result in results:
                new_data.append({
                    STUDENT_NAME_COL: result["name"],
                    GRADE_COL: result["grade"],
                    FEEDBACK_COL: self._format_feedback(result["feedback"])
                })
            
            new_df = pd.DataFrame(new_data)
            
            # Combine and save
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_excel(self.output_path, index=False)
            
            return True
            
        except Exception as e:
            print(f"Error appending results: {str(e)}")
            return False
    
    def update_student_result(self, student_name: str, grade: int, feedback: List[str]):
        """Update or add a single student's result."""
        try:
            # Read existing data
            if self.output_path.exists():
                df = pd.read_excel(self.output_path)
            else:
                df = pd.DataFrame(columns=[
                    STUDENT_NAME_COL, GRADE_COL, FEEDBACK_COL
                ])
            
            # Check if student already exists
            student_exists = df[STUDENT_NAME_COL] == student_name
            
            if student_exists.any():
                # Update existing record
                df.loc[student_exists, GRADE_COL] = grade
                df.loc[student_exists, FEEDBACK_COL] = self._format_feedback(feedback)
            else:
                # Add new record
                new_row = {
                    STUDENT_NAME_COL: student_name,
                    GRADE_COL: grade,
                    FEEDBACK_COL: self._format_feedback(feedback)
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save updated data
            df.to_excel(self.output_path, index=False)
            return True
            
        except Exception as e:
            print(f"Error updating student result: {str(e)}")
            return False
    
    def get_existing_results(self) -> List[str]:
        """Get list of students who already have results."""
        try:
            if not self.output_path.exists():
                return []
            
            df = pd.read_excel(self.output_path)
            return df[STUDENT_NAME_COL].tolist()
            
        except Exception as e:
            print(f"Error reading existing results: {str(e)}")
            return []
    
    def _format_feedback(self, feedback: List[str]) -> str:
        """Format feedback list into a single string."""
        if not feedback:
            return "No feedback provided"
        
        # Join feedback items with bullet points
        formatted = []
        for item in feedback:
            if item.strip():
                formatted.append(f"• {item.strip()}")
        
        return "\n".join(formatted) if formatted else "No feedback provided"
    
    def create_sample_input_file(self, sample_students: List[Dict]):
        """Create a sample input Excel file for testing."""
        try:
            df = pd.DataFrame(sample_students)
            df.to_excel(self.input_path, index=False)
            print(f"Sample input file created: {self.input_path}")
            
        except Exception as e:
            print(f"Error creating sample file: {str(e)}")
    
    def validate_input_file(self) -> bool:
        """Validate that the input file exists and has the correct format."""
        try:
            if not self.input_path.exists():
                return False
            
            df = pd.read_excel(self.input_path)
            required_cols = [STUDENT_NAME_COL, GITHUB_URL_COL]
            
            return all(col in df.columns for col in required_cols)
            
        except Exception as e:
            print(f"Error validating input file: {str(e)}")
            return False