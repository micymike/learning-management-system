/**
 * API service for making HTTP requests to the backend
 */

const API_URL = import.meta.env.VITE_API_URL;

/**
 * Generic fetch wrapper with error handling
 */
async function fetchWithErrorHandling(url, options = {}) {
  try {
    // Don't set Content-Type for FormData as it needs to include the boundary
    const headers = options.body instanceof FormData 
      ? options.headers
      : {
          'Content-Type': 'application/json',
          ...options.headers,
        };

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API error: ${response.status}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'assessment_scores.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      return { success: true, message: 'Excel file downloaded successfully' };
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * Creates FormData from an object
 */
function createFormData(data) {
  const formData = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    formData.append(key, value);
  });
  return formData;
}

/**
 * API methods for code assessment
 */
export const assessApi = {
  // Get all assessments from the backend
  getAssessments: async () => {
    try {
      const response = await fetchWithErrorHandling(`${API_URL}/assessments`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.success && response.assessments) {
        // Also save to localStorage as a fallback
        localStorage.setItem('savedAssessments', JSON.stringify(response.assessments));
        return { success: true, data: response.assessments };
      } else {
        throw new Error(response.error || 'Failed to retrieve assessments');
      }
    } catch (error) {
      console.error('Error getting assessments:', error);
      
      // Fallback to localStorage if backend fails
      try {
        const savedAssessments = localStorage.getItem('savedAssessments');
        if (savedAssessments) {
          const assessments = JSON.parse(savedAssessments);
          return { success: true, data: assessments, source: 'localStorage' };
        }
      } catch (localError) {
        console.error('Error retrieving from localStorage:', localError);
      }
      
      throw error;
    }
  },
  
  // Get a specific assessment by ID from the backend
  getAssessment: async (id) => {
    try {
      // First try to get from backend
      try {
        const response = await fetchWithErrorHandling(`${API_URL}/assessments/${id}`, {
          method: 'GET',
          credentials: 'include'
        });
        
        if (response.success && response.assessment) {
          return { success: true, data: response.assessment };
        }
      } catch (backendError) {
        console.error('Backend retrieval failed, trying localStorage:', backendError);
      }
      
      // Fallback to localStorage
      const savedAssessments = localStorage.getItem('savedAssessments');
      if (!savedAssessments) {
        throw new Error('No assessments found');
      }

      let assessments = [];
      try {
        assessments = JSON.parse(savedAssessments);
      } catch (error) {
        console.error('Error parsing saved assessments:', error);
        throw new Error('Invalid assessment data');
      }

      if (!Array.isArray(assessments)) {
        throw new Error('Invalid assessment data structure');
      }
      
      // Convert id to string for comparison since URL params are strings
      const strId = String(id);
      const assessment = assessments.find(a => String(a.id) === strId);
      
      if (!assessment) {
        throw new Error(`Assessment with ID ${id} not found`);
      }
      
      return { 
        success: true,
        data: assessment,
        source: 'localStorage'
      };
    } catch (error) {
      console.error('Error getting assessment:', error);
      throw error;
    }
  },
  
  // Assess code with rubric
  assess: (code, rubric) => {
    const formData = createFormData({ code, rubric });
    return fetchWithErrorHandling(`${API_URL}/assess`, {
      method: 'POST',
      body: formData,
    });
  },

  // Upload and process CSV file with student data
  uploadCSV: async (file, rubric, assessmentName = '') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', assessmentName); // Add assessment name to form data
    
    if (rubric instanceof File) {
      formData.append('rubric', rubric);
    } else if (typeof rubric === 'string') {
      // Create a proper file object from the string
      const blob = new Blob([rubric], { type: 'text/plain' });
      const rubricFile = new File([blob], 'rubric.txt', { type: 'text/plain' });
      formData.append('rubric', rubricFile);
    } else {
      // If no rubric provided, create a default one
      const defaultRubric = "Code Quality\nFunctionality\nBest Practices";
      const blob = new Blob([defaultRubric], { type: 'text/plain' });
      const rubricFile = new File([blob], 'default_rubric.txt', { type: 'text/plain' });
      formData.append('rubric', rubricFile);
    }
    
    try {
      // Try to use the backend API
      const response = await fetchWithErrorHandling(`${API_URL}/upload_csv`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });
      
      // If successful, update localStorage with the new assessment
      if (response.success && response.assessment) {
        try {
          const savedAssessments = localStorage.getItem('savedAssessments');
          const assessments = savedAssessments ? JSON.parse(savedAssessments) : [];
          
          // Check if assessment already exists
          const existingIndex = assessments.findIndex(a => a.id === response.assessment.id);
          if (existingIndex >= 0) {
            assessments[existingIndex] = response.assessment;
          } else {
            assessments.push(response.assessment);
          }
          
          localStorage.setItem('savedAssessments', JSON.stringify(assessments));
        } catch (storageError) {
          console.error('Error updating localStorage:', storageError);
        }
      }
      
      return response;
    } catch (error) {
      console.error('Failed to process CSV with API:', error);
      
      // Fallback to local processing if API call fails
      console.log('Using local processing fallback');
      
      try {
        // Read the CSV file content
        const csvContent = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = (event) => resolve(event.target.result);
          reader.onerror = () => reject(new Error('Error reading CSV file'));
          reader.readAsText(file);
        });
        
        // Parse CSV content (simple parser)
        const lines = csvContent.split('\n').filter(line => line.trim());
        if (lines.length === 0) {
          throw new Error('CSV file is empty');
        }
        
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        
        // Check if required headers exist
        if (!headers.includes('name') && !headers.includes('student')) {
          throw new Error('CSV must contain a "name" or "student" column');
        }
        
        if (!headers.includes('repo_url') && !headers.includes('github')) {
          throw new Error('CSV must contain a "repo_url" or "github" column');
        }
        
        // Parse the rubric into criteria
        const rubricLines = rubric.split('\n').filter(line => line.trim());
        if (rubricLines.length === 0) {
          throw new Error('Rubric cannot be empty');
        }
        
        // Generate results based on student data
        const results = [];
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(',').map(v => v.trim());
          if (values.length < 2) continue; // Skip invalid lines
          
          const student = {};
          headers.forEach((header, index) => {
            if (index < values.length) {
              student[header] = values[index];
            }
          });
          
          // Ensure we have name and repo_url
          if (!student.name && student.student) {
            student.name = student.student;
          }
          
          if (!student.repo_url && student.github) {
            student.repo_url = student.github;
          }
          
          // In a real implementation, we would call the backend API to assess the code
          // For now, we'll create placeholder results that clearly indicate they need assessment
          
          // Create a placeholder assessment report
          let report = "### Assessment Pending\n\n";
          report += "This student's code needs to be assessed based on the following criteria:\n\n";
          
          rubricLines.forEach(criterion => {
            if (!criterion.trim()) return;
            report += `- ${criterion.trim()}\n`;
          });
          
          report += "\n**Note:** This is a placeholder. In a production environment, the actual code would be assessed against the rubric.";
          
          results.push({
            name: student.name || `Student ${i}`,
            repo_url: student.repo_url || '',
            group: student.group || 'Unassigned',
            score: 'Pending',
            status: 'Needs Assessment',
            report: report
          });
        }
        
        // Create a new assessment with a proper name
        const newAssessment = {
          id: Date.now().toString(),
          name: assessmentName && assessmentName.trim() !== '' 
            ? assessmentName 
            : 'Assessment ' + new Date().toLocaleDateString(),
          createdAt: new Date().toISOString(),
          status: 'Pending Assessment',
          rubric: rubric,
          results: results
        };
        
        // Save to localStorage
        const savedAssessments = localStorage.getItem('savedAssessments');
        const assessments = savedAssessments ? JSON.parse(savedAssessments) : [];
        assessments.push(newAssessment);
        localStorage.setItem('savedAssessments', JSON.stringify(assessments));
        
        return {
          success: true,
          message: 'Assessment created successfully (local fallback)',
          results: results,
          assessment: newAssessment
        };
      } catch (fallbackError) {
        console.error('Local processing failed:', fallbackError);
        throw new Error('Failed to process CSV file: ' + (fallbackError.message || 'Unknown error'));
      }
    }
  },

  // Download Excel for a specific assessment
  downloadExcel: async (assessmentId) => {
    try {
      const response = await fetch(`${API_URL}/download_excel/${assessmentId}`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `API error: ${response.status}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.headers.get('content-disposition')?.split('filename=')[1] || `assessment_${assessmentId}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      return { success: true, message: 'Excel file downloaded successfully' };
    } catch (error) {
      console.error('Error downloading Excel:', error);
      throw error;
    }
  },

  // Upload rubric file
  uploadRubric: (file) => {
    const formData = createFormData({ file });
    return fetchWithErrorHandling(`${API_URL}/upload_rubric`, {
      method: 'POST',
      body: formData,
    });
  },

  // Submit GitHub URL for analysis
  uploadGithubUrl: (url) => {
    const formData = createFormData({ url });
    return fetchWithErrorHandling(`${API_URL}/upload_github_url`, {
      method: 'POST',
      body: formData,
    });
  },
};

export default {
  assess: assessApi,
};
