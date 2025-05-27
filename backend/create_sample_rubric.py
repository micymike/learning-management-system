import pandas as pd
import os
from openpyxl.styles import Font

# Create the data for the rubric
data = [
    ['Code Structure', 8, 'Core structural elements'],
    ['- Poor (0-2)', None, 'Code is disorganized and hard to follow'],
    ['- Basic (3-4)', None, 'Basic organization but lacks clear structure'],
    ['- Good (5-6)', None, 'Well-organized with clear sections'],
    ['- Excellent (7-8)', None, 'Exceptionally structured and modular'],
    [None, None, None],  # Empty row for spacing
    ['Documentation', 8, 'Code documentation quality'],
    ['- Poor (0-2)', None, 'No comments or documentation'],
    ['- Basic (3-4)', None, 'Minimal comments present'],
    ['- Good (5-6)', None, 'Clear comments explaining key parts'],
    ['- Excellent (7-8)', None, 'Comprehensive documentation'],
    [None, None, None],  # Empty row for spacing
    ['Testing', 8, 'Test implementation'],
    ['- Poor (0-2)', None, 'No testing implemented'],
    ['- Basic (3-4)', None, 'Basic error checks only'],
    ['- Good (5-6)', None, 'Good test coverage'],
    ['- Excellent (7-8)', None, 'Comprehensive test suite'],
    [None, None, None],  # Empty row for spacing
    ['Error Handling', 8, 'Error management'],
    ['- Poor (0-2)', None, 'No error handling'],
    ['- Basic (3-4)', None, 'Basic try-catch blocks'],
    ['- Good (5-6)', None, 'Most errors handled properly'],
    ['- Excellent (7-8)', None, 'Complete error handling with recovery']
]

# Create DataFrame
df = pd.DataFrame(data, columns=['Criterion', 'Points', 'Description'])

# Save to Excel with formatting
output_file = 'sample_rubric.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Rubric')
    
    # Get the workbook
    worksheet = writer.sheets['Rubric']
    
    # Set column widths
    worksheet.column_dimensions['A'].width = 40
    worksheet.column_dimensions['B'].width = 10
    worksheet.column_dimensions['C'].width = 50
    
    # Format headers with bold font
    bold_font = Font(bold=True)
    for cell in worksheet[1]:
        cell.font = bold_font
        
print(f"Created {output_file}")
