import React, { useState } from "react";
import "./Dashboard.css";

const Dashboard = ({ onNewAssessment, onViewAssessment }) => {
  const [assessments, setAssessments] = useState(() => {
    // Load assessments from localStorage on component mount
    const savedAssessments = localStorage.getItem('savedAssessments');
    return savedAssessments ? JSON.parse(savedAssessments) : [];
  });
  const [loading] = useState(false);
  const [error] = useState(null);

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Code Assessment Dashboard</h1>
        <button 
          className="new-assessment-btn"
          onClick={onNewAssessment}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>New Assessment</span>
        </button>
      </div>

      {loading ? (
        <div className="loading-spinner">Loading assessments...</div>
      ) : error ? (
        <div className="error-message">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      ) : assessments.length === 0 ? (
        <div className="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#29AB87" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          <h2>No assessments yet</h2>
          <p>Create your first assessment by clicking the New Assessment button</p>
        </div>
      ) : (
        <div className="assessments-grid">
          {assessments.map((assessment, index) => (
            <div 
              key={index}
              className="assessment-card"
              onClick={() => onViewAssessment(assessment)}
            >
              <div className="assessment-card-header">
                <h3>{assessment.name || `Assessment ${index + 1}`}</h3>
                <span className="assessment-date">
                  {new Date(assessment.date).toLocaleDateString()}
                </span>
              </div>
              <div className="assessment-stats">
                <div className="stat">
                  <span className="stat-value">{assessment.results?.length || 0}</span>
                  <span className="stat-label">Students</span>
                </div>
                <div className="stat">
                  <span className="stat-value">
                    {assessment.rubric ? "✓" : "✗"}
                  </span>
                  <span className="stat-label">Rubric</span>
                </div>
              </div>
              <div className="view-details">View Details →</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
