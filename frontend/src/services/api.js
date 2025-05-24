/**
 * API service for making HTTP requests to the backend
 */

const API_URL = import.meta.env.VITE_API_URL || '';

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
      const response = await fetchWithErrorHandling(`${API_URL}/api/assessments`, {
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
        const response = await fetchWithErrorHandling(`${API_URL}/api/assessments/${id}`, {
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
    return fetchWithErrorHandling(`${API_URL}/api/assess`, {
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
      const response = await fetchWithErrorHandling(`${API_URL}/api/upload_csv`, {
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
      throw error;
    }
  },

  // Download Excel for a specific assessment
  downloadExcel: async (assessmentId) => {
    try {
      const response = await fetch(`${API_URL}/api/download_excel/${assessmentId}`, {
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
    return fetchWithErrorHandling(`${API_URL}/api/upload_rubric`, {
      method: 'POST',
      body: formData,
    });
  },

  // Submit GitHub URL for analysis
  uploadGithubUrl: (url) => {
    const formData = createFormData({ url });
    return fetchWithErrorHandling(`${API_URL}/api/upload_github_url`, {
      method: 'POST',
      body: formData,
    });
  },

  // Student-related methods
  getStudents: async () => {
    try {
      const response = await fetchWithErrorHandling(`${API_URL}/api/students`, {
        method: 'GET',
        credentials: 'include'
      });
      
      return response;
    } catch (error) {
      console.error('Failed to fetch students:', error);
      throw error;
    }
  },
  
  getStudent: async (studentId) => {
    try {
      const response = await fetchWithErrorHandling(`${API_URL}/api/students/${studentId}`, {
        method: 'GET',
        credentials: 'include'
      });
      
      return response;
    } catch (error) {
      console.error(`Failed to fetch student ${studentId}:`, error);
      throw error;
    }
  },

  // Analytics
  getAnalytics: async () => {
    try {
      const response = await fetchWithErrorHandling(`${API_URL}/api/analytics`, {
        method: 'GET',
        credentials: 'include'
      });
      return response;
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      throw error;
    }
  },
};

export default {
  ...assessApi,
  getStudents: assessApi.getStudents,
  getStudent: assessApi.getStudent,
  getAnalytics: assessApi.getAnalytics,
};
