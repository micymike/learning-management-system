# Learning Management System with RAG-based Assessment

This system uses Retrieval-Augmented Generation (RAG) to assess student code submissions based on rubrics.

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\\Scripts\\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r backend/requirements.txt`
5. Copy `.env.example` to `.env` and fill in your API keys and configuration
6. Set up Pinecone:
   - Create a Pinecone account at https://www.pinecone.io/
   - Create an index named "code-assessment" with dimension 1536 and metric "cosine"
   - Add your Pinecone API key and environment to `.env`
7. Set up Google Drive API (for bulk training):
   - Create a project in Google Cloud Console
   - Enable the Google Drive API
   - Create a service account and download the credentials JSON file
   - Share your Google Drive folders with the service account email
   - Add the path to the credentials file in `.env`

## Training the RAG System

### Option 1: Using the Training Script

The easiest way to train the RAG system is using the provided script:

```bash
./train.sh training_scripts.csv
```

This will:
1. Process the CSV file containing links to rubrics and example assessments
2. Download the content and extract training data
3. Add the rubrics and examples to the vector database

### Option 2: Bulk Training from Google Drive

1. Organize your rubrics and examples in Google Drive folders
2. Add the folder IDs to `.env`
3. Run the training script: `python backend/rag_trainer.py`

### Option 3: Manual Training via API

Send a POST request to `/rag/train/manual` with JSON data:

```json
{
  "rubric": "Your rubric text here...",
  "rubric_id": "optional_rubric_id",
  "example": {
    "code": "Your example code here...",
    "scores": {
      "Criterion 1": {
        "mark": "10/12",
        "justification": "Explanation for the score"
      },
      "Criterion 2": {
        "mark": "8/12",
        "justification": "Explanation for the score"
      }
    },
    "id": "optional_example_id"
  }
}
```

## Using the Assessment System

### Traditional vs RAG-based Assessment

The system supports both traditional LLM-based assessment and RAG-based assessment:

1. **Traditional Assessment**: Uses OpenAI's GPT models directly with the rubric
2. **RAG-based Assessment**: Enhances the assessment by retrieving similar examples and rubrics

You can choose which method to use:

- Set `USE_RAG=true` in your `.env` file to use RAG-based assessment by default
- Use the `/api/assess` endpoint with `use_rag: true` in your JSON payload
- Use the `/api/compare-assessment` endpoint to get results from both methods

### API Endpoints

#### Assess Code

```
POST /api/assess
```

Request body:
```json
{
  "code": "Your code to assess",
  "rubric": "Your rubric text",
  "use_rag": true
}
```

#### Compare Assessment Methods

```
POST /api/compare-assessment
```

Request body:
```json
{
  "code": "Your code to assess",
  "rubric": "Your rubric text"
}
```

#### RAG-specific Endpoints

```
POST /rag/assess
```
- Supports both JSON and form data
- Can process individual code or GitHub repositories

```
POST /rag/assess/excel
```
- Returns an Excel file with formatted assessment results

## File Structure

- `backend/AI_assessor.py`: Traditional assessment system
- `backend/rag_assessor.py`: RAG-based assessment system
- `backend/rag_trainer.py`: Script for training the RAG system
- `backend/train_from_csv.py`: Script for training from CSV data
- `backend/routes/api_routes.py`: Combined API routes
- `backend/routes/rag_routes.py`: RAG-specific API routes
- `train.sh`: Shell script for easy training

## Troubleshooting

If you encounter issues with the RAG system:

1. Check that your vector database (Pinecone or ChromaDB) is properly set up
2. Ensure you have trained the system with relevant examples
3. Verify your OpenAI API key is valid and has sufficient credits
4. If RAG assessment fails, the system will fall back to traditional assessment