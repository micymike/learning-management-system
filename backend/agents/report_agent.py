from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any, List
import pandas as pd
import io
from openpyxl.styles import PatternFill, Font

class ReportAgent(BaseAgent):
    def __init__(self):
        super().__init__("report_agent")
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            results = data.get('results', [])
            
            if not results:
                raise ValueError("No results to process")
                
            excel_file = await self._generate_excel_report(results)
            summary = await self._generate_summary(results)
            
            return {
                'excel_file': excel_file,
                'summary': summary,
                'status': 'completed'
            }
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {
                'error': str(e),
                'status': 'error'
            }
    
    async def _generate_excel_report(self, results: List[Dict]) -> io.BytesIO:
        # Flatten results for DataFrame
        flattened_data = []
        
        for result in results:
            row = {
                'Student Name': result.get('student_name', ''),
                'Repository URL': result.get('repo_url', ''),
                'AI Percentage': result.get('ai_percentage', 0),
                'Status': result.get('status', 'unknown')
            }
            
            # Add scores
            scores = result.get('scores', {})
            for criterion, score_data in scores.items():
                if isinstance(score_data, dict):
                    row[f"{criterion} - Score"] = score_data.get('mark', '')
                    row[f"{criterion} - Justification"] = score_data.get('justification', '')
                else:
                    row[criterion] = score_data
                    
            flattened_data.append(row)
        
        df = pd.DataFrame(flattened_data)
        
        # Create Excel file
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        df.to_excel(writer, sheet_name='Assessment Results', index=False)
        
        # Format Excel
        workbook = writer.book
        worksheet = writer.sheets['Assessment Results']
        
        # Header formatting
        for col in range(len(df.columns)):
            cell = worksheet.cell(row=1, column=col + 1)
            cell.fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
            cell.font = Font(color='FFFFFF', bold=True)
        
        # Auto-adjust columns
        for column in worksheet.columns:
            max_length = max(len(str(cell.value or '')) for cell in column)
            worksheet.column_dimensions[column[0].column_letter].width = min(max_length + 2, 50)
        
        writer.close()
        output.seek(0)
        return output
    
    async def _generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        total_students = len(results)
        successful_assessments = sum(1 for r in results if r.get('status') == 'completed')
        avg_ai_percentage = sum(r.get('ai_percentage', 0) for r in results) / total_students if total_students > 0 else 0
        
        return {
            'total_students': total_students,
            'successful_assessments': successful_assessments,
            'failed_assessments': total_students - successful_assessments,
            'average_ai_percentage': round(avg_ai_percentage, 2),
            'success_rate': round((successful_assessments / total_students) * 100, 2) if total_students > 0 else 0
        }