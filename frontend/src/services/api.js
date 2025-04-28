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
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API error: ${response.status}`);
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
  // Assess code with rubric
  assess: (code, rubric) => {
    const formData = createFormData({ code, rubric });
    return fetchWithErrorHandling(`${API_URL}/assess`, {
      method: 'POST',
      body: formData,
    });
  },

  // Upload and process CSV file with student data
  uploadCSV: (file) => {
    const formData = createFormData({ file });
    return fetchWithErrorHandling(`${API_URL}/upload_csv`, {
      method: 'POST',
      body: formData,
    });
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
