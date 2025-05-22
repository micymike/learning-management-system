# RAG-based Assessment System

This directory contains scripts for the RAG (Retrieval-Augmented Generation) based assessment system.

## Scripts

- `rag_assessor.py`: The main RAG assessment system
- `rag_trainer.py`: Handles training the RAG system with rubrics and examples
- `csv_downloader.py`: Downloads rubrics and examples from Google Sheets
- `process_training_data.py`: Processes downloaded files for RAG training
- `train_from_csv.py`: Main script to train the system from a CSV file of URLs

## Training the System

1. Create a CSV file with rubric and output URLs (see `training_scripts.csv` in the root directory)
2. Run the training script:

```bash
cd backend
python train_from_csv.py
```

Or specify a custom CSV path:

```bash
python train_from_csv.py /path/to/your/csv_file.csv
```

## Environment Variables

Make sure these are set in your `.env` file:

```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENV=your_pinecone_environment
```

## CSV Format

The CSV should have two columns:
1. Label (e.g., "rubric1", "output1")
2. Google Sheets URL

Example:
```
rubric1, https://docs.google.com/spreadsheets/d/...
output1, https://docs.google.com/spreadsheets/d/...
```

The system will automatically match outputs with rubrics based on their labels.