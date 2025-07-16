import requests

url = "http://127.0.0.1:5000/api/agentic/upload_csv"
files = {
    "file": open("backend/sample_students.csv", "rb"),
    "rubric": open("comprehensive_rubric.txt", "rb")
}

response = requests.post(url, files=files)
print("Status code:", response.status_code)
try:
    print("Response:", response.json())
except Exception:
    print("Raw response:", response.text)
