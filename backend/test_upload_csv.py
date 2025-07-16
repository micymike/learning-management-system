import requests

url = "http://localhost:5000/api/agentic/upload_csv"
csv_path = "backend/sample_students.csv"
rubric_path = "comprehensive_rubric.txt"

with open(csv_path, "rb") as csv_file, open(rubric_path, "rb") as rubric_file:
    files = {
        "file": (csv_path, csv_file, "text/csv"),
        "rubric": (rubric_path, rubric_file, "text/plain"),
    }
    response = requests.post(url, files=files)
    print("Status code:", response.status_code)
    print("Response:")
    print(response.text)
