from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any, List
import openai
import os

class BatchAgent(BaseAgent):
    def __init__(self):
        super().__init__("batch_agent")
        self.batch_size = 5
        self.azure_client = None
        self.openai_client = None
        try:
            # Azure OpenAI
            azure_api_key = os.getenv("OPENAI_API_KEY")
            if azure_api_key:
                # Azure OpenAI: use custom base_url if needed
                azure_base_url = os.getenv("OPENAI_API_BASE")
                if azure_base_url:
                    self.azure_client = openai.OpenAI(api_key=azure_api_key, base_url=azure_base_url)
                else:
                    self.azure_client = openai.OpenAI(api_key=azure_api_key)
        except Exception as e:
            print(f"Warning: Azure OpenAI client initialization failed: {e}")
            self.azure_client = None
        try:
            # Standard OpenAI
            openai_api_key = os.getenv("STANDARD_OPENAI_API_KEY")
            if openai_api_key:
                # Standard OpenAI: always use official base_url
                self.openai_client = openai.OpenAI(
                    api_key=openai_api_key,
                    base_url="https://api.openai.com/v1"
                )
        except Exception as e:
            print(f"Warning: Standard OpenAI client initialization failed: {e}")
            self.openai_client = None

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            students_data = data.get('students', [])
            rubric = data.get('rubric')
            api_type = data.get('api_type', None)
            # Default: use OPENAI_API_TYPE env, fallback to 'openai'
            if not api_type:
                api_type = os.getenv("OPENAI_API_TYPE", "openai").lower()
            if api_type == "azure":
                client = self.azure_client
            else:
                client = self.openai_client

            # Process in batches to reduce token usage
            results = []
            for i in range(0, len(students_data), self.batch_size):
                batch = students_data[i:i + self.batch_size]
                batch_result = await self._process_batch(batch, rubric, client)
                results.extend(batch_result)

            return {'results': results, 'total_processed': len(results)}

        except Exception as e:
            self.status = AgentStatus.ERROR
            return {'error': str(e)}

    async def _process_batch(self, batch: List[Dict], rubric: str, client) -> List[Dict]:
        if not client:
            # Fallback processing when OpenAI is not available
            results = []
            for student in batch:
                results.append({
                    'student_name': student.get('name'),
                    'repo_url': student.get('repo_url', ''),
                    'scores': {'total': 15},
                    'status': 'completed_fallback'
                })
            return results

        # Combine multiple students into single prompt
        combined_prompt = f"Rubric:\n{rubric}\n\nEvaluate the following {len(batch)} code submissions:\n\n"

        for i, student in enumerate(batch, 1):
            combined_prompt += f"Student {i} ({student.get('name', 'Unknown')}):\n"
            combined_prompt += f"Code:\n{student.get('code', '')}\n\n"

        combined_prompt += "Provide scores for each student in format:\nStudent X: [scores and justifications]"

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a batch code assessor. Evaluate multiple submissions efficiently."},
                    {"role": "user", "content": combined_prompt}
                ],
                temperature=0.2
            )
            return self._parse_batch_response(response.choices[0].message.content, batch)
        except Exception as e:
            print(f"Batch OpenAI API call failed: {e}")
            results = []
            for student in batch:
                results.append({
                    'student_name': student.get('name'),
                    'repo_url': student.get('repo_url', ''),
                    'scores': {'total': 10},
                    'status': 'completed_with_error'
                })
            return results
    
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
