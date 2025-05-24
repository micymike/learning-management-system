import React, { useState } from 'react';
import UploadCSV from './UploadCSV';
import UploadRubric from './UploadRubric';
import RubricTemplates from './RubricTemplates';
import ReportViewer from './ReportViewer';
import './FormCard.css';

const AssessmentWizard = () => {
  const [step, setStep] = useState(1);
  const [assessmentName, setAssessmentName] = useState('');
  const [csvFile, setCsvFile] = useState(null);
  const [rubric, setRubric] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [useTemplate, setUseTemplate] = useState(false);

  const handleCsvUpload = (file) => {
    setCsvFile(file);
    setStep(2);
  };

  const handleRubricUpload = (rubricContent) => {
    setRubric(rubricContent);
    setStep(3);
  };

  const handleTemplateSelect = (rubricContent) => {
    setRubric(rubricContent);
    setStep(3);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!csvFile || !rubric) {
      setError('Please upload both a CSV file and a rubric.');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', csvFile);
    formData.append('name', assessmentName);

    // Create a blob from the rubric text and append it as a file
    const rubricBlob = new Blob([rubric], { type: 'text/plain' });
    formData.append('rubric', rubricBlob, 'rubric.txt');

    try {
      const response = await fetch('/upload_csv', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setResults(data.results);
        setStep(4);
      }
    } catch (err) {
      setError('Failed to process assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="assessment-wizard">
      <h1>Assessment Wizard</h1>
      
      {step === 1 && (
        <div className="step-container">
          <h2>Step 1: Upload Student Data</h2>
          <UploadCSV onCsvUpload={handleCsvUpload} />
        </div>
      )}

      {step === 2 && (
        <div className="step-container">
          <h2>Step 2: Select Rubric</h2>
          
          <div className="rubric-options">
            <div className="option-buttons">
              <button 
                className={`option-btn ${!useTemplate ? 'active' : ''}`}
                onClick={() => setUseTemplate(false)}
              >
                Upload Rubric
              </button>
              <button 
                className={`option-btn ${useTemplate ? 'active' : ''}`}
                onClick={() => setUseTemplate(true)}
              >
                Use Template
              </button>
            </div>
            
            {useTemplate ? (
              <RubricTemplates onSelectRubric={handleTemplateSelect} />
            ) : (
              <UploadRubric onRubric={handleRubricUpload} />
            )}
          </div>
          
          <div className="navigation-buttons">
            <button className="back-btn" onClick={() => setStep(1)}>Back</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="step-container">
          <h2>Step 3: Assessment Details</h2>
          <div className="form-card">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="assessmentName">Assessment Name:</label>
                <input
                  type="text"
                  id="assessmentName"
                  value={assessmentName}
                  onChange={(e) => setAssessmentName(e.target.value)}
                  placeholder="Enter assessment name"
                />
              </div>
              
              <div className="form-summary">
                <h3>Summary</h3>
                <p><strong>CSV File:</strong> {csvFile?.name || 'Not uploaded'}</p>
                <p><strong>Rubric:</strong> {rubric ? 'Uploaded' : 'Not uploaded'}</p>
              </div>
              
              <div className="button-group">
                <button type="button" className="back-btn" onClick={() => setStep(2)}>
                  Back
                </button>
                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? 'Processing...' : 'Run Assessment'}
                </button>
              </div>
            </form>
            {error && <div className="error-msg">{error}</div>}
          </div>
        </div>
      )}

      {step === 4 && results && (
        <div className="step-container">
          <h2>Step 4: Assessment Results</h2>
          <ReportViewer results={results} />
          <button className="new-assessment-btn" onClick={() => {
            setStep(1);
            setCsvFile(null);
            setRubric(null);
            setResults(null);
            setAssessmentName('');
          }}>
            Start New Assessment
          </button>
        </div>
      )}
    </div>
  );
};

export default AssessmentWizard;