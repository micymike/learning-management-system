from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any
import openai
import os
import re

class GradingAgent(BaseAgent):
    def __init__(self):
        super().__init__("grading_agent")
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            code = data.get('code')
            rubric = data.get('rubric')
            student_name = data.get('student_name')
            
            if not code or not rubric:
                raise ValueError("Code and rubric are required")
                
            scores = await self._assess_code(code, rubric)
            
            return {
                'student_name': student_name,
                'scores': scores,
                'status': 'completed'
            }
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {
                'student_name': data.get('student_name'),
                'error': str(e),
                'status': 'error'
            }
    
    async def _assess_code(self, code: str, rubric: str) -> Dict[str, Any]:
        system_prompt = """You are a code assessor. Evaluate code based on the rubric and return scores in this format:
Criterion: [Name]
Mark: [Score]
Justification: [Brief explanation]"""
        
        user_prompt = f"""Rubric:\n{rubric}\n\nCode:\n{code}\n\nEvaluate according to each criterion."""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        
        return self._parse_assessment(response.choices[0].message.content)
    
    def _parse_assessment(self, content: str) -> Dict[str, Any]:
        scores = {}
        criterion_pattern = r'Criterion:\s*(.*?)\s*\n'
        mark_pattern = r'Mark:\s*(.*?)\s*\n'
        justification_pattern = r'Justification:\s*(.*?)(?:\n\n|\Z)'
        
        criteria = re.findall(criterion_pattern, content, re.DOTALL)
        marks = re.findall(mark_pattern, content, re.DOTALL)
        justifications = re.findall(justification_pattern, content, re.DOTALL)
        
        for i in range(len(criteria)):
            if i < len(marks):
                scores[criteria[i].strip()] = {
                    'mark': marks[i].strip(),
                    'justification': justifications[i].strip() if i < len(justifications) else ''
                }
                
        return scores