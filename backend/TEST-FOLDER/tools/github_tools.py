import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Dict, List
import git
import requests
from urllib.parse import urlparse
from config.settings import TEMP_DIR, GITHUB_TOKEN, MAX_REPO_SIZE_MB

class GitHubTools:
    def __init__(self):
        self.temp_dir = TEMP_DIR
        
    def clone_repository(self, github_url: str, student_name: str) -> Dict:
        """Clone a GitHub repository and return analysis data."""
        try:
            # Create unique directory for this student's repo
            repo_dir = self.temp_dir / f"{student_name.replace(' ', '_')}"
            
            # Clean up if directory exists
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            
            # Clone the repository
            repo = git.Repo.clone_from(github_url, repo_dir)
            
            # Check repository size
            size_mb = self._get_directory_size(repo_dir) / (1024 * 1024)
            if size_mb > MAX_REPO_SIZE_MB:
                return {
                    "success": False,
                    "error": f"Repository too large: {size_mb:.1f}MB (max: {MAX_REPO_SIZE_MB}MB)",
                    "repo_path": None
                }
            
            return {
                "success": True,
                "repo_path": repo_dir,
                "size_mb": size_mb,
                "error": None
            }
            
        except git.GitCommandError as e:
            return {
                "success": False,
                "error": f"Git clone failed: {str(e)}",
                "repo_path": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "repo_path": None
            }
    
    def analyze_repository_structure(self, repo_path: Path) -> Dict:
        """Analyze the structure and contents of a cloned repository."""
        if not repo_path or not repo_path.exists():
            return {"error": "Repository path does not exist"}
        
        analysis = {
            "files": [],
            "directories": [],
            "file_types": {},
            "has_readme": False,
            "has_tests": False,
            "python_files": [],
            "readme_content": None,
            "total_files": 0
        }
        
        try:
            # Walk through all files
            for item in repo_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(repo_path)
                    analysis["files"].append(str(relative_path))
                    analysis["total_files"] += 1
                    
                    # Track file types
                    ext = item.suffix.lower()
                    analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                    
                    # Check for Python files
                    if ext == ".py":
                        analysis["python_files"].append(str(relative_path))
                    
                    # Check for README
                    if item.name.lower().startswith("readme"):
                        analysis["has_readme"] = True
                        try:
                            analysis["readme_content"] = item.read_text(encoding='utf-8')
                        except:
                            analysis["readme_content"] = "Could not read README content"
                    
                    # Check for test files
                    if ("test" in item.name.lower() or 
                        item.name.lower().startswith("test_") or
                        item.name.lower().endswith("_test.py")):
                        analysis["has_tests"] = True
                
                elif item.is_dir():
                    analysis["directories"].append(str(item.relative_to(repo_path)))
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze repository: {str(e)}"}
    
    def cleanup_repository(self, repo_path: Path):
        """Clean up cloned repository."""
        try:
            if repo_path and repo_path.exists():
                shutil.rmtree(repo_path)
        except Exception as e:
            print(f"Warning: Could not clean up {repo_path}: {e}")
    
    def _get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes."""
        total_size = 0
        for item in path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size
    
    def validate_github_url(self, url: str) -> bool:
        """Validate if URL is a proper GitHub repository URL."""
        try:
            parsed = urlparse(url)
            return (parsed.netloc.lower() in ["github.com", "www.github.com"] and
                    len(parsed.path.strip("/").split("/")) >= 2)
        except:
            return False