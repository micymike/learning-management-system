import * as XLSX from 'xlsx';

export const excelToText = async (file) => {
  try {
    // Create a blob URL from the Excel file
    const buffer = await file.arrayBuffer();
    const workbook = XLSX.read(buffer, { type: 'array' });
    
    // Get the first worksheet
    const worksheet = workbook.Sheets[workbook.SheetNames[0]];
    
    // Convert worksheet to array of arrays
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    
    // Format rows into rubric text
    const rubricText = data
      .filter(row => row.length > 0) // Skip empty rows
      .map(row => {
        // Check if this is a criterion row (contains "[X points]")
        if (row[0] && row[0].includes("[") && row[0].includes("points]")) {
          return row[0]; // Main criterion with points
        }
        // Check if this is a level description row (starts with - or *)
        else if (row[0] && (row[0].startsWith("-") || row[0].startsWith("*"))) {
          return row[0]; // Level description
        }
        // Format other rows as criteria if they contain points
        else if (row.length >= 2) {
          const criterion = row[0];
          const points = parseFloat(row[1]);
          if (!isNaN(points)) {
            return `${criterion} [${points} points]`;
          }
        }
        return row[0];
      })
      .filter(line => line) // Remove undefined/empty lines
      .join("\n");
    
    return rubricText;
  } catch (error) {
    console.error("Error converting Excel to text:", error);
    throw new Error("Failed to convert Excel file to text format");
  }
};

export const validateExcelRubric = (textContent) => {
  // Check if there's at least one criterion with points
  if (!textContent.includes("[") || !textContent.includes("points]")) {
    throw new Error("Excel file must contain at least one criterion with points specified");
  }
  
  // Split into lines and check format
  const lines = textContent.split("\n").filter(line => line.trim());
  if (lines.length < 2) {
    throw new Error("Rubric must contain at least one criterion and one level description");
  }
  
  return true;
};
