"""
Script to process downloaded training data and prepare it for RAG training
"""
import os
import json
import pandas as pd
from csv_downloader import process_training_csv

def extract_code_examples(filepath):
    """Extract code examples from output files"""
    try:
        df = pd.read_csv(filepath)
        examples = []
        
        # Check if this is a structured output file
        if 'code' in df.columns and 'assessment' in df.columns:
            for _, row in df.iterrows():
                code = row['code']
                assessment = row['assessment']
                
                # Try to parse assessment as JSON
                try:
                    scores = json.loads(assessment)
                except:
                    # If not JSON, try to parse as string with format "criterion: score"
                    scores = {}
                    for line in assessment.split('\n'):
                        if ':' in line:
                            parts = line.split(':', 1)
                            criterion = parts[0].strip()
                            score = parts[1].strip()
                            scores[criterion] = {
                                "mark": score,
                                "justification": ""
                            }
                
                examples.append({
                    'code': code,
                    'scores': scores
                })
        
        # Alternative format: code in one column, scores in separate columns
        elif 'code' in df.columns:
            score_columns = [col for col in df.columns if col != 'code']
            
            for _, row in df.iterrows():
                code = row['code']
                scores = {}
                
                for col in score_columns:
                    if not pd.isna(row[col]):
                        scores[col] = {
                            "mark": str(row[col]),
                            "justification": ""
                        }
                
                examples.append({
                    'code': code,
                    'scores': scores
                })
        
        return examples
    except Exception as e:
        print(f"Error extracting examples from {filepath}: {e}")
        return []

def extract_rubric_criteria(filepath):
    """Extract rubric criteria from rubric files"""
    try:
        df = pd.read_csv(filepath)
        
        # Check if this is a structured rubric file
        if 'criterion' in df.columns and 'description' in df.columns:
            criteria = []
            for _, row in df.iterrows():
                criterion = row['criterion']
                description = row['description']
                
                # Check if there are mark ranges
                mark_ranges = []
                for col in df.columns:
                    if 'mark' in col.lower() and not pd.isna(row[col]):
                        mark_ranges.append(f"{col}: {row[col]}")
                
                criteria.append(f"{criterion}: {description}")
                for mark_range in mark_ranges:
                    criteria.append(f"  {mark_range}")
            
            return "\n".join(criteria)
        
        # Simple format: just take the first column
        else:
            return "\n".join(df.iloc[:, 0].dropna().astype(str).tolist())
    except Exception as e:
        print(f"Error extracting rubric from {filepath}: {e}")
        return ""