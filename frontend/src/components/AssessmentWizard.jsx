import React, { useState } from "react";
import { AnimatePresence } from "framer-motion";
import { assessApi } from "../services/api"; // Import assessApi
import { useNavigate } from "react-router-dom";

const steps = ["Define Rubric", "Upload Students", "View Results"];

const AssessmentWizard = ({ onComplete, onCancel }) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [rubric, setRubric] = useState("");
  const [rubricFile, setRubricFile] = useState(null);
  const [csvFile, setCsvFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [assessmentName, setAssessmentName] = useState("");
  const [rubricText, setRubricText] = useState("");
  const [error, setError] = useState("");
  const [results, setResults] = useState([]);
  const [isAuthenticated] = useState(true);
  const [createdAssessment, setCreatedAssessment] = useState(null);

  const handleRubricTextChange = (e) => {
    const value = e?.target?.value ?? "";
    setRubric(value);
    setRubricText(value);
  };

  const handleRubricFileChange = (e) => {
    const file = e?.target?.files?.[0] || null;
    setRubricFile(file);
    // Clear text input if file is selected
    if (file) {
      setRubric("");
      setRubricText("");
    }
  };

  const handleCsvFileChange = (e) => {
    const file = e?.target?.files?.[0] || null;
    setCsvFile(file);
  };

  const uploadRubric = async () => {
    // Validate assessment name
    if (!assessmentName.trim()) {
      setError("Please provide an assessment name");
      return;
    }

    // Validate rubric
    if (!rubric && !rubricFile) {
      setError("Please provide a rubric text or upload a rubric file");
      return;
    }

    setLoading(true);
    setError("");

    try {
      if (!isAuthenticated) {
        setError("Authentication required. Please log in to continue.");
        setLoading(false);
        return;
      }

      // If we have a rubric file, we'll read it in the next step
      // No need to do anything else here, just proceed to the next step
      setCurrentStep(1);
    } catch (err) {
      console.error("Error uploading rubric:", err);
      setError("Failed to process rubric. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const processCSV = async () => {
    if (!csvFile) {
      setError("Please upload a CSV file with student data");
      return;
    }

    if (!rubric && !rubricFile) {
      setError("Please provide a rubric");
      return;
    }

    setLoading(true);
    setError("");

    try {
      if (!isAuthenticated) {
        setError("Authentication required. Please log in to continue.");
        setLoading(false);
        return;
      }

      // Prepare rubric data
      let rubricContent = rubric;
      
      // If a file was uploaded, use the file directly instead of reading as text
      if (rubricFile) {
        // Pass the actual file object to the API
        rubricContent = rubricFile;
      }

      // Process the CSV file with the API
      const response = await assessApi.uploadCSV(csvFile, rubricContent, assessmentName);
      
      if (response.success) {
        setResults(response.results || []);
        
        // Store the created assessment
        if (response.assessment) {
          setCreatedAssessment(response.assessment);
        }
        
        setCurrentStep(2);
      } else {
        setError(response.error || "Failed to process CSV file");
      }
    } catch (err) {
      console.error("Error processing CSV:", err);
      setError(err.message || "Failed to process CSV file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentStep === 0) {
      uploadRubric();
    } else if (currentStep === 1) {
      processCSV();
    } else if (currentStep === 2) {
      if (createdAssessment && createdAssessment.id) {
        // Navigate to the assessment details page
        navigate(`/assessments/${createdAssessment.id}`);
      } else {
        // Fallback to onComplete if provided
        onComplete && onComplete(results);
      }
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else {
      onCancel && onCancel();
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div>
              <label htmlFor="assessment-name" className="block text-sm font-medium text-gray-700 mb-1">
                Assessment Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="assessment-name"
                value={assessmentName}
                onChange={(e) => setAssessmentName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                placeholder="e.g., Midterm Project Assessment"
                required
              />
            </div>
            
            <div>
              <label htmlFor="rubric-text" className="block text-sm font-medium text-gray-700 mb-1">
                Rubric Criteria <span className="text-red-500">*</span>
              </label>
              <textarea
                id="rubric-text"
                value={rubricText}
                onChange={handleRubricTextChange}
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                placeholder="Enter rubric criteria, one per line. For example:&#10;Code quality and organization&#10;Documentation and comments&#10;Proper use of version control&#10;Implementation of required features&#10;Testing and error handling"
                required={!rubricFile}
              />
            </div>
            
            <div className="text-center border-t border-b border-gray-200 py-2 my-4">
              <span className="px-2 bg-white text-sm text-gray-500">OR</span>
            </div>
            
            <div>
              <label htmlFor="rubric-file" className="block text-sm font-medium text-gray-700 mb-1">
                Upload Rubric File
              </label>
              <input
                type="file"
                id="rubric-file"
                onChange={handleRubricFileChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                accept=".txt,.md,.docx,.xlsx"
              />
              <p className="mt-1 text-xs text-gray-500">
                Supported formats: .txt, .md, .docx, .xlsx
              </p>
            </div>
          </div>
        );
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <label htmlFor="csv-file" className="block text-sm font-medium text-gray-700 mb-1">
                Upload Student Data (CSV) <span className="text-red-500">*</span>
              </label>
              <input
                type="file"
                id="csv-file"
                onChange={handleCsvFileChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                accept=".csv,.xlsx,.txt"
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                Supported formats: .csv, .xlsx, .txt
              </p>
              <p className="mt-2 text-sm text-gray-600">
                CSV file should contain at minimum: student name and GitHub repository URL.
              </p>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-md border border-blue-200">
              <h3 className="text-sm font-medium text-blue-800 mb-2">CSV Format Example</h3>
              <pre className="text-xs text-blue-700 bg-blue-100 p-2 rounded overflow-x-auto">
                name,repo_url<br/>
                John Doe,https://github.com/johndoe/project<br/>
                Jane Smith,https://github.com/janesmith/assignment
              </pre>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="space-y-6">
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">Assessment Created Successfully</h3>
                
                <button
                  type="button"
                  onClick={() => {
                    // Download Excel functionality would go here
                    // For now, just log
                    console.log("Download Excel clicked");
                  }}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  Download Excel
                </button>
              </div>
              
              <div className="bg-green-50 p-4 rounded-md border border-green-200 mb-6">
                <div className="flex">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-400 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <p className="text-sm text-green-700">
                    Assessment "{createdAssessment?.name || assessmentName}" has been created successfully. Click "Finish" to view the assessment details.
                  </p>
                </div>
              </div>
              
              <h3 className="text-lg font-medium text-gray-900">Student Submissions</h3>
              
              {results.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No results available yet</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Student
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Repository
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {results.map((result, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {result.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <a href={result.repo_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800">
                              {result.repo_url}
                            </a>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                              {result.status || 'Pending'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-white min-h-screen p-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Create Assessment</h2>
          <button
            type="button"
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={index} className="flex items-center">
                <div className={`flex items-center justify-center h-8 w-8 rounded-full ${
                  index < currentStep ? 'bg-green-600' : index === currentStep ? 'bg-green-500' : 'bg-gray-300'
                } text-white text-sm font-medium`}>
                  {index < currentStep ? (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    index + 1
                  )}
                </div>
                <span className={`ml-2 text-sm ${
                  index <= currentStep ? 'text-gray-900 font-medium' : 'text-gray-500'
                }`}>
                  {step}
                </span>
                {index < steps.length - 1 && (
                  <div className={`h-0.5 w-12 mx-2 ${
                    index < currentStep ? 'bg-green-600' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-400 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}
        
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6 mb-6">
          {renderStepContent()}
        </div>
        
        <div className="flex justify-between">
          <button
            type="button"
            onClick={handleBack}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            {currentStep === 0 ? 'Cancel' : 'Back'}
          </button>
          <button
            type="button"
            onClick={handleNext}
            disabled={loading}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
              loading ? 'bg-green-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
            }`}
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : currentStep === steps.length - 1 ? (
              'Finish'
            ) : (
              'Next'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AssessmentWizard;
