import React, { useState } from "react";
import { AnimatePresence } from "framer-motion";
import * as XLSX from 'xlsx';
import { assessApi } from "../services/api";
import "./AssessmentWizard.css";

const steps = ["Define Rubric", "Upload Students", "View Results"];

const AssessmentWizard = ({ onComplete, onCancel }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [rubric, setRubric] = useState("");
  const [rubricFile, setRubricFile] = useState(null);
  const [csvFile, setCsvFile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [assessmentName, setAssessmentName] = useState("");
  const [error, setError] = useState("");

  const handleRubricTextChange = (e) => {
    setRubric(e.target.value);
  };

  const handleRubricFileChange = (e) => {
    setRubricFile(e.target.files[0]);
  };

  const handleCsvFileChange = (e) => {
    setCsvFile(e.target.files[0]);
  };

  const uploadRubric = async () => {
    if (!rubricFile && !rubric) {
      setError("Please provide a rubric file or define criteria manually");
      return false;
    }

    setLoading(true);
    setError("");

    try {
      if (rubricFile) {
        const data = await assessApi.uploadRubric(rubricFile);
        setRubric(data.result || data.rubric);
      }
      setLoading(false);
      return true;
    } catch (err) {
      console.error("Rubric upload error:", err);
      setError("Failed to upload rubric. Please try again.");
      setLoading(false);
      return false;
    }
  };

  const uploadCsvAndAssess = async () => {
    if (!csvFile) {
      setError("Please upload a CSV file with student information");
      return false;
    }

    setLoading(true);
    setError("");

    try {
      const assessment = {
        name: assessmentName || `Assessment ${new Date().toLocaleDateString()}`,
        date: new Date().toISOString(),
        rubric: rubric,
      };

      // Upload CSV and get results
      const data = await assessApi.uploadCSV(csvFile);
      if (data.results) {
        setResults(data.results);
        
        // Save to localStorage
        const assessmentData = {
          ...assessment,
          id: Date.now(),
          results: data.results
        };
        const savedAssessments = JSON.parse(localStorage.getItem('savedAssessments') || '[]');
        savedAssessments.push(assessmentData);
        localStorage.setItem('savedAssessments', JSON.stringify(savedAssessments));
        
        setLoading(false);
        return true;
      } else {
        throw new Error("Unexpected response from server");
      }
    } catch (err) {
      console.error("CSV upload error:", err);
      setError("Failed to upload CSV or assess students. Please try again.");
      setLoading(false);
      return false;
    }
  };

  const handleNext = async () => {
    if (currentStep === 0) {
      const success = await uploadRubric();
      if (success) setCurrentStep(1);
    } else if (currentStep === 1) {
      const success = await uploadCsvAndAssess();
      if (success) setCurrentStep(2);
    } else if (currentStep === 2) {
      onComplete(results);
    }
  };

  const handleDownloadReport = () => {
    if (!results || results.length === 0) return;

    // Prepare data for Excel sheet
    const reportData = results.map(result => ({
      Name: result.name,
      Repository: result.repo_url,
      Assessment: result.report || result.assessment,
    }));

    // Create worksheet
    const ws = XLSX.utils.json_to_sheet(reportData);

    // Create workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Assessment Results");

    // Generate Excel file and trigger download
    XLSX.writeFile(wb, `${assessmentName || 'assessment'}-report.xlsx`);
  };

  return (
    <div className="wizard-container">
      <div className="wizard-header">
        <h2>Create New Assessment</h2>
        <button className="close-btn" onClick={onCancel}>×</button>
      </div>

      <div className="wizard-progress">
        {steps.map((step, index) => (
          <div 
            key={index} 
            className={`progress-step ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''}`}
          >
            <div className="step-number">{index + 1}</div>
            <div className="step-label">{step}</div>
          </div>
        ))}
      </div>

      <div className="wizard-content">
        <AnimatePresence mode="wait">
          {currentStep === 0 && (
            <div key="step1" className="wizard-step">
              <div className="form-group">
                <label>Assessment Name</label>
                <input 
                  type="text" 
                  value={assessmentName} 
                  onChange={(e) => setAssessmentName(e.target.value)}
                  placeholder="e.g., Midterm Project Assessment"
                  className="input-field"
                />
              </div>
              
              <div className="form-group">
                <label>Upload Rubric File</label>
                <input 
                  type="file" 
                  accept=".txt,.md" 
                  onChange={handleRubricFileChange}
                  className="input-file"
                />
              </div>
              
              <div className="form-group">
                <label>Or Define Rubric Manually</label>
                <textarea 
                  rows={6} 
                  value={rubric} 
                  onChange={handleRubricTextChange}
                  placeholder="Define assessment criteria here..."
                  className="input-area"
                />
              </div>
            </div>
          )}

          {currentStep === 1 && (
            <div key="step2" className="wizard-step">
              <div className="rubric-preview">
                <h3>Assessment Rubric</h3>
                <pre>{rubric}</pre>
              </div>
              
              <div className="form-group">
                <label>Upload Students CSV</label>
                <input 
                  type="file" 
                  accept=".csv" 
                  onChange={handleCsvFileChange}
                  className="input-file"
                />
                <div className="help-text">
                  CSV should contain student names and GitHub repository URLs
                </div>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div key="step3" className="wizard-step">
              <div className="results-header">
                <h3>Assessment Results</h3>
                <div className="results-actions">
                  <button 
                    className="download-btn"
                    onClick={handleDownloadReport}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                      <polyline points="7 10 12 15 17 10"></polyline>
                      <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download Report (.xlsx)
                  </button>
                  <button 
                    className="next-btn finish-btn"
                    onClick={handleNext}
                    disabled={loading}
                  >
                    {loading ? (
                      <div className="loading-spinner-small"></div>
                    ) : (
                      "Finish"
                    )}
                  </button>
                </div>
              </div>
              
              <div className="results-list scrollable">
                {results.map((result, index) => (
                  <div 
                    key={index}
                    className="result-card"
                  >
                    <div className="result-header">
                      <h4>{result.name}</h4>
                      <a href={result.repo_url} target="_blank" rel="noopener noreferrer" className="repo-link">
                        View Repository
                      </a>
                    </div>
                    <div className="result-content">
                      <div dangerouslySetInnerHTML={{ 
                        __html: window.marked ? window.marked.parse(result.report || result.assessment) : (result.report || result.assessment) 
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </AnimatePresence>
      </div>

      {error && <div className="error-message">{error}</div>}

      {currentStep < 2 && (
        <div className="wizard-actions">
          {currentStep > 0 && (
            <button 
              className="back-btn"
              onClick={() => setCurrentStep(currentStep - 1)}
              disabled={loading}
            >
              Back
            </button>
          )}
          
          <button 
            className="next-btn"
            onClick={handleNext}
            disabled={loading}
          >
            {loading ? (
              <div className="loading-spinner-small"></div>
            ) : (
              "Next"
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default AssessmentWizard;
