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
        console.log(`Fetching assessment with ID: ${id}`);
        const response = await assessApi.getAssessment(id);
        
        if (response.success && response.data) {
          console.log('Assessment data received:', response.data);
          setAssessment(response.data);
          setError(null);
        } else if (response.redirect) {
          // Handle redirect case for invalid ID format
          console.warn('Invalid assessment ID, redirecting to dashboard');
          navigate('/');
          return;
        } else {
          console.error('Invalid response format:', response);
          setError('Failed to load assessment details: Invalid response format');
        }
      } catch (err) {
        console.error('Error loading assessment:', err);
        
        // Check if the error is related to ObjectId validation
        if (err.message && (
            err.message.includes('ObjectId') || 
            err.message.includes('not a valid') ||
            err.message.includes('400')
        )) {
          console.warn('Invalid assessment ID format, redirecting to dashboard');
          navigate('/');
          return;
        }
        
        setError(`Failed to load assessment: ${err.message || 'Unknown error'}`);
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchAssessment();
    } else {
      setError('No assessment ID provided');
    }
  }, [id, navigate]);

  const handleDownloadExcel = async () => {
    try {
      setLoading(true);
      console.log(`Downloading Excel for assessment ID: ${id}`);
      await assessApi.downloadExcel(id);
      console.log('Excel download completed successfully');
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

  // Helper function to format score with max value
  const formatScore = (score, maxPoints) => {
    if (typeof score === 'object' && score.mark !== undefined) {
      // If the mark already includes a format like "8.0/10.0", return it as is
      if (typeof score.mark === 'string' && score.mark.includes('/')) {
        return score.mark;
      }
      // Otherwise, format it with the maxPoints
      return `${score.mark}/${maxPoints}`;
    }
    if (typeof score !== 'number') return 'N/A';
    return `${score.toFixed(1)}/${maxPoints}`; // Include the max points from backend
  };

  // Helper function to determine if a score is a structured score object
  const isStructuredScore = (score) => {
    return typeof score === 'object' && score !== null && (score.mark !== undefined || score.justification !== undefined);
  };

  // Helper function to extract numeric value from mark range for calculations
  const getNumericValue = (score) => {
    // If score is already a number, return it directly without normalization
    if (typeof score === 'number') {
      return score;
    }
    
    if (typeof score === 'object' && score !== null && score.mark) {
      const mark = score.mark;
      
      if (typeof mark !== 'string') return 0;
      
      const markLower = mark.toLowerCase();
      
      // Extract numeric values from various formats
      
      // Check for fractions like "8.0/10.0" - extract just the first number
      const fractionWithDecimalMatch = markLower.match(/([\d.]+)\s*\/\s*[\d.]+/);
      if (fractionWithDecimalMatch) {
        return parseFloat(fractionWithDecimalMatch[1]);
      }
      
      // Check for percentage ranges (e.g., "90-100%")
      const percentRangeMatch = markLower.match(/(\d+)\s*-\s*(\d+)%/);
      if (percentRangeMatch) {
        const min = parseInt(percentRangeMatch[1]);
        const max = parseInt(percentRangeMatch[2]);
        return (min + max) / 2;
      }
      
      // Check for simple percentage (e.g., "90%")
      const percentMatch = markLower.match(/(\d+)%/);
      if (percentMatch) {
        return parseInt(percentMatch[1]);
      }
      
      // Check for ranges like "4-8 Marks"
      const rangeMatch = markLower.match(/(\d+)\s*-\s*(\d+)/);
      if (rangeMatch) {
        const min = parseInt(rangeMatch[1]);
        const max = parseInt(rangeMatch[2]);
        return (min + max) / 2;
      }
      
      // Check for fractions like "4/5" - don't convert to percentage
      const fractionMatch = markLower.match(/(\d+)\/(\d+)/);
      if (fractionMatch) {
        return parseInt(fractionMatch[1]);
      }
      
      // Check for single values like "0 (No Mark)" or "8.0"
      const decimalMatch = markLower.match(/([\d.]+)/);
      if (decimalMatch) {
        return parseFloat(decimalMatch[1]); // Return actual value
      }
    }
    
    return 0; // Default if we can't extract a numeric value
  };

  // Helper function to determine status based on mark
  const getStatusFromMark = (mark) => {
    if (typeof mark !== 'string') return 'Pending';
    
    // Convert to lowercase for case-insensitive matching
    const markLower = mark.toLowerCase();
    
    // Check for excellent/high scores
    if (markLower.includes('excellent') || 
        markLower.includes('fully correct') || 
        markLower.includes('10-12') || 
        markLower.includes('90-100%') || 
        markLower.includes('a+') || 
        markLower.includes('a grade') ||
        markLower.match(/\b[4-5]\/5\b/) ||
        markLower.match(/\b[9]\/10\b/) ||
        markLower.match(/\b10\/10\b/)) {
      return 'Excellent';
    }
    
    // Check for good scores
    if (markLower.includes('good') || 
        markLower.includes('mostly correct') || 
        markLower.includes('4-8') || 
        markLower.includes('80-89%') || 
        markLower.includes('b+') || 
        markLower.includes('b grade') ||
        markLower.match(/\b[3-4]\/5\b/) ||
        markLower.match(/\b[7-8]\/10\b/)) {
      return 'Good';
    }
    
    // Check for satisfactory scores
    if (markLower.includes('satisfactory') || 
        markLower.includes('70-79%') || 
        markLower.includes('c+') || 
        markLower.includes('c grade') ||
        markLower.match(/\b[2-3]\/5\b/) ||
        markLower.match(/\b[5-6]\/10\b/)) {
      return 'Satisfactory';
    }
    
    // Check for needs improvement scores
    if (markLower.includes('needs improvement') || 
        markLower.includes('partially correct') || 
        markLower.includes('1-3') || 
        markLower.includes('60-69%') || 
        markLower.includes('d+') || 
        markLower.includes('d grade') ||
        markLower.match(/\b[1-2]\/5\b/) ||
        markLower.match(/\b[3-4]\/10\b/)) {
      return 'Needs Improvement';
    }
    
    // Check for unsatisfactory scores
    if (markLower.includes('unsatisfactory') || 
        markLower.includes('fail') || 
        markLower.includes('incorrect') || 
        markLower.includes('no mark') || 
        markLower.includes('0-59%') || 
        markLower.includes('f grade') ||
        markLower.match(/\b[0-1]\/5\b/) ||
        markLower.match(/\b[0-2]\/10\b/) ||
        markLower === '0') {
      return 'Unsatisfactory';
    }
    
    // Default to pending if no match found
    return 'Pending';
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
          className="px-4 py-2 bg-blue-500 text-gray-700 rounded hover:bg-blue-600"
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
        <div className="text-gray-500 mb-4">ID: {id}</div>
        <button 
          onClick={handleBackClick}
          className="px-4 py-2 bg-blue-500 text-gray-700 rounded hover:bg-blue-600"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }
  
  // Log assessment data for debugging
  console.log('Rendering assessment:', assessment);

  // Calculate statistics
  const students = assessment.results || [];
  const totalStudents = students.length;
  
  // Get max points from first student result if available
  const maxPoints = students[0]?.assessment?.max_points || assessment.max_points || 100;
  
  // Group students by their percentage ranges
  const scoreRanges = {
    'Excellent': 0,
    'Good': 0,
    'Satisfactory': 0,
    'Needs Improvement': 0,
    'Unsatisfactory': 0,
    'Pending': 0
  };

  students.forEach(student => {
    // Calculate average score if available
    if (student.scores && typeof student.scores === 'object') {
      const scores = Object.values(student.scores).filter(score => typeof score === 'number' || isStructuredScore(score));
      if (scores.length > 0) {
        // Check if we have structured scores first
        const structuredScores = scores.filter(score => isStructuredScore(score));
        if (structuredScores.length > 0) {
          // Find the main criterion if it exists
          let mainCriterion = null;
          for (const [key, value] of Object.entries(student.scores)) {
            if (key.toLowerCase().includes('correctness') || key.toLowerCase().includes('main')) {
              mainCriterion = [key, value];
              break;
            }
          }
          
          if (mainCriterion && isStructuredScore(mainCriterion[1])) {
            // Use the main criterion's mark to determine status
            const mainStatus = getStatusFromMark(mainCriterion[1].mark);
            
            if (mainStatus === 'Excellent') scoreRanges['Excellent (90-100%)']++;
            else if (mainStatus === 'Good') scoreRanges['Good (80-89%)']++;
            else if (mainStatus === 'Satisfactory') scoreRanges['Satisfactory (70-79%)']++;
            else if (mainStatus === 'Needs Improvement') scoreRanges['Needs Improvement (60-69%)']++;
            else if (mainStatus === 'Unsatisfactory') scoreRanges['Unsatisfactory (0-59%)']++;
            else scoreRanges['Pending']++;
            
            // Skip the numeric calculation
            return;
          }
        }
        
        // Fall back to numeric calculation if no structured main criterion
        const avgScore = scores.reduce((sum, score) => sum + getNumericValue(score), 0) / scores.length;
        
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
    <div className="container mx-auto px-4 py-8 bg-gray-100">
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
          className="px-4 py-2 bg-green-500 text-gray-700 rounded hover:bg-green-600 flex items-center"
        >
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
          </svg>
          Download Excel
        </button>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-8">
        <div className="p-6">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-2xl font-bold text-gray-800">{assessment.name}</h1>
            <button
              onClick={async () => {
                if (!assessment._id && !assessment.id) {
                  alert("Assessment ID is missing or invalid. Cannot delete.");
                  return;
                }
                if (window.confirm("Are you sure you want to delete this assessment? This action cannot be undone.")) {
                  try {
                    const idToDelete = assessment._id || assessment.id;
                    if (!idToDelete) {
                      alert("Assessment ID is missing or invalid. Cannot delete.");
                      return;
                    }
                    await assessApi.deleteAssessment(idToDelete);
                    navigate('/');
                    return;
                  } catch (err) {
                    alert("Failed to delete assessment: " + (err.message || err));
                  }
                }
              }}
              className="ml-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              Delete Assessment
            </button>
          </div>
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
                          .filter(entry => typeof entry[1] === 'number' || isStructuredScore(entry[1]))
                          .map(entry => ({ criterion: entry[0], score: entry[1] }));
                        
                        if (criteriaScores.length > 0) {
                          // Check if we have structured scores first
                          const structuredScores = criteriaScores.filter(score => isStructuredScore(score));
                          if (structuredScores.length > 0) {
                            // Find the main criterion if it exists
                            let mainCriterion = null;
                            for (const [key, value] of Object.entries(student.scores)) {
                              if (key.toLowerCase().includes('correctness') || key.toLowerCase().includes('main')) {
                                mainCriterion = [key, value];
                                break;
                              }
                            }
                            
                            if (mainCriterion && isStructuredScore(mainCriterion[1])) {
                              // Use the main criterion's mark to determine status
                              status = getStatusFromMark(mainCriterion[1].mark);
                            }
                          }
                          
                          // Fall back to numeric calculation if no structured main criterion
                          const avg = criteriaScores.reduce((sum, item) => sum + getNumericValue(item.score), 0) / criteriaScores.length;
                          
                          // Store just the numeric value for status determination
                          avgScore = avg.toFixed(1);
                          
                          // Determine status based on score or mark
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
                              {/* Render new extracted_scores if present */}
                              {student.scores && Array.isArray(student.scores.extracted_scores) && student.scores.extracted_scores.length > 0 ? (
                                <div className="flex flex-col">
                                  {student.scores.extracted_scores
                                    .filter(scoreObj =>
                                      typeof scoreObj.context === "string" &&
                                      !/^\d+%$/.test(scoreObj.context.trim())
                                    )
                                    .slice(0, 3)
                                    .map((scoreObj, i) => (
                                      <span key={i} className="mb-1">
                                        {scoreObj.context}
                                        {typeof scoreObj.score === "number" && typeof scoreObj.max_score === "number" && (
                                          <span className="ml-2 text-xs text-gray-500">
                                            ({scoreObj.score}/{scoreObj.max_score} | {Math.round(scoreObj.percentage)}%)
                                          </span>
                                        )}
                                      </span>
                                    ))}
                                  {student.scores.extracted_scores.filter(scoreObj =>
                                    typeof scoreObj.context === "string" &&
                                    !/^\d+%$/.test(scoreObj.context.trim())
                                  ).length > 3 && (
                                    <span className="text-gray-500 text-xs">
                                      +{student.scores.extracted_scores.filter(scoreObj =>
                                        typeof scoreObj.context === "string" &&
                                        !/^\d+%$/.test(scoreObj.context.trim())
                                      ).length - 3} more criteria
                                    </span>
                                  )}
                                </div>
                              ) : (
                                'No criteria scores'
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {typeof avgScore === 'string' && avgScore !== 'N/A' 
                                ? `${avgScore}/${student.assessment?.max_points || maxPoints}` 
                                : avgScore}
                            </div>
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
                  {JSON.stringify(assessment.rubric, null, 2)}
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
                            {/* Render new extracted_scores if present */}
                            {selectedStudent.scores && Array.isArray(selectedStudent.scores.extracted_scores) && selectedStudent.scores.extracted_scores.length > 0 ? (
                              selectedStudent.scores.extracted_scores.map((scoreObj, index) => (
                                <tr key={index}>
                                  <td className="px-6 py-4 whitespace-normal text-sm text-gray-900">
                                    {scoreObj.context}
                                  </td>
                                  <td className="px-6 py-4 whitespace-normal text-sm">
                                    <div className="flex flex-col">
                                      {typeof scoreObj.score === "number" && typeof scoreObj.max_score === "number" ? (
                                        <span className="font-medium text-gray-900">
                                          {scoreObj.score}/{scoreObj.max_score} ({Math.round(scoreObj.percentage)}%)
                                        </span>
                                      ) : (
                                        <span className="text-gray-500">N/A</span>
                                      )}
                                    </div>
                                  </td>
                                </tr>
                              ))
                            ) : (
                              Object.entries(selectedStudent.scores).map(([criterion, score], index) => (
                                <tr key={index}>
                                  <td className="px-6 py-4 whitespace-normal text-sm text-gray-900">
                                    {criterion}
                                  </td>
                                  <td className="px-6 py-4 whitespace-normal text-sm">
                                    <div className="flex flex-col">
                                      <span className="font-medium text-gray-900">{formatScore(score, selectedStudent.assessment?.max_points || maxPoints)}</span>
                                      {isStructuredScore(score) && score.justification && (
                                        <span className="text-gray-600 text-xs mt-1 italic">
                                          {score.justification}
                                        </span>
                                      )}
                                    </div>
                                  </td>
                                </tr>
                              ))
                            )}
                            {/* Add average row at the bottom */}
                            {Object.values(selectedStudent.scores).some(score => typeof score === 'number' || isStructuredScore(score)) && (
                              <tr className="bg-gray-50">
                                <td className="px-6 py-4 whitespace-normal text-sm font-medium text-gray-900">
                                  Average
                                </td>
                                <td className="px-6 py-4 whitespace-normal text-sm font-medium text-gray-900">
                                  {(() => {
                                    const scores = Object.values(selectedStudent.scores).filter(score => typeof score === 'number' || isStructuredScore(score));
                                    if (scores.length === 0) return 'N/A';
                                    const avg = scores.reduce((sum, score) => sum + getNumericValue(score), 0) / scores.length;
                                    return `${avg.toFixed(1)}/${selectedStudent.assessment?.max_points || maxPoints}`;
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
