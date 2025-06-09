from mongoengine import connect
from backend.models import Assessment
import os

def fix_rubric_field():
    # Connect to MongoDB using environment variables or defaults
    mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/learning-management-system")
    connect(host=mongo_uri)

    updated = 0
    for assessment in Assessment.objects():
        rubric = assessment.rubric
        # If rubric is a list with a single dict, convert to just the dict
        if isinstance(rubric, list) and len(rubric) == 1 and isinstance(rubric[0], dict):
            print(f"Fixing assessment {assessment.id} ({assessment.name})")
            assessment.rubric = rubric[0]
            assessment.save()
            updated += 1
    print(f"Updated {updated} assessment(s).")

if __name__ == "__main__":
    fix_rubric_field()
