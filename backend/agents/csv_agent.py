from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any
import pandas as pd
from io import StringIO
import csv

class CSVAgent(BaseAgent):
    def __init__(self):
        super().__init__("csv_agent")
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            file_content = data.get('file_content')
            filename = data.get('filename', '').lower()
            
            if filename.endswith('.csv'):
                return self._process_csv(file_content)
            elif filename.endswith(('.xlsx', '.xls')):
                return self._process_excel(data.get('file_storage'))
            else:
                raise ValueError('Unsupported file type')
                
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {'error': str(e)}
    
    def _process_csv(self, content: str) -> Dict[str, Any]:
        reader = csv.reader(StringIO(content))
        headers = next(reader, [])
        students = []
        
        for row in reader:
            if not any(row):
                continue
            student_data = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    header = headers[i].lower()
                    if 'name' in header:
                        student_data['name'] = value.strip()
                    elif header == 'repo_url' or ('github' in header and 'url' in header):
                        student_data['repo_url'] = value.strip()

            if 'name' in student_data and 'repo_url' in student_data:
                students.append(student_data)
                
        return {'students': students, 'count': len(students)}
    
    def _process_excel(self, file_storage) -> Dict[str, Any]:
        df = pd.read_excel(file_storage)
        students = []
        
        for _, row in df.iterrows():
            student_data = {}
            for col in df.columns:
                col_lower = col.lower()
                value = str(row[col]) if not pd.isnull(row[col]) else ''
                if 'name' in col_lower:
                    student_data['name'] = value.strip()
                elif col_lower == 'repo_url' or ('github' in col_lower and 'url' in col_lower):
                    student_data['repo_url'] = value.strip()

            if 'name' in student_data and 'repo_url' in student_data:
                students.append(student_data)
                
        return {'students': students, 'count': len(students)}
