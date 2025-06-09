import json
from pathlib import Path
from typing import Dict, List, Tuple
from config.settings import RUBRIC_PATH

class GradingTools:
    def __init__(self):
        self.rubric = self._load_rubric()
    
    def _load_rubric(self) -> Dict:
        """Load grading rubric from JSON file."""
        try:
            with open(RUBRIC_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading rubric: {e}")
            return self._get_default_rubric()
    
    def _get_default_rubric(self) -> Dict:
        """Return default rubric if file cannot be loaded."""
        return {
            "total_points": 12,
            "categories": {
                "correctness": {"max_points": 4, "description": "Code correctness"},
                "organization": {"max_points": 3, "description": "Code organization"},
                "documentation": {"max_points": 2, "description": "Documentation quality"},
                "testing": {"max_points": 2, "description": "Testing and error handling"},
                "efficiency": {"max_points": 1, "description": "Code efficiency"}
            }
        }
    
    def analyze_code_quality(self, repo_analysis: Dict) -> Dict:
        """Analyze code quality based on repository analysis."""
        if "error" in repo_analysis:
            return {
                "correctness": 0,
                "organization": 0,
                "documentation": 0,
                "testing": 0,
                "efficiency": 0,
                "total_grade": 0,
                "feedback": [f"Repository analysis failed: {repo_analysis['error']}"]
            }
        
        scores = {}
        feedback = []
        
        # Analyze each category
        scores["correctness"] = self._analyze_correctness(repo_analysis, feedback)
        scores["organization"] = self._analyze_organization(repo_analysis, feedback)
        scores["documentation"] = self._analyze_documentation(repo_analysis, feedback)
        scores["testing"] = self._analyze_testing(repo_analysis, feedback)
        scores["efficiency"] = self._analyze_efficiency(repo_analysis, feedback)
        
        # Calculate total grade
        total_grade = sum(scores.values())
        
        return {
            **scores,
            "total_grade": total_grade,
            "feedback": feedback
        }
    
    def _analyze_correctness(self, analysis: Dict, feedback: List[str]) -> int:
        """Analyze code correctness (0-4 points)."""
        max_points = self.rubric["categories"]["correctness"]["max_points"]
        score = 0
        
        # Basic checks
        if analysis.get("python_files"):
            score += 1
            feedback.append("✓ Python files found")
        else:
            feedback.append("✗ No Python files detected")
            return 0
        
        # Check for reasonable file structure
        if len(analysis.get("python_files", [])) > 0:
            score += 1
            if len(analysis.get("python_files", [])) > 1:
                score += 1
                feedback.append("✓ Multiple Python files suggest good modularity")
            else:
                feedback.append("~ Single Python file - consider breaking into modules")
        
        # Check for basic project completeness
        if analysis.get("total_files", 0) > 2:
            score += 1
            feedback.append("✓ Project has multiple files")
        else:
            feedback.append("~ Very few files - project may be incomplete")
        
        return min(score, max_points)
    
    def _analyze_organization(self, analysis: Dict, feedback: List[str]) -> int:
        """Analyze code organization (0-3 points)."""
        max_points = self.rubric["categories"]["organization"]["max_points"]
        score = 0
        
        # Check directory structure
        directories = analysis.get("directories", [])
        if directories:
            score += 1
            feedback.append("✓ Good directory structure")
        else:
            feedback.append("~ All files in root directory - consider organizing into folders")
        
        # Check for logical file naming
        python_files = analysis.get("python_files", [])
        if python_files:
            score += 1
            # Look for main/init files
            has_main = any("main" in f.lower() for f in python_files)
            has_init = any("__init__" in f for f in python_files)
            
            if has_main:
                score += 1
                feedback.append("✓ Main entry point identified")
            elif has_init:
                feedback.append("✓ Package structure detected")
            else:
                feedback.append("~ Consider having a clear main entry point")
        
        return min(score, max_points)
    
    def _analyze_documentation(self, analysis: Dict, feedback: List[str]) -> int:
        """Analyze documentation quality (0-2 points)."""
        max_points = self.rubric["categories"]["documentation"]["max_points"]
        score = 0
        
        # Check for README
        if analysis.get("has_readme"):
            readme_content = analysis.get("readme_content", "")
            if readme_content and len(readme_content.strip()) > 50:
                score += 2
                feedback.append("✓ Comprehensive README file found")
            else:
                score += 1
                feedback.append("~ README exists but could be more detailed")
        else:
            feedback.append("✗ No README file found - add project documentation")
        
        return min(score, max_points)
    
    def _analyze_testing(self, analysis: Dict, feedback: List[str]) -> int:
        """Analyze testing and error handling (0-2 points)."""
        max_points = self.rubric["categories"]["testing"]["max_points"]
        score = 0
        
        # Check for test files
        if analysis.get("has_tests"):
            score += 2
            feedback.append("✓ Test files found - excellent!")
        else:
            feedback.append("✗ No test files detected - add unit tests")
        
        # Look for common Python patterns that suggest error handling
        python_files = analysis.get("python_files", [])
        if python_files and not analysis.get("has_tests"):
            # Give partial credit if they have multiple files (suggests some structure)
            if len(python_files) > 1:
                score += 1
                feedback.append("~ Multiple files suggest some error handling may be present")
        
        return min(score, max_points)
    
    def _analyze_efficiency(self, analysis: Dict, feedback: List[str]) -> int:
        """Analyze code efficiency and best practices (0-1 points)."""
        max_points = self.rubric["categories"]["efficiency"]["max_points"]
        score = 0
        
        # Basic efficiency indicators
        file_types = analysis.get("file_types", {})
        
        # Check for requirements.txt or config files
        if any(ext in file_types for ext in [".txt", ".json", ".yml", ".yaml"]):
            score += 1
            feedback.append("✓ Configuration files suggest good project setup")
        else:
            feedback.append("~ Consider adding requirements.txt or config files")
        
        return min(score, max_points)
    
    def format_grade_summary(self, scores: Dict) -> str:
        """Format grade summary for display."""
        categories = self.rubric["categories"]
        summary_lines = [f"Grade: {scores['total_grade']}/{self.rubric['total_points']}"]
        
        for category, details in categories.items():
            if category in scores:
                score = scores[category]
                max_score = details["max_points"]
                summary_lines.append(f"{category.title()}: {score}/{max_score}")
        
        return "\n".join(summary_lines)
    
    def get_rubric_description(self) -> str:
        """Get human-readable rubric description."""
        lines = [f"Grading Rubric (Total: {self.rubric['total_points']} points)"]
        
        for category, details in self.rubric["categories"].items():
            lines.append(f"• {category.title()} ({details['max_points']} pts): {details['description']}")
        
        return "\n".join(lines)