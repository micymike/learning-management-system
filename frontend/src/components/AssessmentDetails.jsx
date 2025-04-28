import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { assessApi } from "../services/api";
import "./AssessmentDetails.css";

const AssessmentDetails = ({ assessment, onBack }) => {
  const [activeTab, setActiveTab] = useState("results");
  const [currentAssessment, setCurrentAssessment] = useState(assessment);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Set the current assessment from props
  useEffect(() => {
    if (assessment) {
      setCurrentAssessment(assessment);
    }
  }, [assessment]);
  
  const handleDownloadReport = () => {
    const reportContent = currentAssessment.results.map(r => r.report || r.assessment).join('\n\n---\n\n');
    const blob = new Blob([reportContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentAssessment.name || 'assessment'}-report.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <motion.div 
      className="assessment-details"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="details-header">
        <button className="back-button" onClick={onBack}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Back
        </button>
        <h2>{currentAssessment.name}</h2>
        <div className="details-actions">
          <button 
            className="download-button" 
            onClick={handleDownloadReport}
            disabled={loading}
          >
            {loading ? (
              <div className="loading-spinner-small"></div>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Download Report
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          {error}
        </div>
      )}

      <div className="assessment-meta">
        <div className="meta-item">
          <span className="meta-label">Date</span>
          <span className="meta-value">{new Date(currentAssessment.date).toLocaleDateString()}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Students</span>
          <span className="meta-value">{currentAssessment.results?.length || 0}</span>
        </div>
      </div>

      <div className="details-tabs">
        <button 
          className={`tab-button ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          Results
        </button>
        <button 
          className={`tab-button ${activeTab === 'rubric' ? 'active' : ''}`}
          onClick={() => setActiveTab('rubric')}
        >
          Rubric
        </button>
      </div>

      <div className="details-content">
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading assessment data...</p>
          </div>
        ) : activeTab === 'results' && (
          <div className="results-grid">
            {currentAssessment.results && currentAssessment.results.length > 0 ? (
              currentAssessment.results.map((result, index) => (
                <motion.div 
                  key={index}
                  className="result-item"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div className="result-header">
                    <h3>{result.name}</h3>
                    <a 
                      href={result.repo_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="repo-link"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                      </svg>
                      Repository
                    </a>
                  </div>
                  <div className="result-content">
                    <div dangerouslySetInnerHTML={{ 
                      __html: window.marked ? window.marked.parse(result.report || result.assessment) : (result.report || result.assessment) 
                    }} />
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="empty-results">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <h3>No results available</h3>
                <p>This assessment doesn't have any student results yet.</p>
              </div>
            )}
          </div>
        )}

        {!loading && activeTab === 'rubric' && (
          <div className="rubric-content">
            <pre>{currentAssessment.rubric}</pre>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default AssessmentDetails;
