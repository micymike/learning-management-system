from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any
import requests
import tempfile
import zipfile
import os
import glob

class RepoAgent(BaseAgent):
    def __init__(self):
        super().__init__("repo_agent")
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            repo_url = data.get('repo_url')
            student_name = data.get('student_name')
            
            if not repo_url:
                raise ValueError("Repository URL is required")
                
            code = await self._analyze_repo(repo_url)
            
            return {
                'student_name': student_name,
                'repo_url': repo_url,
                'code': code,
                'status': 'success' if code else 'no_code_found'
            }
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {
                'student_name': data.get('student_name'),
                'repo_url': data.get('repo_url'),
                'error': str(e),
                'status': 'error'
            }
    
    async def _analyze_repo(self, url: str) -> str:
        if url.endswith('/'):
            url = url[:-1]
        if url.endswith('.git'):
            url = url[:-4]
            
        user_repo = '/'.join(url.split('/')[-2:])
        
        for branch in ['main', 'master']:
            zip_url = f"https://github.com/{user_repo}/archive/refs/heads/{branch}.zip"
            r = requests.get(zip_url)
            
            if r.status_code == 404:
                continue
            elif r.status_code != 200:
                continue
                
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, 'repo.zip')
                with open(zip_path, 'wb') as f:
                    f.write(r.content)
                    
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(tmpdir)
                except zipfile.BadZipFile:
                    continue
                    
                code = ""
                for ext in ['py', 'js', 'jsx', 'ts', 'tsx', 'java', 'cpp', 'c']:
                    for file in glob.glob(os.path.join(tmpdir, '**', f'*.{ext}'), recursive=True):
                        try:
                            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                                code += f.read() + '\n\n'
                        except Exception:
                            continue

                return code[:10000] if code else ""
                
        raise Exception(f"Could not access repository: {url}")
