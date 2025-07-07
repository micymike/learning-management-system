from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any
import openai
import os

class AIDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai_detection_agent")
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            code = data.get('code')
            student_name = data.get('student_name')
            
            if not code:
                return {
                    'student_name': student_name,
                    'ai_percentage': 0,
                    'confidence': 'low',
                    'status': 'no_code'
                }
                
            ai_analysis = await self._detect_ai_code(code)
            
            return {
                'student_name': student_name,
                'ai_percentage': ai_analysis['percentage'],
                'confidence': ai_analysis['confidence'],
                'indicators': ai_analysis['indicators'],
                'status': 'completed'
            }
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {
                'student_name': data.get('student_name'),
                'error': str(e),
                'status': 'error'
            }
    
    async def _detect_ai_code(self, code: str) -> Dict[str, Any]:
        system_prompt = """You are an AI code detection expert. Analyze code for AI-generated patterns.
Return your analysis in this format:
Percentage: [0-100]
Confidence: [low/medium/high]
Indicators: [list of specific indicators found]"""
        
        user_prompt = f"""Analyze this code for AI-generated patterns:
- Overly perfect formatting
- Generic variable names
- Excessive comments
- Boilerplate patterns
- Lack of personal coding style

Code:
{code}"""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        
        return self._parse_ai_analysis(response.choices[0].message.content)
    
    def _parse_ai_analysis(self, content: str) -> Dict[str, Any]:
        lines = content.strip().split('\n')
        percentage = 0
        confidence = 'low'
        indicators = []
        
        for line in lines:
            if line.startswith('Percentage:'):
                try:
                    percentage = int(line.split(':')[1].strip().replace('%', ''))
                except:
                    percentage = 0
            elif line.startswith('Confidence:'):
                confidence = line.split(':')[1].strip().lower()
            elif line.startswith('Indicators:'):
                indicators_text = line.split(':', 1)[1].strip()
                indicators = [i.strip() for i in indicators_text.split(',')]
                
        return {
            'percentage': percentage,
            'confidence': confidence,
            'indicators': indicators
        }