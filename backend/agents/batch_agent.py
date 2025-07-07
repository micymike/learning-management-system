from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any, List
import openai
import os

class BatchAgent(BaseAgent):
    def __init__(self):
        super().__init__("batch_agent")
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.batch_size = 5
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            students_data = data.get('students', [])
            rubric = data.get('rubric')
            
            # Process in batches to reduce token usage
            results = []
            for i in range(0, len(students_data), self.batch_size):
                batch = students_data[i:i + self.batch_size]
                batch_result = await self._process_batch(batch, rubric)
                results.extend(batch_result)
            
            return {'results': results, 'total_processed': len(results)}
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {'error': str(e)}
    
    async def _process_batch(self, batch: List[Dict], rubric: str) -> List[Dict]:
        # Combine multiple students into single prompt to reduce token usage
        combined_prompt = f"Rubric:\n{rubric}\n\nEvaluate the following {len(batch)} code submissions:\n\n"
        
        for i, student in enumerate(batch, 1):
            combined_prompt += f"Student {i} ({student.get('name', 'Unknown')}):\n"
            combined_prompt += f"Code:\n{student.get('code', '')}\n\n"
        
        combined_prompt += "Provide scores for each student in format:\nStudent X: [scores and justifications]"
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a batch code assessor. Evaluate multiple submissions efficiently."},
                {"role": "user", "content": combined_prompt}
            ],
            temperature=0.2
        )
        
        return self._parse_batch_response(response.choices[0].message.content, batch)
    
    def _parse_batch_response(self, content: str, batch: List[Dict]) -> List[Dict]:
        results = []
        lines = content.split('\n')
        
        for i, student in enumerate(batch, 1):
            student_result = {
                'student_name': student.get('name'),
                'repo_url': student.get('repo_url', ''),
                'scores': {},
                'status': 'completed'
            }
            
            # Simple parsing - look for "Student X:" patterns
            for line in lines:
                if f'Student {i}:' in line:
                    # Extract basic score info
                    if 'score' in line.lower():
                        try:
                            score = int(''.join(filter(str.isdigit, line)))
                            student_result['scores']['total'] = score
                        except:
                            student_result['scores']['total'] = 0
            
            results.append(student_result)
        
        return results