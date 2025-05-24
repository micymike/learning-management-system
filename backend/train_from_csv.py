#!/usr/bin/env python3
"""
Main script to download training data from CSV and train the RAG system
"""
import os
from dotenv import load_dotenv

# Import the necessary modules
# Import only csv_downloader here to avoid circular imports
from csv_downloader import process_training_csv

def main(csv_path=None):
    """
    Train the RAG system from a CSV file
    
    Args:
        csv_path: Path to the CSV file. If None, uses default path
    """
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not set in .env file")
    
    # Use default path if none provided
    if csv_path is None:
        csv_path = '../training_scripts.csv'
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at {csv_path}")
    
    print(f"Processing training data from {csv_path}...")
    
    # Create output directory for downloads
    output_dir = os.path.join('downloads')
    os.makedirs(output_dir, exist_ok=True)
    
    # Download all files from the CSV
    files = process_training_csv(csv_path, output_dir)
    
    if not files:
        raise ValueError("No files were downloaded. Check the CSV format and URLs.")
    
    print(f"Downloaded {len(files)} files. Processing...")
    
    # Import these here to avoid circular imports
    from process_training_data import extract_rubric_criteria, extract_code_examples
    from rag_trainer import RAGTrainer
    
    # Initialize the RAG trainer
    trainer = RAGTrainer()
    
    # Process rubrics
    rubrics = {}
    for file in files:
        if file['type'] == 'rubric':
            rubric_text = extract_rubric_criteria(file['filepath'])
            rubric_id = file['label']
            rubrics[rubric_id] = rubric_text
            
            # Add to ChromaDB
            trainer.add_rubric(rubric_text, rubric_id)
            print(f"Added rubric {rubric_id} to ChromaDB")
    
    # Process outputs and match with rubrics
    for file in files:
        if file['type'] == 'output':
            examples = extract_code_examples(file['filepath'])
            
            # Try to match with a rubric
            rubric_id = None
            for r_id in rubrics.keys():
                if r_id in file['label']:
                    rubric_id = r_id
                    break
            
            # If no specific rubric found, use the first one
            if not rubric_id and rubrics:
                rubric_id = list(rubrics.keys())[0]
            
            # Get the rubric text
            rubric_text = rubrics.get(rubric_id, "")
            
            # Add examples to ChromaDB
            for i, example in enumerate(examples):
                if example['code'] and example['scores']:
                    trainer.add_assessment_example(
                        example['code'],
                        rubric_text,
                        example['scores'],
                        f"{file['label']}_{i}"
                    )
                    print(f"Added example {i+1} from {file['label']} to ChromaDB")
    
    print(f"Training complete! Processed {len(files)} files from {csv_path}")
    print(f"Added {len(rubrics)} rubrics and {sum(1 for f in files if f['type'] == 'output')} output files to the RAG system")
    
    return {
        'rubrics': len(rubrics),
        'outputs': sum(1 for f in files if f['type'] == 'output'),
        'total_files': len(files)
    }

if __name__ == "__main__":
    import sys
    csv_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(csv_path)
