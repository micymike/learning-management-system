import csv
import requests

API_URL = "http://127.0.0.1:5000/api/agentic/process"
CSV_PATH = "backend/sample_students.csv"

def main():
    # Read the rubric from comprehensive_rubric.txt
    with open("comprehensive_rubric.txt", "r", encoding="utf-8") as rubric_file:
        rubric = rubric_file.read()

    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            repo = row['repo_url']
            # Construct the prompt to include the rubric and analysis instruction
            prompt = (
                f"Rubric for code assessment:\n{rubric}\n\n"
                f"Analyze the repository for student {name} ({repo}) according to the rubric above. "
                "Provide a detailed assessment for each criterion."
            )
            payload = {
                "repo": repo,
                "prompt": prompt
            }
            try:
                response = requests.post(API_URL, json=payload)
                print(f"Student: {name}")
                print(f"Repo: {repo}")
                print("Response:", response.json())
                print("-" * 40)
            except Exception as e:
                print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    main()
