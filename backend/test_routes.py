import requests
import csv

BASE_URL = "http://127.0.0.1:8000"

def print_response(resp, route):
    print(f"{route} raw response:", resp.text)
    try:
        print(f"{route} JSON:", resp.json())
    except Exception as e:
        print(f"{route} JSON decode error: {e}")

# Helper to read students from csv
def get_students_from_csv(csv_path):
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]

# 1. Test /assess route for each student (requires explicit code/rubric input)
def test_assess_for_students():
    students = get_students_from_csv("sample_students.csv")
    for student in students:
        print(f"\nTesting /assess for {student['name']} (skipped: no code/rubric provided)...")
        # To avoid bias, do not use any sample code or rubric.
        # You can uncomment and provide your own test values below if needed.
        # data = {
        #     "code": "<INSERT CODE HERE>",
        #     "rubric": "<INSERT RUBRIC HERE>"
        # }
        # resp = requests.post(f"{BASE_URL}/assess", data=data)
        # print_response(resp, f"/assess for {student['name']}")

# 2. Test /upload_csv route (all students at once)
def test_upload_csv():
    with open("sample_students.csv", "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{BASE_URL}/upload_csv", files=files)
        print_response(resp, "/upload_csv")

# 3. Test /upload_rubric route
def test_upload_rubric():
    with open("sample_rubric.txt", "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{BASE_URL}/upload_rubric", files=files)
        print_response(resp, "/upload_rubric")

# 4. Test /upload_github_url for each student
def test_upload_github_url_for_students():
    students = get_students_from_csv("sample_students.csv")
    for student in students:
        print(f"\nTesting /upload_github_url for {student['name']}...")
        data = {"url": student['repo_url']}
        resp = requests.post(f"{BASE_URL}/upload_github_url", data=data)
        print_response(resp, f"/upload_github_url for {student['name']}")

if __name__ == "__main__":
    test_assess_for_students()
    print("\nTesting /upload_csv...")
    test_upload_csv()
    print("\nTesting /upload_rubric...")
    test_upload_rubric()
    test_upload_github_url_for_students()
