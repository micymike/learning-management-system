import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { assessApi } from "../services/api";

const AssessmentDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedStudent, setSelectedStudent] = useState(null);

  // Fetch assessment details from the backend API
  useEffect(() => {
    const fetchAssessment = async () => {
      try {
        setLoading(true);
        const response = await assessApi.getAssessment(id);
        
        if (response.success && response.data) {
          setAssessment(response.data);
          setError(null);
        } else {
          setError('Failed to load assessment details');
        }
      } catch (err) {
        console.error('Error loading assessment:', err);
        setError(`Failed to load assessment: ${err.message || 'Unknown error'}`);
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchAssessment();
    }
  }, [id]);

  const handleDownloadExcel = async () => {
    try {
      setLoading(true);
      await assessApi.downloadExcel(id);
    } catch (err) {
      console.error('Error downloading Excel:', err);
      setError(`Failed to download Excel: ${err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleBackClick = () => {
    navigate('/');
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSelectedStudent(null);
  };

  const handleStudentClick = (student) => {
    setSelectedStudent(student);
    setActiveTab('student');
  };

  // Helper function to format score with max value (assuming scores are out of 5)
  const formatScore = (score) => {
    if (typeof score !== 'number') return 'N/A';
    return `${score}/5`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col justify-center items-center h-screen">
        <div className="text-red-500 text-xl mb-4">{error}</div>
        <button 
          onClick={handleBackClick}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="flex flex-col justify-center items-center h-screen">
        <div className="text-xl mb-4">Assessment not found</div>
        <button 
          onClick={handleBackClick}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  // Calculate statistics
  const students = assessment.results || [];
  const totalStudents = students.length;
  
  // Group students by their score ranges
  const scoreRanges = {
    'Excellent (90-100%)': 0,
    'Good (80-89%)': 0,
    'Satisfactory (70-79%)': 0,
    'Needs Improvement (60-69%)': 0,
    'Unsatisfactory (0-59%)': 0,
    'Pending': 0
  };

  students.forEach(student => {
    // Calculate average score if available
    if (student.scores && typeof student.scores === 'object') {
      const scores = Object.values(student.scores).filter(score => typeof score === 'number');
      if (scores.length > 0) {
        const avgScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        
        if (avgScore >= 90) scoreRanges['Excellent (90-100%)']++;
        else if (avgScore >= 80) scoreRanges['Good (80-89%)']++;
        else if (avgScore >= 70) scoreRanges['Satisfactory (70-79%)']++;
        else if (avgScore >= 60) scoreRanges['Needs Improvement (60-69%)']++;
        else scoreRanges['Unsatisfactory (0-59%)']++;
      } else {
        scoreRanges['Pending']++;
      }
    } else {
      scoreRanges['Pending']++;
    }
  });

  return (
    <div className="container mx-auto px-4 py-8 bg-white">
      <div className="flex justify-between items-center mb-6">
        <button 
          onClick={handleBackClick}
          className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 flex items-center"
        >
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
          </svg>
          Back
        </button>
        <button 
          onClick={handleDownloadExcel}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 flex items-center"
        >
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
          </svg>
          Download Excel
        </button>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-8">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">{assessment.name}</h1>
          <p className="text-gray-600 mb-4">
            Created: {new Date(assessment.created_at).toLocaleString()}
          </p>
          <div className="flex flex-wrap -mx-2">
            <div className="w-full md:w-1/3 px-2 mb-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">Total Students</h3>
                <p className="text-3xl font-bold text-blue-600">{totalStudents}</p>
              </div>
            </div>
            <div className="w-full md:w-2/3 px-2 mb-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">Score Distribution</h3>
                <div className="flex flex-wrap">
                  {Object.entries(scoreRanges).map(([range, count]) => (
                    count > 0 && (
                      <div key={range} className="mr-4 mb-2">
                        <span className="text-gray-700">{range}:</span>
                        <span className="ml-1 font-semibold">{count}</span>
                      </div>
                    )
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <div className="border-b">
          <div className="flex">
            <button 
              className={`px-6 py-3 font-medium ${activeTab === 'overview' ? 'text-blue-600 border-b-2 border-blue-500' : 'text-gray-600 hover:text-blue-500'}`}
              onClick={() => handleTabChange('overview')}
            >
              Overview
            </button>
            <button 
              className={`px-6 py-3 font-medium ${activeTab === 'students' ? 'text-blue-600 border-b-2 border-blue-500' : 'text-gray-600 hover:text-blue-500'}`}
              onClick={() => handleTabChange('students')}
            >
              Students
            </button>
            <button 
              className={`px-6 py-3 font-medium ${activeTab === 'rubric' ? 'text-blue-600 border-b-2 border-blue-500' : 'text-gray-600 hover:text-blue-500'}`}
              onClick={() => handleTabChange('rubric')}
            >
              Rubric
            </button>
            {selectedStudent && (
              <button 
                className={`px-6 py-3 font-medium ${activeTab === 'student' ? 'text-blue-600 border-b-2 border-blue-500' : 'text-gray-600 hover:text-blue-500'}`}
                onClick={() => setActiveTab('student')}
              >
                {selectedStudent.name}
              </button>
            )}
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Assessment Overview</h2>
              <p className="mb-4">This assessment contains results for {totalStudents} students.</p>
              
              <h3 className="text-lg font-semibold mb-2">Score Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {Object.entries(scoreRanges).map(([range, count]) => (
                  <div key={range} className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-700">{range}</h4>
                    <p className="text-2xl font-bold">{count}</p>
                    <p className="text-sm text-gray-500">
                      {totalStudents > 0 ? Math.round((count / totalStudents) * 100) : 0}% of students
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'students' && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Student Results</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Repository
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Criteria Scores
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Average
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {students.map((student, index) => {
                      // Calculate average score
                      let avgScore = 'N/A';
                      let status = 'Pending';
                      let criteriaScores = [];
                      
                      if (student.scores && typeof student.scores === 'object') {
                        criteriaScores = Object.entries(student.scores)
                          .filter(entry => typeof entry[1] === 'number')
                          .map(entry => ({ criterion: entry[0], score: entry[1] }));
                        
                        if (criteriaScores.length > 0) {
                          const avg = criteriaScores.reduce((sum, item) => sum + item.score, 0) / criteriaScores.length;
                          avgScore = avg.toFixed(1);
                          
                          if (avg >= 90) status = 'Excellent';
                          else if (avg >= 80) status = 'Good';
                          else if (avg >= 70) status = 'Satisfactory';
                          else if (avg >= 60) status = 'Needs Improvement';
                          else status = 'Unsatisfactory';
                        }
                      }
                      
                      return (
                        <tr 
                          key={index} 
                          className="hover:bg-gray-50 cursor-pointer"
                          onClick={() => handleStudentClick(student)}
                        >
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{student.name}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-500">
                              <a 
                                href={student.repo_url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-blue-500 hover:underline"
                                onClick={(e) => e.stopPropagation()}
                              >
                                {student.repo_url}
                              </a>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="text-sm text-gray-900">
                              {criteriaScores.length > 0 ? (
                                <div className="flex flex-col">
                                  {criteriaScores.slice(0, 3).map((item, i) => (
                                    <span key={i} className="mb-1">
                                      {item.criterion}: {formatScore(item.score)}
                                    </span>
                                  ))}
                                  {criteriaScores.length > 3 && (
                                    <span className="text-gray-500 text-xs">
                                      +{criteriaScores.length - 3} more criteria
                                    </span>
                                  )}
                                </div>
                              ) : (
                                'No criteria scores'
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{avgScore}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                              ${status === 'Excellent' ? 'bg-green-100 text-green-800' : 
                                status === 'Good' ? 'bg-blue-100 text-blue-800' : 
                                status === 'Satisfactory' ? 'bg-yellow-100 text-yellow-800' : 
                                status === 'Needs Improvement' ? 'bg-orange-100 text-orange-800' : 
                                status === 'Unsatisfactory' ? 'bg-red-100 text-red-800' : 
                                'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {status}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'rubric' && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Assessment Rubric</h2>
              <div className="bg-gray-50 p-4 rounded-lg">
                <pre className="whitespace-pre-wrap font-mono text-sm">
                  {assessment.rubric}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'student' && selectedStudent && (
            <div>
              <h2 className="text-xl font-semibold mb-4">{selectedStudent.name}</h2>
              
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-2">Repository</h3>
                <a 
                  href={selectedStudent.repo_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  {selectedStudent.repo_url}
                </a>
              </div>
              
              {selectedStudent.error ? (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
                  <h3 className="text-lg font-medium mb-2">Error</h3>
                  <p>{selectedStudent.error}</p>
                </div>
              ) : (
                <>
                  <div className="mb-6">
                    <h3 className="text-lg font-medium mb-2">Scores</h3>
                    {selectedStudent.scores && typeof selectedStudent.scores === 'object' ? (
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Criterion
                              </th>
                              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Score
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(selectedStudent.scores).map(([criterion, score], index) => (
                              <tr key={index}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {criterion}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {typeof score === 'number' ? formatScore(score) : 'N/A'}
                                </td>
                              </tr>
                            ))}
                            {/* Add average row at the bottom */}
                            {Object.values(selectedStudent.scores).some(score => typeof score === 'number') && (
                              <tr className="bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  Average
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {(() => {
                                    const scores = Object.values(selectedStudent.scores).filter(score => typeof score === 'number');
                                    if (scores.length === 0) return 'N/A';
                                    const avg = scores.reduce((sum, score) => sum + score, 0) / scores.length;
                                    return avg.toFixed(1);
                                  })()}
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="text-gray-500">No scores available</p>
                    )}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AssessmentDetails;
