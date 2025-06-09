import os
import sys
import argparse
from agents.controller import ControllerAgent
from agents.aggregator import AggregatorAgent
from agents.publisher import PublisherAgent  # Optional, can be omitted if not needed
from csv_analyzer import process_csv

# Configuration - use direct parameters (not environment variables)
INPUT_FILE = "input_students.xlsx"
RESULTS_EXCEL = "results.xlsx"
BATCH_SIZE = 4
ANALYZER_SLOTS = 4
TIMEOUT = 120  # seconds per repo

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Grading System")
    parser.add_argument("--rubric", required=True, help="Path to rubric JSON file (provided by frontend)")
    args = parser.parse_args()

    RUBRIC_JSON = args.rubric

    print("=== Multi-Agent Grading System ===")
    print(f"Input File: {INPUT_FILE}")
    print(f"Rubric: {RUBRIC_JSON}")
    print(f"Results Excel: {RESULTS_EXCEL}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Analyzer slots: {ANALYZER_SLOTS}")

    # Load rubric
    if not os.path.exists(RUBRIC_JSON):
        print(f"Rubric file {RUBRIC_JSON} not found.")
        sys.exit(1)
    with open(RUBRIC_JSON, "r") as f:
        rubric = f.read()

    # Load students using real process_csv logic
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found.")
        sys.exit(1)
    class DummyFileStorage:
        def __init__(self, filename):
            self.filename = filename
        def read(self):
            with open(self.filename, "rb") as f:
                return f.read()
        def seek(self, pos):
            pass
    file_storage = DummyFileStorage(INPUT_FILE)
    students = process_csv(file_storage)
    if not students:
        print("No students found in input file.")
        sys.exit(1)

    # Initialize agents
    aggregator = AggregatorAgent(RESULTS_EXCEL)
    controller = ControllerAgent(
        students=students,
        rubric=rubric,
        batch_size=BATCH_SIZE,
        analyzer_slots=ANALYZER_SLOTS,
        aggregator=aggregator,
        timeout=TIMEOUT
    )

    # Optional: publisher agent
    publisher = None
    if os.getenv("ENABLE_PUBLISHER", "0") == "1":
        publisher = PublisherAgent(RESULTS_EXCEL)

    # Run the pipeline
    controller.run_batches()

    # Optionally publish results
    if publisher:
        publisher.publish()

    print("=== Grading complete. Results written to", RESULTS_EXCEL, "===")

if __name__ == "__main__":
    main()
