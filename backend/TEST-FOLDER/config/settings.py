import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
TEMP_DIR = DATA_DIR / "temp"

# Ensure directories exist
for directory in [DATA_DIR, INPUT_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Processing settings
BATCH_SIZE = 4
MAX_ANALYZER_TIMEOUT = 300  # 5 minutes
MAX_REPO_SIZE_MB = 100
MAX_CONCURRENT_ANALYZERS = 4

# File paths
INPUT_EXCEL = INPUT_DIR / "students.xlsx"
OUTPUT_EXCEL = OUTPUT_DIR / "results.xlsx"
RUBRIC_PATH = BASE_DIR / "config" / "rubric.json"

# GitHub settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional for private repos

# CrewAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CREWAI_LOG_LEVEL = "INFO"

# Column names in Excel
STUDENT_NAME_COL = "Name"
GITHUB_URL_COL = "GitHub URL"
GRADE_COL = "Grade (out of 12)"
FEEDBACK_COL = "Concise Analysis"