import React, { useState } from "react";
import './ReportViewer.css';

const ReportViewer = ({ reports, scores, onScoresUpdate }) => {
  const [selectedScores, setSelectedScores] = useState([]);
  const [loading, setLoading] = useState(false);

  if ((!reports || reports.length === 0) && (!scores || scores.length === 0)) return null;

  const handleDownloadExcel = async () => {
    try {
      const response = await fetch('/download-scores', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) throw new Error('Failed to download scores');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'student_scores.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading scores:', error);
      alert('Failed to download scores. Please try again.');
    }
  };

  const handleDeleteScore = async (scoreId) => {
    try {
      setLoading(true);
      const response = await fetch(`/delete-score/${scoreId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to delete score');
      
      const data = await response.json();
      onScoresUpdate(data);
      setSelectedScores([]);
    } catch (error) {
      console.error('Error deleting score:', error);
      alert('Failed to delete score. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSelected = async () => {
    if (!selectedScores.length) return;
    
    try {
      setLoading(true);
      const response = await fetch('/delete-scores', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ score_ids: selectedScores }),
      });
      
      if (!response.ok) throw new Error('Failed to delete scores');
      
      const data = await response.json();
      onScoresUpdate(data);
      setSelectedScores([]);
    } catch (error) {
      console.error('Error deleting scores:', error);
      alert('Failed to delete selected scores. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = async () => {
    if (!confirm('Are you sure you want to clear all scores?')) return;
    
    try {
      setLoading(true);
      const response = await fetch('/clear-scores', {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to clear scores');
      
      const data = await response.json();
      onScoresUpdate(data);
      setSelectedScores([]);
    } catch (error) {
      console.error('Error clearing scores:', error);
      alert('Failed to clear scores. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectScore = (scoreId) => {
    setSelectedScores(prev => 
      prev.includes(scoreId)
        ? prev.filter(id => id !== scoreId)
        : [...prev, scoreId]
    );
  };

  const handleSelectAll = () => {
    setSelectedScores(
      selectedScores.length === scores.scores.length
        ? []
        : scores.scores.map(score => score.id)
    );
  };

  return (
    <div className="report-container animate-slidein">
      {scores && scores.scores && scores.scores.length > 0 && (
        <div className="scores-section">
          <div className="scores-header">
            <h2>Student Scores</h2>
            <div className="scores-actions">
              <button 
                onClick={handleDownloadExcel} 
                className="action-button download-button"
                disabled={loading}
              >
                <i className="fas fa-download"></i>
                Download Excel
              </button>
              <button 
                onClick={handleDeleteSelected} 
                className="action-button delete-button"
                disabled={loading || !selectedScores.length}
              >
                <i className="fas fa-trash"></i>
                Delete Selected ({selectedScores.length})
              </button>
              <button 
                onClick={handleClearAll} 
                className="action-button clear-button"
                disabled={loading}
              >
                <i className="fas fa-trash-alt"></i>
                Clear All
              </button>
            </div>
          </div>
          <div className="scores-table-container">
            <table className="scores-table">
              <thead>
                <tr>
                  <th>
                    <input 
                      type="checkbox"
                      checked={selectedScores.length === scores.scores.length}
                      onChange={handleSelectAll}
                    />
                  </th>
                  {Object.keys(scores.scores[0]).filter(key => key !== 'id').map(header => (
                    <th key={header}>{header}</th>
                  ))}
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {scores.scores.map(score => (
                  <tr key={score.id} className={selectedScores.includes(score.id) ? 'selected' : ''}>
                    <td>
                      <input 
                        type="checkbox"
                        checked={selectedScores.includes(score.id)}
                        onChange={() => handleSelectScore(score.id)}
                      />
                    </td>
                    {Object.entries(score)
                      .filter(([key]) => key !== 'id')
                      .map(([key, value]) => (
                        <td key={key}>{value}</td>
                      ))
                    }
                    <td>
                      <button 
                        onClick={() => handleDeleteScore(score.id)}
                        className="delete-icon"
                        disabled={loading}
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {reports && reports.map((r, idx) => (
        <div key={idx} className="report-card jungle-green-border">
          <div className="report-content">
            <div dangerouslySetInnerHTML={{ __html: window.marked ? window.marked.parse(r.report || r.assessment || r.result || "") : (r.report || r.assessment || r.result || "") }} />
          </div>
        </div>
      ))}
    </div>
  );
};

export default ReportViewer;
