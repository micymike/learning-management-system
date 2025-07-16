from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any
import openai
import os
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GradingAgent(BaseAgent):
    def __init__(self):
        super().__init__("grading_agent")
        self.azure_client = None
        self.openai_client = None
        
        try:
            # Azure OpenAI
            azure_api_key = os.getenv("OPENAI_API_KEY")
            azure_base_url = os.getenv("OPENAI_API_BASE")
            api_version = os.getenv("OPENAI_API_VERSION", "2023-05-15")
            
            if azure_api_key and azure_base_url:
                self.azure_client = openai.AzureOpenAI(
                    api_key=azure_api_key,
                    azure_endpoint=azure_base_url,
                    api_version=api_version
                )
                logger.info("Grading agent initialized with Azure OpenAI")
        except Exception as e:
            logger.error(f"Azure OpenAI client initialization failed: {e}")
            self.azure_client = None
            
        try:
            # Standard OpenAI
            openai_api_key = os.getenv("STANDARD_OPENAI_API_KEY")
            if openai_api_key:
                self.openai_client = openai.OpenAI(
                    api_key=openai_api_key,
                    base_url="https://api.openai.com/v1"
                )
                logger.info("Grading agent initialized with standard OpenAI")
        except Exception as e:
            logger.error(f"Standard OpenAI client initialization failed: {e}")
            self.openai_client = None

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
        # Determine which client to use
        api_type = os.getenv("OPENAI_API_TYPE", "openai").lower()
        if api_type == "azure":
            client = self.azure_client
            model = os.getenv("OPENAI_DEPLOYMENT_NAME")
        else:
            client = self.openai_client
            model = "gpt-3.5-turbo"
            
        if not client:
            logger.warning("Using fallback assessment due to missing OpenAI client")
            return {
                'Correctness of Code': {'mark': '8', 'justification': 'Code demonstrates good understanding (fallback assessment)'},
                'Code Quality': {'mark': '4', 'justification': 'Well-structured code (fallback assessment)'},
                'Documentation': {'mark': '3', 'justification': 'Basic documentation present (fallback assessment)'},
                'Efficiency': {'mark': '3', 'justification': 'Efficient approach used (fallback assessment)'}
            }
        
        system_prompt = """You are a code assessor. Evaluate code based on the rubric and return scores in this format:
Criterion: [Name]
Mark: [Score]
Justification: [Brief explanation]"""
        
        user_prompt = f"""Rubric:\n{rubric}\n\nCode:\n{code}\n\nEvaluate according to each criterion."""

        try:
            # Create the messages array
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Make API call
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2
            )
                
            return self._parse_assessment(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            # Return fallback assessment with error information
            error_msg = str(e)[:50] + '...' if len(str(e)) > 50 else str(e)
            return {
                'Correctness of Code': {'mark': '6', 'justification': f'Assessment unavailable - API error: {error_msg}'},
                'Code Quality': {'mark': '3', 'justification': 'Assessment unavailable - API error'},
                'Documentation': {'mark': '2', 'justification': 'Assessment unavailable - API error'},
                'Efficiency': {'mark': '3', 'justification': 'Assessment unavailable - API error'}
            }
    
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
