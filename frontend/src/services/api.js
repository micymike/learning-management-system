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
      const filename = response.headers.get('content-disposition')?.split('filename=')[1];
      if (!filename) {
        throw new Error('No filename provided in response headers');
      }
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
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
        return { success: true, data: response.assessments };
      } else {
        throw new Error(response.error || 'Failed to retrieve assessments');
      }
    } catch (error) {
      console.error('Error getting assessments:', error);
      throw error;
    }
  },
  
  // Get a specific assessment by ID from the backend
  getAssessment: async (id) => {
    try {
      const response = await fetchWithErrorHandling(`${API_URL}/assessments/${id}`, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.success && response.assessment) {
        return { success: true, data: response.assessment };
      }
      throw new Error(`Assessment with ID ${id} not found`);
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
    
    if (!rubric) {
      throw new Error('Rubric is required');
    }
    
    if (rubric instanceof File) {
      formData.append('rubric', rubric);
    } else if (typeof rubric === 'string') {
      const blob = new Blob([rubric], { type: 'text/plain' });
      const rubricFile = new File([blob], 'rubric.txt', { type: 'text/plain' });
      formData.append('rubric', rubricFile);
    }
    
    const response = await fetchWithErrorHandling(`${API_URL}/upload_csv`, {
      method: 'POST',
      body: formData,
      credentials: 'include'
    });
    
    return response;
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
      const filename = response.headers.get('content-disposition')?.split('filename=')[1];
      if (!filename) {
        throw new Error('No filename provided in response headers');
      }
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
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

  // Student-related methods
  getStudents: async () => {
    try {
      const response = await fetchWithErrorHandling(`${API_URL}/students`, {
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
      const response = await fetchWithErrorHandling(`${API_URL}/students/${studentId}`, {
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
      const response = await fetchWithErrorHandling(`${API_URL}/analytics`, {
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
