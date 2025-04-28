# AI-Powered Student Repo Grader

A web-based application that automates the grading of coding assignments submitted by students via GitHub repositories. The tool uses a grading rubric provided by the instructor and analyzes student code submissions to output structured grading reports.

## Features

- **CSV Upload Interface**: Upload a CSV file with student names and GitHub repository URLs
- **Rubric Creation**: Define custom grading criteria with maximum scores and descriptions
- **Repository Analysis**: Automatically clone and analyze GitHub repositories
- **AI Grading Engine**: Evaluate code against defined rubric criteria
- **AI-Generated Code Estimation**: Estimate the percentage of AI-generated code
- **Report Generation**: Download comprehensive evaluation reports in CSV or Excel format

## Tech Stack

### Backend
- Python with FastAPI
- SQLite database
- GitPython for repository interaction
- Pandas for data processing and report generation

### Frontend
- React with Vite
- Framer Motion for animations
- CSS Variables for theming
- Fetch API for network requests

## Environment Variables

### Frontend (.env file)

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_URL | URL of the backend API | http://localhost:5000/api |

You can copy the `.env.example` file to create your own `.env` file:
```
cp frontend/.env.example frontend/.env
```

## Setup Instructions

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the backend server:
   ```
   python run.py
   ```
   The API will be available at http://localhost:5000/api

   > **Note:** The frontend is configured to connect to the backend at http://localhost:5000/api by default. If you need to change this, update the `VITE_API_URL` in the frontend's `.env` file.

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Create an environment file:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file to configure your environment variables.

3. Install dependencies:
   ```
   npm install
   ```

4. Run the development server:
   ```
   npm run dev
   ```
   The application will be available at http://localhost:5173

## Usage Guide

1. **Create an Assignment**:
   - Navigate to the Assignments page
   - Click "Create Assignment"
   - Fill in assignment details and create a rubric

2. **Add Student Submissions**:
   - Open an assignment
   - Add individual submissions or upload a CSV file with multiple submissions

3. **View Evaluations**:
   - Wait for the automatic grading to complete
   - Click on a submission to view detailed evaluation results

4. **Download Reports**:
   - Go to the Reports tab in an assignment
   - Download CSV or Excel reports with all evaluation results

## License

This project is licensed under the MIT License - see the LICENSE file for details.
