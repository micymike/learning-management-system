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

    # Ensure rubric is formatted as a string list if it's not already
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
Your task is to perform a thorough analysis of the provided code, focusing on:

1. Code structure and organization
2. Algorithm efficiency and complexity
3. Error handling and edge cases
4. Adherence to language-specific conventions and best practices
5. Maintainability and readability
6. Security considerations
7. Performance implications
8. Potential bugs or issues

Provide a detailed analysis that will be used as input for a subsequent scoring process.
"""

    analysis_user_prompt = f"""
Analyze the following code in depth, considering the rubric criteria that will be used for assessment:

Rubric criteria:
{rubric_str}

Code to analyze:
{code}

Provide a detailed analysis of the code's strengths and weaknesses relative to each criterion.
"""

    try:
        # First pass: Get detailed analysis
        analysis_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",  # Cheaper while still capable
            messages=[
                {"role": "system", "content": analysis_system_prompt},
                {"role": "user", "content": analysis_user_prompt}
            ],
            temperature=0.3
        )
        code_analysis = analysis_response.choices[0].message.content

        # Second pass: Score based on the analysis
        scoring_system_prompt = """
You are a strict code assessor. Your task is to evaluate code based STRICTLY on the given rubric criteria and a detailed code analysis.
Each criterion must be rated from 1 (Poor) to 5 (Excellent).

Your response must follow this exact format for each criterion:
criterion_name,score,brief_justification

Example:
Code compiles and runs without errors,4,The code compiles cleanly with only minor warnings about unused variables
Code follows best practices,3,Some functions are too long and variable naming is inconsistent
Functionality matches requirements,5,All specified features are implemented correctly
Code is efficient and readable,4,Good use of comments but some algorithms could be optimized
Proper use of version control,3,Commit messages are descriptive but some large commits contain unrelated changes

Rules:
1. Score must be between 1-5 (integer only)
2. Provide a brief justification (1-2 sentences) for each score
3. Base scores on the provided code analysis
4. Each criterion must get a score
5. Be consistent and fair in your scoring
"""

        scoring_user_prompt = f"""
Rubric criteria to score (1-5):
{rubric_str}

Detailed code analysis:
{code_analysis}

Return the scores with brief justifications for each criterion.
"""

        scoring_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",  # Cost-effective scoring
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
        
        for line in assessment_content.strip().split('\n'):
            if ',' in line:
                parts = line.split(',', 2)
                if len(parts) >= 2:
                    criterion = parts[0].strip()
                    try:
                        score = int(parts[1].strip())
                        scores_dict[criterion] = score
                        
                        # Store justification if available
                        if len(parts) > 2:
                            justifications[criterion] = parts[2].strip()
                    except ValueError:
                        # If score is not an integer, skip this line
                        continue

        # If no scores were parsed, try a more lenient parsing approach
        if not scores_dict:
            for line in assessment_content.strip().split('\n'):
                if ':' in line:
                    criterion, rest = line.split(':', 1)
                    # Try to extract a number from the rest of the line
                    import re
                    score_match = re.search(r'\b[1-5]\b', rest)
                    if score_match:
                        scores_dict[criterion.strip()] = int(score_match.group())

        # If still no scores, return an error
        if not scores_dict:
            raise ValueError("Could not parse assessment results into scores")

        return scores_dict
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
