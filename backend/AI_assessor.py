"""
This file is responsible for assessing code based on a structured rubric with multiple criteria and scoring levels.
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

def format_criterion_for_prompt(criterion):
    """Format a single criterion with its levels for the prompt"""
    # If max_points is None, use a default value but preserve the original None
    max_points = criterion['max_points'] if criterion['max_points'] is not None else 40
    
    result = f"{criterion['criterion']} [Maximum {max_points} points]\n"
    if 'levels' in criterion:
        for level in criterion['levels']:
            result += f"- Level ({level['min_points']}-{level['max_points']}): {level['description']}\n"
    return result

def assess_code(code, rubric, client):
    """
    Assesses code using structured rubric criteria with defined scoring levels.
    
    Args:
        code (str): The code to assess
        rubric (list): List of criteria dictionaries with points and levels
        client: OpenAI client instance
    """
    print("Assessing code with rubric:")
    print(json.dumps(rubric, indent=2))

    # Format rubric for prompt
    rubric_prompt = "Assessment Criteria:\n\n"
    total_max_points = 0
    
    for criterion in rubric:
        rubric_prompt += format_criterion_for_prompt(criterion) + "\n"
        total_max_points += criterion['max_points']
    
    analysis_system_prompt = f"""You are an expert code assessor. Analyze the code according to these criteria:

{rubric_prompt}

For each criterion:
1. Analyze the code thoroughly
2. Consider all aspects of the criterion and its scoring levels
3. Provide specific examples from the code to support your analysis

Your analysis will be used to assign scores in the next step."""

    analysis_user_prompt = f"""Analyze this code based on the criteria:

{code}

Provide detailed analysis for each criterion, citing specific code examples."""

    try:
        # First pass: Detailed analysis
        print("Getting detailed analysis...")
        analysis_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": analysis_system_prompt},
                {"role": "user", "content": analysis_user_prompt}
            ],
            temperature=0.3
        )
        
        code_analysis = analysis_response.choices[0].message.content
        print("\nCode Analysis:")
        print(code_analysis)

        # Second pass: Score based on analysis and rubric levels
        scoring_system_prompt = f"""You are a code assessor. Score the code based on this rubric:

{rubric_prompt}

Rules:
1. Assign points within the defined ranges for each criterion
2. Support each score with specific examples from the analysis
3. Ensure scores match the level descriptions

Format your response exactly like this for each criterion:

CRITERION: [Name]
SCORE: [X] out of [Y] points
LEVEL: [Description of matched level]
JUSTIFICATION: [Specific examples and reasoning]
"""

        scoring_user_prompt = f"""Score this code analysis according to the rubric:

Analysis:
{code_analysis}

Provide detailed scoring for each criterion."""

        print("\nGetting scores...")
        scoring_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": scoring_system_prompt},
                {"role": "user", "content": scoring_user_prompt}
            ],
            temperature=0.2
        )

        assessment_text = scoring_response.choices[0].message.content
        print("\nScoring Response:")
        print(assessment_text)

        # Parse the scoring response
        result = {
            'criteria_scores': {},
            'total_points': 0,
            'max_points': total_max_points,
            'percentage': 0,
            'passing': False
        }

        # Extract scores and justifications
        current_criterion = None
        current_score = None
        current_justification = []
        
        for line in assessment_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('CRITERION:'):
                # Save previous criterion if exists
                if current_criterion and current_score is not None:
                    result['criteria_scores'][current_criterion] = {
                        'points': current_score['points'],
                        'max_points': current_score['max'],
                        'justification': ' '.join(current_justification)
                    }
                    result['total_points'] += current_score['points']
                
                # Start new criterion
                current_criterion = line.split(':', 1)[1].strip()
                current_score = None
                current_justification = []
            
            elif line.startswith('SCORE:'):
                score_text = line.split(':', 1)[1].strip()
                points = float(score_text.split()[0])
                max_points = float(score_text.split()[-2])
                current_score = {'points': points, 'max': max_points}
            
            elif line.startswith('JUSTIFICATION:'):
                current_justification = [line.split(':', 1)[1].strip()]
            
            elif current_justification:  # Continue previous justification
                current_justification.append(line)

        # Add final criterion
        if current_criterion and current_score is not None:
            result['criteria_scores'][current_criterion] = {
                'points': current_score['points'],
                'max_points': current_score['max'],
                'justification': ' '.join(current_justification)
            }
            result['total_points'] += current_score['points']

        # Calculate final percentage and passing status
        result['percentage'] = calculate_percentage(result['total_points'], result['max_points'])
        result['passing'] = is_passing_grade(result['percentage'])
        
        print("\nFinal Assessment:")
        print(json.dumps(result, indent=2))
        return result

    except Exception as e:
        print(f"Error in assessment: {str(e)}")
        raise Exception(f"Assessment failed: {str(e)}")

def read_sample_csv(file_path):
    """Read student information from CSV"""
    if not file_path:
        raise ValueError("CSV file path must be provided")
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

if __name__ == "__main__":
    main()
