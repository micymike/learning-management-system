"""
This file is responsible for assessing code based on raw rubric content without modifications.
The AI assessor uses the exact rubric content as provided without creating its own criteria.
"""

import os
import json
import requests
import re
import pandas as pd
from repo_analyzer import analyze_repo
from csv_analyzer import process_csv, score_manager
from rubric_handler import (
    get_custom_rubric, 
    format_rubric_for_ai_assessment,
    calculate_percentage, 
    is_passing_grade
)
from openai import AzureOpenAI
import dotenv

dotenv.load_dotenv()

# Azure OpenAI configuration (match test script)
endpoint = os.getenv("ENDPOINT_URL", "https://kidus-mafuwv4a-eastus2.cognitiveservices.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4.1")
subscription_key = os.getenv("AZURE_OPENAI_KEY", "8ZlW0fgGBZH3YfSEUJrTvgxMNuHBZ1ANPXl12MHGzURPjHnrsKWFJQQJ99BEACHYHv6XJ3w3AAAAACOGJyfI")
api_version = "2025-01-01-preview"

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version=api_version,
)

def assess_code_with_raw_rubric(code, client=None):
    """
    Assesses code using the exact raw rubric content without any modifications.
    The AI must work with whatever rubric format is provided - no assumptions, no defaults.

    Args:
        code (str): The code to assess
        client: OpenAI client instance (optional)

    Returns:
        dict: Assessment results with scores exactly as determined by the AI based on raw rubric

    Raises:
        ValueError: If no rubric is loaded or if assessment fails
    """
    if client is None:
        client = globals().get("client")
    print("Starting code assessment with raw rubric...")

    # Get the raw rubric content - this will throw an error if no rubric is loaded
    try:
        raw_rubric = get_custom_rubric()
    except ValueError as e:
        raise ValueError(f"Cannot assess code: {str(e)}")

    # Format the raw rubric for AI consumption without any modifications
    formatted_rubric = format_rubric_for_ai_assessment(raw_rubric)

    print("Using raw rubric content for assessment:")
    print("=" * 50)
    print(formatted_rubric)
    print("=" * 50)

    # Create the system prompt that instructs AI to use ONLY the provided rubric
    analysis_system_prompt = f"""You are an expert code assessor. You must assess the provided code using ONLY the rubric content provided below.

CRITICAL INSTRUCTIONS:
1. Use ONLY the rubric content provided - do not create your own criteria.
2. Do not modify, interpret, or assume anything about the rubric structure.
3. Extract the scoring criteria, points, and levels exactly as they appear in the rubric.
4. If the rubric format is unclear, work with what is provided - do not default to standard criteria.
5. Your assessment must be based entirely on the rubric content below.

SCORING FORMAT REQUIREMENTS:
- For each criterion, output the score as a single numeric value chosen from the allowed range in the rubric (e.g., if the rubric says 1-3, output 1, 2, or 3).
- Display the score for each criterion in the format: Criterion Name: x/total max (where x is the awarded mark and total max is the maximum for that criterion as specified in the rubric).
- Do NOT output a range or a label; always output a single numeric score for each criterion.
- After the score, provide a brief justification and relevant code examples.

RUBRIC CONTENT:
{formatted_rubric}

Your task:
1. Carefully analyze the rubric to understand the exact criteria and scoring structure.
2. Assess the code against these specific rubric criteria.
3. For each criterion, output the score as described above.
4. Cite specific examples from the code to justify your scores.
5. Follow any specific instructions or formats mentioned in the rubric.

The rubric above is the ONLY source of assessment criteria you should use."""

    analysis_user_prompt = f"""Assess this code using ONLY the rubric provided in the system prompt:

CODE TO ASSESS:
{code}

Instructions:
1. First, analyze the rubric structure to understand the criteria and scoring system
2. Then assess the code against each criterion as defined in the rubric
3. Provide specific scores as defined in the rubric (not standard scores)
4. Support each score with specific code examples
5. Follow the exact format and requirements specified in the rubric

Provide your assessment following the rubric's own structure and requirements."""

    try:
        print("Sending code and rubric to AI for assessment...")

        # Single comprehensive assessment using the raw rubric
        assessment_response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": analysis_system_prompt},
                {"role": "user", "content": analysis_user_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent scoring
            max_tokens=4000   # Ensure enough space for detailed assessment
        )

        assessment_text = assessment_response.choices[0].message.content
        print("\nRaw AI Assessment Response:")
        print("=" * 50)
        print(assessment_text)
        print("=" * 50)

        # Parse the assessment response to extract structured results
        # This parsing is flexible and doesn't assume any specific format
        result = parse_flexible_assessment_response(assessment_text, raw_rubric)

        print("\nStructured Assessment Result:")
        print(json.dumps(result, indent=2, default=str))

        return result

    except Exception as e:
        print(f"Error in assessment: {str(e)}")
        raise Exception(f"Code assessment failed: {str(e)}. Ensure the rubric is properly formatted and try again.")

def parse_flexible_assessment_response(assessment_text, raw_rubric):
    """
    Parse the AI assessment response flexibly without assuming specific format.
    Extracts whatever scoring information the AI provided based on the raw rubric.
    """
    print("\nParsing flexible assessment response...")

    # Initialize result structure
    result = {
        'raw_assessment': assessment_text,
        'rubric_type': raw_rubric['type'],
        'extracted_scores': {},
        'total_assessment': None,
        'summary': None
    }

    # Try to extract any numerical scores mentioned in the response
    score_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(\d+(?:\.\d+)?)',  # "X out of Y" or "X/Y"
        r'(\d+(?:\.\d+)?)\s*points?\s*(?:out of|/)\s*(\d+(?:\.\d+)?)',  # "X points out of Y"
        r'Score:\s*(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(\d+(?:\.\d+)?)',  # "Score: X out of Y"
        r'(\d+(?:\.\d+)?)%',  # "X%"
    ]

    extracted_scores = []
    lines = assessment_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try each score pattern
        for pattern in score_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    # Score out of max
                    score = float(match[0])
                    max_score = float(match[1])
                    extracted_scores.append({
                        'score': score,
                        'max_score': max_score,
                        'context': line,
                        'percentage': (score / max_score * 100) if max_score > 0 else 0
                    })
                elif isinstance(match, str):
                    # Percentage
                    percentage = float(match)
                    extracted_scores.append({
                        'percentage': percentage,
                        'context': line
                    })

    result['extracted_scores'] = extracted_scores

    # Try to find overall/total scores
    total_patterns = [
        r'(?:total|overall|final)\s*(?:score|points?):\s*(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(\d+(?:\.\d+)?)',
        r'(?:total|overall|final):\s*(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(\d+(?:\.\d+)?)',
    ]

    for line in lines:
        for pattern in total_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                total_score = float(match.group(1))
                max_total = float(match.group(2))
                result['total_assessment'] = {
                    'total_points': total_score,
                    'max_points': max_total,
                    'percentage': (total_score / max_total * 100) if max_total > 0 else 0,
                    'context': line
                }
                break

    # Extract any summary or conclusion
    summary_keywords = ['summary', 'conclusion', 'overall', 'final assessment', 'verdict']
    for i, line in enumerate(lines):
        for keyword in summary_keywords:
            if keyword.lower() in line.lower():
                # Take this line and the next few lines as summary
                summary_lines = lines[i:i+3]
                result['summary'] = '\n'.join(summary_lines).strip()
                break

    print(f"Extracted {len(extracted_scores)} score entries from assessment")
    if result['total_assessment']:
        print(f"Found total assessment: {result['total_assessment']}")

    return result

def get_assessment_summary(assessment_result):
    """
    Generate a summary of the assessment results without modifying scores.
    """
    if not assessment_result:
        return "No assessment results available"

    summary = ["ASSESSMENT SUMMARY", "=" * 50]

    # Add raw assessment
    summary.append(f"Assessment Type: {assessment_result.get('rubric_type', 'Unknown')}")

    # Add extracted scores
    if assessment_result.get('extracted_scores'):
        summary.append(f"\nExtracted Scores ({len(assessment_result['extracted_scores'])} found):")
        for i, score_info in enumerate(assessment_result['extracted_scores'], 1):
            if 'score' in score_info and 'max_score' in score_info:
                summary.append(f"  {i}. {score_info['score']}/{score_info['max_score']} ({score_info['percentage']:.1f}%)")
            elif 'percentage' in score_info:
                summary.append(f"  {i}. {score_info['percentage']:.1f}%")
            summary.append(f"     Context: {score_info['context']}")

    # Add total if available
    if assessment_result.get('total_assessment'):
        total = assessment_result['total_assessment']
        summary.append(f"\nTotal Score: {total['total_points']}/{total['max_points']} ({total['percentage']:.1f}%)")

    # Add summary if available
    if assessment_result.get('summary'):
        summary.append(f"\nSummary: {assessment_result['summary']}")

    return '\n'.join(summary)

def read_sample_csv(file_path):
    """Read student information from CSV"""
    if not file_path:
        raise ValueError("CSV file path must be provided")
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        raise ValueError(f"Failed to read CSV file: {e}")

def assess_code(code, rubric_items=None, client=None):
    """
    Wrapper for backward compatibility. Sets the custom rubric if rubric_items is provided,
    then calls assess_code_with_raw_rubric.
    """
    if rubric_items is not None:
        from rubric_handler import set_custom_rubric
        set_custom_rubric(rubric_items)
    return assess_code_with_raw_rubric(code, client=client)

if __name__ == "__main__":
    # Example usage
    try:
        # This would fail if no rubric is loaded
        result = assess_code_with_raw_rubric("print('Hello World')")
        print(get_assessment_summary(result))
    except ValueError as e:
        print(f"Assessment error: {e}")
        print("Please load a rubric file first using upload_rubric_file()")
