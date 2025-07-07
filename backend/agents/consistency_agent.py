from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any, List
import openai
import os
import statistics

class ConsistencyAgent(BaseAgent):
    def __init__(self):
        super().__init__("consistency_agent")
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            code = data.get('code')
            rubric = data.get('rubric')
            student_name = data.get('student_name')
            runs = data.get('runs', 3)
            
            # Run multiple assessments for consistency
            assessments = []
            for _ in range(runs):
                assessment = await self._single_assessment(code, rubric)
                assessments.append(assessment)
            
            # Calculate consistency metrics
            consistency_result = self._calculate_consistency(assessments)
            
            return {
                'student_name': student_name,
                'assessments': assessments,
                'consistency': consistency_result,
                'final_score': consistency_result['median_score']
            }
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {'error': str(e)}
    
    async def _single_assessment(self, code: str, rubric: str) -> Dict[str, Any]:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a consistent code assessor. Provide numerical scores."},
                {"role": "user", "content": f"Rubric:\n{rubric}\n\nCode:\n{code}\n\nProvide numerical scores only."}
            ],
            temperature=0.1
        )
        
        return self._extract_numerical_scores(response.choices[0].message.content)
    
    def _extract_numerical_scores(self, content: str) -> Dict[str, Any]:
        scores = {}
        lines = content.split('\n')
        
        for line in lines:
            if ':' in line and any(char.isdigit() for char in line):
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    try:
                        value = int(''.join(filter(str.isdigit, parts[1])))
                        scores[key] = value
                    except:
                        continue
        
        return {'scores': scores, 'total': sum(scores.values())}
    
    def _calculate_consistency(self, assessments: List[Dict]) -> Dict[str, Any]:
        all_scores = []
        for assessment in assessments:
            total = sum(assessment.get('scores', {}).values())
            all_scores.append(total)
        
        if not all_scores:
            return {'consistency': 'low', 'variance': 0, 'median_score': 0}
        
        variance = statistics.variance(all_scores) if len(all_scores) > 1 else 0
        median_score = statistics.median(all_scores)
        
        # Determine consistency level
        if variance < 5:
            consistency = 'high'
        elif variance < 15:
            consistency = 'medium'
        else:
            consistency = 'low'
        
        return {
            'consistency': consistency,
            'variance': variance,
            'median_score': median_score,
            'all_scores': all_scores
        }