import json
from repo_analyzer import analyze_repo
from AI_assessor import assess_code
from rubric_handler import get_custom_rubric, set_custom_rubric

class AnalyzerAgent:
    def __init__(self, student, rubric):
        self.student = student
        self.rubric = json.loads(rubric) if isinstance(rubric, str) else rubric
        self.repo_url = student.get("GitHub URL") or student.get("repo_url")
        self.name = student.get("Name") or student.get("name")

    def analyze(self):
        result = {
            "name": self.name,
            "grade": 0,
            "feedback": [],
            "rubric_breakdown": {},
            "repo_access": False
        }
        if not self.repo_url or not self.repo_url.startswith("http"):
            result["feedback"].append("Invalid or missing GitHub URL.")
            return result

        # Use real repo analyzer to fetch code
        code = analyze_repo(self.repo_url)
        if not code or "error" in str(code).lower() or "not found" in str(code).lower():
            result["feedback"].append(f"Repo could not be analyzed: {code}")
            return result
        result["repo_access"] = True

        # Set rubric for assessment
        set_custom_rubric(self.rubric)
        # Use real AI assessor to grade code
        try:
            assessment = assess_code(code)
            # Extract grade and feedback from assessment
            extracted_scores = assessment.get("extracted_scores", [])
            total = assessment.get("total_assessment", {})
            summary = assessment.get("summary", "")
            result["rubric_breakdown"] = extracted_scores
            if total and "total_points" in total:
                result["grade"] = total["total_points"]
            elif extracted_scores:
                result["grade"] = sum(s.get("score", 0) for s in extracted_scores if "score" in s)
            else:
                result["grade"] = 0
            # Feedback: combine summary and extracted score contexts
            feedback = []
            if summary:
                feedback.append(summary)
            for s in extracted_scores:
                if "context" in s:
                    feedback.append(s["context"])
            result["feedback"] = feedback if feedback else ["Assessment complete."]
        except Exception as e:
            result["feedback"].append(f"Error during AI assessment: {str(e)}")
        return result
