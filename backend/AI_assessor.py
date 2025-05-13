""" this file is responsible for assessing the AI generated code. so based on the given rubric, it will assess the code and return the score the data will be used to generate a report and also we will get the name of the student and the girhub url from csv.py and the analyzed codes from repo_analyzer.py we will use gpt3.5-turbo"""

import os
import json
import requests
import pandas as pd
from repo_analyzer import analyze_repo
from csv_analyzer import process_csv, score_manager
from rubric_handler import load_rubric
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
    Implements a two-pass evaluation for deeper analysis and more accurate scoring.
    
    Args:
        code (str): The code to assess
        rubric (str): The rubric to use for assessment
        client: OpenAI client instance
        
    Returns:
        dict: Dictionary of scores for each criterion
        
    Raises:
        ValueError: If rubric is empty or invalid
        Exception: For API errors or other issues
    """
    # Validate the rubric
    if not rubric or not rubric.strip():
        raise ValueError("Rubric cannot be empty. Please provide assessment criteria.")

    # Ensure rubric is formatted as a string
    if isinstance(rubric, list):
        rubric_str = "\n".join([f"- {item}" for item in rubric])
    else:
        rubric_str = str(rubric) # Assume it's already a string
    
    # Check if the rubric has at least one criterion
    rubric_lines = [line.strip() for line in rubric_str.split('\n') if line.strip()]
    if not rubric_lines:
        raise ValueError("Rubric must contain at least one criterion")

    # First pass: Deep analysis of the code
    analysis_system_prompt = """
You are an expert code analyzer with deep knowledge of software engineering principles, design patterns, and best practices.
Your task is to perform a thorough analysis of the provided code based EXACTLY on the rubric provided.

The rubric may be in a tabular format with specific mark ranges and criteria descriptions.
You must analyze the code according to the EXACT criteria in the rubric, not any predefined criteria.

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

IMPORTANT: The rubric may have specific mark ranges (e.g., 0, 1-3, 4-8, 10-12) and detailed descriptions for each level.
You MUST use the EXACT scoring system from the rubric, not a generic 1-5 scale.

For each criterion in the rubric:
1. Determine which mark range/category the code falls into based on the descriptions
2. Assign the appropriate mark or mark range
3. Provide a brief justification for your assessment

Your response should include:
1. The criterion name
2. The mark or mark range assigned (exactly as specified in the rubric)
3. A brief justification

Example format:
Criterion: [Name of criterion]
Mark: [Mark or mark range as specified in the rubric]
Justification: [Brief explanation]
"""

        scoring_user_prompt = f"""
Rubric to use for assessment:
{rubric_str}

Detailed code analysis:
{code_analysis}

Evaluate the code according to EACH criterion in the rubric, using the EXACT mark ranges and categories specified in the rubric.
Return the assessment with marks and justifications for each criterion.
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
        scores_dict = {}
        justifications = {}
        
        # Try to parse structured format first
        import re
        criterion_pattern = r'Criterion:\s*(.*?)\s*\n'
        mark_pattern = r'Mark:\s*(.*?)\s*\n'
        justification_pattern = r'Justification:\s*(.*?)(?:\n\n|\Z)'
        
        criteria_matches = re.findall(criterion_pattern, assessment_content, re.DOTALL)
        mark_matches = re.findall(mark_pattern, assessment_content, re.DOTALL)
        justification_matches = re.findall(justification_pattern, assessment_content, re.DOTALL)
        
        if criteria_matches and mark_matches and len(criteria_matches) == len(mark_matches):
            for i in range(len(criteria_matches)):
                criterion = criteria_matches[i].strip()
                mark = mark_matches[i].strip()
                
                # Store the exact mark or mark range from the rubric
                scores_dict[criterion] = mark
                
                # Store justification if available
                if i < len(justification_matches):
                    justifications[criterion] = justification_matches[i].strip()
        else:
            # Fallback to line-by-line parsing
            current_criterion = None
            current_mark = None
            current_justification = []
            
            for line in assessment_content.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this line starts a new criterion
                if line.lower().startswith('criterion:'):
                    # Save previous criterion if exists
                    if current_criterion and current_mark:
                        scores_dict[current_criterion] = current_mark
                        if current_justification:
                            justifications[current_criterion] = ' '.join(current_justification)
                    
                    # Start new criterion
                    current_criterion = line.split(':', 1)[1].strip()
                    current_mark = None
                    current_justification = []
                elif line.lower().startswith('mark:') and current_criterion:
                    current_mark = line.split(':', 1)[1].strip()
                elif line.lower().startswith('justification:') and current_criterion:
                    justification_text = line.split(':', 1)[1].strip()
                    current_justification = [justification_text]
                elif current_criterion and current_justification:
                    # Continuation of justification
                    current_justification.append(line)
            
            # Save the last criterion
            if current_criterion and current_mark:
                scores_dict[current_criterion] = current_mark
                if current_justification:
                    justifications[current_criterion] = ' '.join(current_justification)
        
        # If still no scores, try a more lenient parsing approach
        if not scores_dict:
            for line in assessment_content.strip().split('\n'):
                if ':' in line:
                    parts = line.split(':', 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    if key.lower() in ['criterion', 'criteria']:
                        current_criterion = value
                    elif key.lower() in ['mark', 'marks', 'score', 'grade'] and current_criterion:
                        scores_dict[current_criterion] = value
                    elif key.lower() in ['justification', 'reason', 'explanation'] and current_criterion:
                        justifications[current_criterion] = value

        # If still no scores, return an error
        if not scores_dict:
            raise ValueError("Could not parse assessment results into scores")

        # Add justifications to the return value
        result = {}
        for criterion, score in scores_dict.items():
            result[criterion] = {
                'mark': score,
                'justification': justifications.get(criterion, '')
            }

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
                scores = assess_code(code, rubric, client)
                
                # Add to results
                results.append({
                    'name': student_name,
                    'repo_url': repo_url,
                    'scores': scores
                })
                
                print(f"Assessment completed for {student_name}.")
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
