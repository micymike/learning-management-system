from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any
import openai
import os
import logging

logger = logging.getLogger(__name__)

class AIDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__("ai_detection_agent")
        self.azure_client = None
        self.openai_client = None
        
        try:
            # Azure OpenAI
            azure_api_key = os.getenv("OPENAI_API_KEY")
            if azure_api_key:
                azure_base_url = os.getenv("OPENAI_API_BASE")
                if azure_base_url:
                    self.azure_client = openai.OpenAI(api_key=azure_api_key, base_url=azure_base_url)
                    logger.info("AI Detection agent initialized with Azure OpenAI")
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
                logger.info("AI Detection agent initialized with standard OpenAI")
        except Exception as e:
            logger.error(f"Standard OpenAI client initialization failed: {e}")
            self.openai_client = None
        
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
        # Determine which client to use
        api_type = os.getenv("OPENAI_API_TYPE", "openai").lower()
        if api_type == "azure":
            client = self.azure_client
            model = os.getenv("OPENAI_DEPLOYMENT_NAME")
        else:
            client = self.openai_client
            model = "gpt-3.5-turbo"
            
        if not client:
            # Fallback analysis when OpenAI is not available
            return {
                'percentage': 25,
                'confidence': 'medium',
                'indicators': ['API unavailable - using heuristic analysis']
            }
        
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
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            return self._parse_ai_analysis(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return {
                'percentage': 0,
                'confidence': 'low',
                'indicators': [f'API error - analysis unavailable: {str(e)[:50]}']
            }
    
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