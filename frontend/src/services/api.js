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

    // For debugging
    console.log('Making request to:', url);
    console.log('Request method:', options.method);
    console.log('Request headers:', headers);
    
    if (options.body instanceof FormData) {
      console.log('Request contains FormData with the following entries:');
      for (let [key, value] of options.body.entries()) {
        if (value instanceof File || value instanceof Blob) {
          console.log(`${key}: ${value.name}, ${value.type}, ${value.size} bytes`);
        } else {
          console.log(`${key}: ${value}`);
        }
      }
    }
    
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include',
    });
    
    // Log response status and headers
    console.log('Response status:', response.status);
    console.log('Response headers:', {
      'content-type': response.headers.get('content-type'),
      'content-length': response.headers.get('content-length')
    });

    if (!response.ok) {
      try {
        // Clone the response before trying to parse it as JSON
        const clonedResponse = response.clone();
        
        try {
          const errorData = await response.json();
          console.log('Error response data (JSON):', errorData);
          throw new Error(errorData.error || errorData.message || `API error: ${response.status}`);
        } catch (jsonError) {
          console.log('Failed to parse error response as JSON, trying text:', jsonError);
          
          // Try to get the response as text instead
          const textResponse = await clonedResponse.text();
          console.log('Error response text:', textResponse);
          
          throw new Error(`API error: ${response.status} - ${textResponse.substring(0, 100)}`);
        }
      } catch (responseError) {
        console.log('Failed to parse error response:', responseError);
        throw new Error(`API error: ${response.status}`);
      }
    }

    // Check if response is a file download
    const contentDisposition = response.headers.get('content-disposition');
    if (contentDisposition && contentDisposition.includes('attachment')) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const filename = contentDisposition.split('filename=')[1]?.replace(/"/g, '');
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
      console.log('Fetching all assessments');
      const response = await fetchWithErrorHandling(`${API_URL}/assessments`, {
        method: 'GET',
        credentials: 'include'
      });
      
      console.log('Assessments response:', response);
      
      if (response.success && response.assessments) {
        // Add _id field for frontend compatibility if not present
        const assessmentsWithId = response.assessments.map(assessment => {
          if (!assessment._id && assessment.id) {
            return { ...assessment, _id: assessment.id };
          }
          return assessment;
        });
        
        return { success: true, data: assessmentsWithId };
      } else {
        console.error('Invalid assessments response:', response);
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
      // Validate ID format before sending to backend
      if (!id) {
        throw new Error('Assessment ID is required');
      }
      
      // Try to convert numeric ID to string if needed
      const assessmentId = String(id);
      
      console.log(`Fetching assessment with ID: ${assessmentId}`);
      
      const response = await fetchWithErrorHandling(`${API_URL}/assessments/${assessmentId}`, {
        method: 'GET',
        credentials: 'include'
      });
      
      // The backend returns the assessment directly, not wrapped in an object
      if (response && Object.keys(response).length > 0) {
        // Check if we have a valid assessment object
        if (response.name) {
          // Ensure _id field exists
          if (!response._id && response.id) {
            response._id = response.id;
          }
          return { success: true, data: response };
        }
      }
      
      // If we get here, the response doesn't contain a valid assessment
      console.error('Invalid assessment data:', response);
      throw new Error(`Assessment with ID ${id} not found`);
    } catch (error) {
      // Handle specific error cases
      if (error.message && error.message.includes('ObjectId')) {
        console.error('Invalid ObjectId format:', error);
        // Try to recover by redirecting to assessments list
        return { 
          success: false, 
          error: 'Invalid assessment ID format', 
          redirect: true 
        };
      }
      
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
    try {
      // Input validation
      if (!file) {
        throw new Error('CSV file is required');
      }
      if (!rubric) {
        throw new Error('Rubric is required');
      }
      if (!assessmentName) {
        throw new Error('Assessment name is required');
      }

      // Log request details for debugging
      console.log('Uploading assessment:', { fileName: file.name, assessmentName });
      
      // Create a new FormData object
      const formData = new FormData();
      
      // Append the CSV file with explicit filename - exactly as curl does
      console.log('Appending CSV file:', file.name, file.type, file.size);
      formData.append('file', file, file.name);
      
      // Check if rubric is already a File object or Blob
      if (rubric instanceof File) {
        console.log('Appending rubric as File:', rubric.name, rubric.type, rubric.size);
        // Correct syntax: append(name, file, filename)
        formData.append('rubric', rubric, rubric.name);

        // Log the first few bytes of the file for debugging
        const reader = new FileReader();
        reader.onload = function(e) {
          const arrayBuffer = e.target.result;
          const bytes = new Uint8Array(arrayBuffer).slice(0, 100);
          console.log('First 100 bytes of rubric file:', Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join(' '));
        };
        reader.readAsArrayBuffer(rubric);
      } else if (rubric instanceof Blob) {
        console.log('Appending rubric as Blob');
        formData.append('rubric', rubric, 'rubric.json');
      } else {
        console.log('Converting rubric to Blob:', typeof rubric);
        const rubricBlob = new Blob([rubric], { type: 'text/plain' });
        formData.append('rubric', rubricBlob, 'rubric.txt');
      }
      
      console.log('Assessment name:', assessmentName);
      formData.append('name', assessmentName);
      
      // Log all form data entries for debugging
      console.log('FormData entries:');
      for (let [key, value] of formData.entries()) {
        if (value instanceof File || value instanceof Blob) {
          console.log(`${key}: ${value.name}, ${value.type}, ${value.size} bytes`);
        } else {
          console.log(`${key}: ${value}`);
        }
      }
      
      // Make the request with explicit headers
      const response = await fetchWithErrorHandling(`${API_URL}/upload_csv`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
        // Don't set Content-Type header - browser will set it with boundary
        headers: {
          // Let the browser set the Content-Type with boundary
          // 'Content-Type': 'multipart/form-data' - DO NOT SET THIS
        }
      });
      return response;
    } catch (error) {
      console.error('Error uploading CSV:', error);
      throw error;
    }
  },

  // Upload GitHub URL for assessment
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
  
  // Download Excel for assessment
  downloadExcel: async (assessmentId) => {
    try {
      console.log(`Downloading Excel for assessment: ${assessmentId}`);
      const response = await fetch(`${API_URL}/assessments/${assessmentId}/excel`, {
        method: 'GET',
        credentials: 'include',
        mode: 'cors',
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Excel download failed with status ${response.status}:`, errorText);
        throw new Error(`Failed to download Excel: ${response.status} ${errorText}`);
      }
      
      // Check if we got an Excel file
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('spreadsheetml')) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        // Get filename from Content-Disposition header or use default
        const contentDisposition = response.headers.get('content-disposition');
        const filename = contentDisposition && contentDisposition.includes('filename=') 
          ? contentDisposition.split('filename=')[1].replace(/"/g, '')
          : `assessment_${assessmentId}.xlsx`;
        
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        return { success: true, message: 'Excel file downloaded successfully' };
      } else {
        throw new Error('Server did not return an Excel file');
      }
    } catch (error) {
      console.error('Failed to download Excel:', error);
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
