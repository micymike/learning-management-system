""" 
This file is responsible for assessing the AI generated code based on the given rubric.
It will assess the code and return the score in points as specified by the rubric.
"""

import os
import json
import requests
import pandas as pd
from repo_analyzer import analyze_repo
from csv_analyzer import process_csv, score_manager
from rubric_handler import load_rubric, calculate_percentage, is_passing_grade
import openai
import dotenv

dotenv.load_dotenv()

try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"Error: {e} check your environment for openai key")
    exit(1)

def assess_code(code, rubric, client):
    """
    Assesses the given code based on the provided rubric using OpenAI API.
    Returns points for each criterion based on the rubric's maximum points.
    
    Args:
        code (str): The code to assess
        rubric (str or list): The rubric to use for assessment
        client: OpenAI client instance
        
    Returns:
        dict: Dictionary with scores, max_points, percentages and pass/fail status
        
    Raises:
        ValueError: If rubric is empty or invalid
        Exception: For API errors or other issues
    """
    # Parse the rubric to get criteria and max points
    if isinstance(rubric, list) and isinstance(rubric[0], dict) and 'criterion' in rubric[0]:
        # Already parsed rubric with criteria and max_points
        rubric_items = rubric
    else:
        # Need to parse the rubric
        from rubric_handler import parse_rubric_lines
        if isinstance(rubric, list):
            rubric_items = parse_rubric_lines(rubric)
        else:
            # Assume it's a string
            rubric_items = parse_rubric_lines(rubric.strip().split('\n'))
    
    # Validate the rubric
    if not rubric_items:
        raise ValueError("Rubric cannot be empty. Please provide assessment criteria.")
    
    # Format rubric for the prompt
    rubric_str = "\n".join([f"- {item['criterion']} (Maximum points: {item['max_points']})" for item in rubric_items])
    
    # First pass: Deep analysis of the code
    analysis_system_prompt = """
You are an expert code analyzer with deep knowledge of software engineering principles, design patterns, and best practices.
Your task is to perform a thorough analysis of the provided code based EXACTLY on the rubric provided.

The rubric contains criteria with maximum points for each criterion.
You must analyze the code according to the EXACT criteria in the rubric.

Provide a detailed analysis that will be used as input for a subsequent scoring process.
"""

    analysis_user_prompt = f"""
Analyze the following code in depth, considering ONLY the rubric criteria that will be used for assessment:

Rubric:
{rubric_str}

Code to analyze:
{code}

Provide a detailed analysis of the code's strengths and weaknesses relative to EACH criterion in the rubric.
"""

    try:
        # First pass: Get detailed analysis
        analysis_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": analysis_system_prompt},
                {"role": "user", "content": analysis_user_prompt}
            ],
            temperature=0.3
        )
        code_analysis = analysis_response.choices[0].message.content

        # Second pass: Score based on the analysis and the exact rubric format
        scoring_system_prompt = """
You are a strict code assessor. Your task is to evaluate code based STRICTLY on the given rubric and a detailed code analysis.

IMPORTANT: Each rubric criterion has a maximum number of points. You must:
1. Assign points for each criterion (not exceeding the maximum)
2. Provide a brief justification for your point assignment
3. Be objective and consistent in your scoring

For each criterion in the rubric:
1. Determine how many points the code deserves based on the analysis
2. Ensure the points do not exceed the maximum allowed for that criterion
3. Provide a brief justification for your assessment

Your response MUST follow this exact format for each criterion:
Criterion: [Name of criterion]
Points: [Assigned points as a number] out of [Maximum points]
Justification: [Brief explanation]

Example:
Criterion: Code quality and organization
Points: 8 out of 10
Justification: The code is well-organized with clear function definitions, but lacks consistent naming conventions in some areas.
"""

        scoring_user_prompt = f"""
Rubric to use for assessment:
{rubric_str}

Detailed code analysis:
{code_analysis}

Evaluate the code according to EACH criterion in the rubric, assigning points that do not exceed the maximum for each criterion.
Return the assessment with points and justifications for each criterion.
"""

        scoring_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": scoring_system_prompt},
                {"role": "user", "content": scoring_user_prompt}
            ],
            temperature=0.2
        )
        assessment_content = scoring_response.choices[0].message.content

        # Parse the response into a dictionary with scores and justifications
        import re
        criterion_pattern = r'Criterion:\s*(.*?)\s*\n'
        points_pattern = r'Points:\s*(\d+(?:\.\d+)?)\s*out of\s*(\d+(?:\.\d+)?)'
        justification_pattern = r'Justification:\s*(.*?)(?:\n\n|\Z)'
        
        criteria_matches = re.findall(criterion_pattern, assessment_content, re.DOTALL)
        points_matches = re.findall(points_pattern, assessment_content, re.DOTALL)
        justification_matches = re.findall(justification_pattern, assessment_content, re.DOTALL)
        
        # Prepare the result dictionary
        result = {
            'criteria_scores': {},
            'total_points': 0,
            'max_points': 0,
            'percentage': 0,
            'passing': False
        }
        
        # Process each criterion
        if criteria_matches and points_matches and len(criteria_matches) == len(points_matches):
            for i in range(len(criteria_matches)):
                criterion = criteria_matches[i].strip()
                points = float(points_matches[i][0])
                max_points = float(points_matches[i][1])
                
                # Store the points and max points
                result['criteria_scores'][criterion] = {
                    'points': points,
                    'max_points': max_points
                }
                
                # Add to total points
                result['total_points'] += points
                result['max_points'] += max_points
                
                # Store justification if available
                if i < len(justification_matches):
                    result['criteria_scores'][criterion]['justification'] = justification_matches[i].strip()
        
        # Calculate percentage and passing status
        if result['max_points'] > 0:
            result['percentage'] = calculate_percentage(result['total_points'], result['max_points'])
            result['passing'] = is_passing_grade(result['percentage'])
        
        return result
    except Exception as e:
        raise Exception(f"Error assessing code: {str(e)}")

def read_sample_csv(file_path='backend/sample_students.csv'):
    """
    Read the sample CSV file containing student information.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def main():
    """
    Main function to process student repositories and assess their code.
    """
    try:
        # Load environment variables
        dotenv.load_dotenv()
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("Error: OpenAI API key not found in environment variables.")
            return
        
        # Read sample CSV
        students_df = read_sample_csv()
        if students_df is None:
            print("Error: Could not read student data.")
            return
        
        # Load rubric
        rubric = load_rubric()
        if not rubric:
            print("Error: Could not load rubric.")
            return
        
        # Process each student
        results = []
        for index, row in students_df.iterrows():
            student_name = row['name']
            repo_url = row['repo_url']
            
            print(f"Processing {student_name}'s repository: {repo_url}")
            
            try:
                # Analyze repository
                code = analyze_repo(repo_url)
                if not code:
                    print(f"Warning: No code found for {student_name}'s repository.")
                    continue
                
                # Assess code
                assessment = assess_code(code, rubric, client)
                
                # Add to results
                results.append({
                    'name': student_name,
                    'repo_url': repo_url,
                    'assessment': assessment
                })
                
                print(f"Assessment completed for {student_name}.")
                print(f"Total points: {assessment['total_points']} out of {assessment['max_points']}")
                print(f"Percentage: {assessment['percentage']}%")
                print(f"Passing: {'Yes' if assessment['passing'] else 'No'}")
            except Exception as e:
                print(f"Error processing {student_name}'s repository: {e}")
        
        # Save results
        if results:
            with open('assessment_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Assessment results saved to assessment_results.json")
        else:
            print("No assessment results to save.")
    
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()