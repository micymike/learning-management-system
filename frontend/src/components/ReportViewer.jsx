import React from 'react';
import './ReportViewer.css';

const ReportViewer = ({ results }) => {
  if (!results || results.length === 0) {
    return <div className="report-empty">No results to display</div>;
  }

  // Function to determine if a student passed based on the 80% threshold
  const isPassing = (result) => {
    if (result.assessment && typeof result.assessment.passing === 'boolean') {
      return result.assessment.passing;
    }
    
    // Legacy format
    if (result.scores) {
      const scores = Object.values(result.scores).filter(score => 
        typeof score === 'number' || 
        (typeof score === 'object' && typeof score.mark === 'number')
      );
      
      if (scores.length === 0) return false;
      
      const total = scores.reduce((sum, score) => 
        sum + (typeof score === 'number' ? score : score.mark), 0);
      const average = total / scores.length;
      
      return average >= 8; // Assuming 10-point scale with 80% passing
    }
    
    return false;
  };

  // Function to get the percentage score
  const getPercentage = (result) => {
    if (result.assessment && typeof result.assessment.percentage === 'number') {
      return result.assessment.percentage.toFixed(1) + '%';
    }
    
    // Legacy format
    if (result.scores) {
      const scores = Object.values(result.scores).filter(score => 
        typeof score === 'number' || 
        (typeof score === 'object' && typeof score.mark === 'number')
      );
      
      if (scores.length === 0) return 'N/A';
      
      const total = scores.reduce((sum, score) => 
        sum + (typeof score === 'number' ? score : score.mark), 0);
      const average = total / scores.length;
      
      return ((average / 10) * 100).toFixed(1) + '%'; // Assuming 10-point scale
    }
    
    return 'N/A';
  };

  return (
    <div className="report-container">
      <h2>Assessment Results</h2>
      <div className="report-summary">
        <p><strong>Total Students:</strong> {results.length}</p>
        <p><strong>Passing:</strong> {results.filter(r => isPassing(r)).length}</p>
        <p><strong>Failing:</strong> {results.filter(r => !isPassing(r)).length}</p>
      </div>
      
      <table className="report-table">
        <thead>
          <tr>
            <th>Student</th>
            <th>Repository</th>
            <th>Points</th>
            <th>Percentage</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result, index) => (
            <tr key={index} className={isPassing(result) ? 'passing' : 'failing'}>
              <td>{result.name}</td>
              <td>
                <a href={result.repo_url} target="_blank" rel="noopener noreferrer">
                  {result.repo_url.replace('https://github.com/', '')}
                </a>
              </td>
              <td>
                {result.assessment ? 
                  `${result.assessment.total_points}/${result.assessment.max_points}` : 
                  'N/A'}
              </td>
              <td>{getPercentage(result)}</td>
              <td className={isPassing(result) ? 'status-pass' : 'status-fail'}>
                {isPassing(result) ? 'PASS' : 'FAIL'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      <div className="detailed-results">
        <h3>Detailed Assessments</h3>
        {results.map((result, index) => (
          <div key={index} className="student-result">
            <h4>{result.name}</h4>
            <p><strong>Repository:</strong> <a href={result.repo_url} target="_blank" rel="noopener noreferrer">{result.repo_url}</a></p>
            
            {result.assessment && result.assessment.criteria_scores ? (
              <div className="criteria-scores">
                <h5>Criteria Scores:</h5>
                <table>
                  <thead>
                    <tr>
                      <th>Criterion</th>
                      <th>Points</th>
                      <th>Justification</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(result.assessment.criteria_scores).map(([criterion, data], i) => (
                      <tr key={i}>
                        <td>{criterion}</td>
                        <td>{data.points}/{data.max_points}</td>
                        <td>{data.justification || 'No justification provided'}</td>
                      </tr>
                    ))}
                    <tr className="total-row">
                      <td><strong>Total</strong></td>
                      <td><strong>{result.assessment.total_points}/{result.assessment.max_points}</strong></td>
                      <td>
                        <strong>
                          {result.assessment.percentage}% - 
                          {result.assessment.passing ? 'PASS' : 'FAIL'}
                        </strong>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            ) : result.scores ? (
              <div className="legacy-scores">
                <h5>Scores:</h5>
                <ul>
                  {Object.entries(result.scores).map(([criterion, score], i) => (
                    <li key={i}>
                      <strong>{criterion}:</strong> {
                        typeof score === 'object' ? 
                          `${score.mark} - ${score.justification || 'No justification'}` : 
                          score
                      }
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <p>No detailed scores available</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReportViewer;