from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any, List
import openai
import os
import re

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
                    'student_name': student.get('student_name'),
                    'repo_url': student.get('repo_url', ''),
                    'scores': {'total': 15},
                    'status': 'completed_fallback'
                })
            return results

        # Combine multiple students into single prompt with structured format instructions
        combined_prompt = f"""Rubric:
{rubric}

Evaluate the following {len(batch)} code submissions. For EACH student, provide scores in this EXACT format:

Student X (Name):
- Criterion1: Score
  - Justification for criterion1 score
- Criterion2: Score
  - Justification for criterion2 score
- Criterion3: Score
  - Justification for criterion3 score

Where:
- Each criterion is on its own line starting with a dash
- Each score is a number based on the rubric without any text after it
- Each justification is on the next line, indented with 2 spaces and starting with a dash

Here are the submissions:
"""

        for i, student in enumerate(batch, 1):
            combined_prompt += f"\nStudent {i} ({student.get('student_name', 'Unknown')}):\nCode:\n{student.get('code', '')}\n"

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a batch code assessor. Evaluate multiple submissions efficiently. Follow the EXACT output format requested in the prompt. Always provide scores as numbers between 1-10 for each criterion, followed by justifications on the next line with proper indentation."},
                    {"role": "user", "content": combined_prompt}
                ],
                temperature=0.1
            )
            print("=== OpenAI Batch Response ===")
            print(response.choices[0].message.content)
            print("============================")
            return self._parse_batch_response(response.choices[0].message.content, batch)
        except Exception as e:
            print(f"Batch OpenAI API call failed: {e}")
            results = []
            for student in batch:
                results.append({
                    'student_name': student.get('student_name'),
                    'repo_url': student.get('repo_url', ''),
                    'scores': {'total': 10},
                    'status': 'completed_with_error'
                })
            return results
    
    def _parse_batch_response(self, content: str, batch: List[Dict]) -> List[Dict]:
        results = []
        
        for idx, student in enumerate(batch):
            student_name = student.get('student_name')
            student_result = {
                'student_name': student_name,
                'repo_url': student.get('repo_url', ''),
                'scores': {},
                'status': 'completed'
            }
            
            # Look for this student's section in the content
            student_pattern = rf"Student \d+\s*\({student_name}\):"
            student_match = re.search(student_pattern, content)
            
            if student_match:
                # Find the start of this student's section
                start_pos = student_match.start()
                
                # Find the start of the next student's section or end of content
                next_student_match = re.search(r"Student \d+\s*\(.*?\):", content[start_pos + 1:])
                end_pos = len(content) if not next_student_match else start_pos + 1 + next_student_match.start()
                
                # Extract this student's section
                student_section = content[start_pos:end_pos]
                
                # Extract criteria scores using regex that matches our requested format
                # Format: "- Criterion: Score" followed by indented "- Justification"
                criteria_pattern = r"- ([^:]+):\s*(\d+)\s*\n\s+- ([^\n]+)"
                criteria_matches = re.findall(criteria_pattern, student_section)
                
                for criterion, score, justification in criteria_matches:
                    criterion = criterion.strip()
                    student_result['scores'][criterion] = {
                        'mark': int(score),
                        'justification': justification.strip()
                    }
                
                # Calculate total score
                if student_result['scores']:
                    total_score = sum(item['mark'] for item in student_result['scores'].values())
                    student_result['scores']['total'] = total_score
            
            results.append(student_result)
        
        # Debug output
        print("=== DEBUG: Parsed Results ===")
        import json
        print(json.dumps(results, indent=2))
        print("=== END DEBUG ===")
        
        return results
