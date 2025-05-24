#!/bin/bash

# Script to train the RAG model from CSV data

# Check if the CSV file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <csv_file>"
    echo "Example: $0 training_scripts.csv"
    exit 1
fi

CSV_FILE=$1

# Check if the file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "Error: File $CSV_FILE not found"
    exit 1
fi

# Navigate to the backend directory
cd backend

# Activate virtual environment if it exists
if [ -d "../.venv" ]; then
    echo "Activating virtual environment..."
    source ../.venv/bin/activate
fi

# Run the training script
echo "Training RAG model from $CSV_FILE..."
python train_from_csv.py "../$CSV_FILE"

# Check if training was successful
if [ $? -eq 0 ]; then
    echo "Training completed successfully!"
else
    echo "Training failed. Check the error messages above."
    exit 1
fi

echo "The RAG model is now ready to use for assessments."
echo "You can use it by setting USE_RAG=true in your .env file or by using the /api/assess endpoint with use_rag=true."