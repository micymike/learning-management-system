import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assessApi } from '../services/api';

const StudentDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchStudentDetails = async () => {
      try {
        setLoading(true);
        const response = await assessApi.getStudent(id);
        if (response.success) {
          setStudent(response.student);
        } else {
          setError('Failed to fetch student details');
        }
      } catch (error) {
        console.error('Error fetching student details:', error);
        setError('Failed to fetch student details: ' + error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStudentDetails();
  }, [id]);

  const handleBack = () => {
    navigate('/students');
  };

  // Helper function to format score
  const formatScore = (score) => {
    if (typeof score === 'object' && score !== null) {
      if (score.mark) {
        return score.mark; // Return the mark from structured score
      }
      return 'N/A'; // Invalid object format
    }
    if (typeof score === 'number') {
      return `${score}/5`; // Legacy format
    }
    return 'N/A'; // Fallback
  };

  // Helper function to extract numeric value for calculations
  const getNumericValue = (score) => {
    if (typeof score === 'number') {
      return score;
    }
    
    if (typeof score === 'object' && score !== null && score.mark) {
      const mark = score.mark;
      // Try to extract numeric values from mark ranges like "4 - 8 Marks"
      if (typeof mark === 'string') {
        // Check for ranges like "4 - 8 Marks"
        const rangeMatch = mark.match(/(\d+)\s*-\s*(\d+)/);
        if (rangeMatch) {
          // Use the average of the range
          return (parseInt(rangeMatch[1]) + parseInt(rangeMatch[2])) / 2;
        }
        
        // Check for single values like "0 (No Mark)"
        const singleMatch = mark.match(/(\d+)/);
        if (singleMatch) {
          return parseInt(singleMatch[1]);
        }
      }
    }
    
    return 0; // Default if we can't extract a numeric value
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 text-red-700 rounded-md">
        <h2 className="text-xl font-bold">Error</h2>
        <p>{error}</p>
        <button 
          onClick={handleBack} 
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Back to Students
        </button>
      </div>
    );
  }

  if (!student) {
    return (
      <div className="p-4 bg-yellow-100 text-yellow-700 rounded-md">
        <h2 className="text-xl font-bold">Student Not Found</h2>
        <p>The requested student could not be found.</p>
        <button 
          onClick={handleBack} 
          className="mt-2 px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
        >
          Back to Students
        </button>
      </div>
    );
  }

  // Sort assessments by date (newest first)
  const sortedAssessments = [...(student.assessments || [])].sort((a, b) => {
    return new Date(b.created_at) - new Date(a.created_at);
  });

  // Get all unique criteria across all assessments
  const allCriteria = new Set();
  sortedAssessments.forEach(assessment => {
    if (assessment.scores) {
      Object.keys(assessment.scores).forEach(criterion => {
        allCriteria.add(criterion);
      });
    }
  });
  const criteriaList = Array.from(allCriteria);

  // Calculate progress over time for each criterion
  const progressData = criteriaList.map(criterion => {
    const scores = sortedAssessments
      .filter(a => a.scores && (typeof a.scores[criterion] === 'number' || 
                               (typeof a.scores[criterion] === 'object' && a.scores[criterion] !== null)))
      .map(a => ({
        assessment_name: a.assessment_name,
        score: a.scores[criterion],
        numeric_value: getNumericValue(a.scores[criterion]),
        date: new Date(a.created_at)
      }))
      .sort((a, b) => a.date - b.date); // Sort by date ascending for progress view
    
    return {
      criterion,
      scores
    };
  });

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <button 
          onClick={handleBack}
          className="flex items-center text-green-600 hover:text-green-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          Back to Students
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 border-b">
          <div className="flex items-center">
            <div className="flex-shrink-0 h-16 w-16 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 text-xl font-medium">
                {student.name.split(' ').map(n => n[0]).join('')}
              </span>
            </div>
            <div className="ml-6">
              <h1 className="text-2xl font-bold">{student.name}</h1>
              {student.email && <p className="text-gray-600">{student.email}</p>}
              {student.github_username && (
                <a 
                  href={`https://github.com/${student.github_username}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800"
                >
                  @{student.github_username}
                </a>
              )}
            </div>
          </div>
        </div>

        <div className="border-b">
          <nav className="flex">
            <button
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'overview' 
                  ? 'border-b-2 border-green-500 text-green-600' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'assessments' 
                  ? 'border-b-2 border-green-500 text-green-600' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab('assessments')}
            >
              Assessments
            </button>
            <button
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'progress' 
                  ? 'border-b-2 border-green-500 text-green-600' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab('progress')}
            >
              Progress
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500 uppercase">Total Assessments</h3>
                  <p className="mt-1 text-3xl font-semibold text-gray-900">{sortedAssessments.length}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500 uppercase">Latest Score</h3>
                  <p className="mt-1 text-3xl font-semibold text-gray-900">
                    {sortedAssessments.length > 0 
                      ? formatScore(sortedAssessments[0].average_score) 
                      : 'N/A'}
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-500 uppercase">Latest Assessment</h3>
                  <p className="mt-1 text-lg font-semibold text-gray-900">
                    {sortedAssessments.length > 0 
                      ? sortedAssessments[0].assessment_name 
                      : 'N/A'}
                  </p>
                </div>
              </div>

              {sortedAssessments.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Latest Assessment Scores</h3>
                  <div className="bg-white rounded-lg border overflow-hidden">
                    {Object.entries(sortedAssessments[0].scores || {}).map(([criterion, score]) => (
                      <div key={criterion} className="flex justify-between p-3 border-b last:border-b-0">
                        <span className="font-medium">{criterion}</span>
                        <span className="text-gray-700">{formatScore(score)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'assessments' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">Assessment History</h3>
              {sortedAssessments.length === 0 ? (
                <p className="text-gray-500">No assessments found for this student.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Assessment
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Average Score
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Details
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {sortedAssessments.map((assessment) => (
                        <tr key={assessment.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{assessment.assessment_name}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-500">
                              {new Date(assessment.created_at).toLocaleDateString()}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{formatScore(assessment.average_score)}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button 
                              onClick={() => navigate(`/assessments/${assessment.assessment_id}`)}
                              className="text-green-600 hover:text-green-900"
                            >
                              View Assessment
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'progress' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">Progress Over Time</h3>
              {progressData.length === 0 ? (
                <p className="text-gray-500">No progress data available.</p>
              ) : (
                <div className="space-y-6">
                  {progressData.map(({ criterion, scores }) => (
                    <div key={criterion} className="bg-white rounded-lg border overflow-hidden">
                      <div className="p-4 border-b bg-gray-50">
                        <h4 className="font-medium">{criterion}</h4>
                      </div>
                      <div className="p-4">
                        {scores.length < 2 ? (
                          <p className="text-gray-500">Need more assessments to show progress.</p>
                        ) : (
                          <div>
                            <div className="relative h-16">
                              {/* Progress line */}
                              <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-200"></div>
                              
                              {/* Score points */}
                              {scores.map((score, index) => {
                                const position = `${(index / (scores.length - 1)) * 100}%`;
                                return (
                                  <div 
                                    key={index}
                                    className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 flex flex-col items-center"
                                    style={{ left: position }}
                                  >
                                    <div 
                                      className={`w-4 h-4 rounded-full ${
                                        index === scores.length - 1 
                                          ? 'bg-green-500' 
                                          : index === 0 
                                            ? 'bg-blue-500' 
                                            : 'bg-gray-400'
                                      }`}
                                    ></div>
                                    <div className="mt-1 text-xs font-medium">
                                      {formatScore(score.score)}
                                    </div>
                                    <div className="text-xs text-gray-500">
                                      {new Date(score.date).toLocaleDateString()}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                            
                            <div className="mt-8 flex justify-between text-xs text-gray-500">
                              <div>First: {scores[0].assessment_name}</div>
                              <div>Latest: {scores[scores.length - 1].assessment_name}</div>
                            </div>
                            
                            <div className="mt-2">
                              <p className="text-sm">
                                {scores[scores.length - 1].numeric_value > scores[0].numeric_value
                                  ? `Improved by ${(scores[scores.length - 1].numeric_value - scores[0].numeric_value).toFixed(1)} points`
                                  : scores[scores.length - 1].numeric_value < scores[0].numeric_value
                                    ? `Decreased by ${(scores[0].numeric_value - scores[scores.length - 1].numeric_value).toFixed(1)} points`
                                    : 'No change in score'}
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentDetails;
