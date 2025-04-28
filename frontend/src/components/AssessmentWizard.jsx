import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
    const reportContent = results.map(r => r.report || r.assessment).join('\n\n---\n\n');
    const blob = new Blob([reportContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${assessmentName || 'assessment'}-report.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <motion.div 
      className="wizard-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
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
            <motion.div 
              key="step1"
              className="wizard-step"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
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
            </motion.div>
          )}

          {currentStep === 1 && (
            <motion.div 
              key="step2"
              className="wizard-step"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
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
            </motion.div>
          )}

          {currentStep === 2 && (
            <motion.div 
              key="step3"
              className="wizard-step"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="results-header">
                <h3>Assessment Results</h3>
                <button 
                  className="download-btn"
                  onClick={handleDownloadReport}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  Download Report
                </button>
              </div>
              
              <div className="results-list">
                {results.map((result, index) => (
                  <motion.div 
                    key={index}
                    className="result-card"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
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
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {error && <div className="error-message">{error}</div>}

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
          ) : currentStep === steps.length - 1 ? (
            "Finish"
          ) : (
            "Next"
          )}
        </button>
      </div>
    </motion.div>
  );
};

export default AssessmentWizard;
