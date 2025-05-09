import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from './Sidebar';
import { assessApi } from "../services/api";

const Dashboard = ({ activeView = "dashboard", onNewAssessment, onViewAssessment }) => {
  const navigate = useNavigate();
  
  // Use state for assessments
  const [assessments, setAssessments] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showStudentsModal, setShowStudentsModal] = useState(false);
  const [studentStats, setStudentStats] = useState({
    total: 0,
    groups: {},
    projects: {},
    students: []
  });

  // Load assessments from the backend API
  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        setLoading(true);
        const response = await assessApi.getAssessments();
        
        if (response.success && response.data) {
          setAssessments(response.data);
          setError(null);
        } else {
          setError("Failed to load assessments");
        }
      } catch (err) {
        console.error("Error loading assessments:", err);
        setError("Failed to load assessment data. " + (err.message || ""));
      } finally {
        setLoading(false);
      }
    };
    
    fetchAssessments();
  }, [activeView]); // Reload when activeView changes

  // Calculate student statistics from assessments
  useEffect(() => {
    try {
      if (assessments && assessments.length > 0) {
        const stats = { 
          total: 0, 
          groups: {}, 
          projects: {}, 
          students: [] 
        };
        
        // Track unique student names to avoid duplicates
        const uniqueStudentNames = new Set();
        
        assessments.forEach(assessment => {
          if (assessment.results && assessment.results.length > 0) {
            assessment.results.forEach(student => {
              // Only count and add unique students
              if (!uniqueStudentNames.has(student.name)) {
                uniqueStudentNames.add(student.name);
                
                // Add to students array
                stats.students.push({
                  name: student.name,
                  github: student.github || '',
                  group: student.group || 'Unassigned',
                  project: assessment.name || 'Unnamed Project',
                  score: student.score || 0
                });
                
                // Count groups
                const group = student.group || 'Unassigned';
                stats.groups[group] = (stats.groups[group] || 0) + 1;
                
                // Count projects
                const project = assessment.name || 'Unnamed Project';
                stats.projects[project] = (stats.projects[project] || 0) + 1;
              }
            });
          }
        });
        
        // Set total to the number of unique students
        stats.total = uniqueStudentNames.size;
        
        setStudentStats(stats);
      }
      setLoading(false);
    } catch (err) {
      console.error("Error processing assessments:", err);
      setError("Failed to load assessment data");
      setLoading(false);
    }
  }, [assessments]);

  // Function to add a new assessment
  const handleAddAssessment = () => {
    if (onNewAssessment) {
      onNewAssessment();
    } else {
      navigate('/assessments/new');
    }
  };

  const handleSidebarItemClick = (section) => {
    if (section === "new-assessment") {
      handleAddAssessment();
    } else if (section === "previous-assessments") {
      navigate('/assessments');
    } else if (section === "student-stats") {
      setShowStudentsModal(true);
    }
  };

  // Function to handle viewing an assessment
  const handleViewAssessment = (assessment) => {
    if (onViewAssessment) {
      onViewAssessment(assessment);
    } else {
      // Fallback if onViewAssessment is not provided
      console.log("View assessment:", assessment);
    }
  };

  // Mock function to add a sample assessment (for testing)
  const addSampleAssessment = () => {
    const newAssessment = {
      id: Date.now().toString(),
      name: `Assessment ${assessments.length + 1}`,
      createdAt: new Date().toISOString(),
      status: 'Completed',
      rubric: "Code compiles and runs without errors\nCode follows best practices (naming, structure, comments)\nFunctionality matches assignment requirements\nCode is efficient and readable\nProper use of version control (commits, messages)",
      results: [
        { 
          name: 'Adrian',
          github: 'https://github.com/saintAdrian7/Group-5-Project',
          group: 'Group 5',
          score: 85,
          report: "### Assessment Results\n\n- Code quality: 4/5\n- Documentation: 3/5\n- Version control: 4/5\n- Features: 5/5\n- Testing: 3/5\n\n**Overall Score:** 85%"
        },
        {
          name: 'Jonathan',
          github: 'https://github.com/Vaniah1/Blog',
          group: 'Group 3',
          score: 78,
          report: "### Assessment Results\n\n- Code quality: 3/5\n- Documentation: 4/5\n- Version control: 3/5\n- Features: 4/5\n- Testing: 3/5\n\n**Overall Score:** 78%"
        }
      ]
    };
    
    setAssessments(prevAssessments => [...prevAssessments, newAssessment]);
  };

  // Function to render the assessments list view
  const renderAssessmentsList = () => {
    return (
      <div className="w-full">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-black">Assessments</h1>
          <div className="flex gap-2">
            <button
              onClick={handleAddAssessment}
              className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
              New Assessment
            </button>
            {/* Add a sample assessment button for testing */}
            <button
              onClick={addSampleAssessment}
              className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md"
            >
              Add Sample
            </button>
          </div>
        </div>

        {assessments.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <h3 className="text-xl font-medium text-gray-900 mb-2">No Assessments Yet</h3>
            <p className="text-gray-600 mb-6">Start by creating your first code assessment</p>
            <button
              onClick={handleAddAssessment}
              className="bg-green-600 hover:bg-green-700 text-white py-2 px-6 rounded-md"
            >
              Create Assessment
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {assessments.map((assessment, index) => (
              <div
                key={assessment.id || index}
                className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleViewAssessment(assessment)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">{assessment.name || `Assessment ${index + 1}`}</h3>
                    <p className="text-gray-600 mt-1">
                      {assessment.results?.length || 0} students assessed
                    </p>
                    <p className="text-gray-500 text-sm mt-2">
                      Created: {new Date(assessment.createdAt || Date.now()).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="bg-green-100 text-green-800 text-sm font-medium px-3 py-1 rounded-full">
                    {assessment.status || 'Completed'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Function to render the dashboard overview
  const renderDashboardOverview = () => {
    return (
      <>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-black">Dashboard Overview</h1>
          <p className="text-gray-700">Welcome to your code assessment dashboard</p>
        </div>
        
        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            {/* Card 1: Create Assessment */}
            <div 
              className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-all flex flex-col items-center justify-center min-h-[180px] cursor-pointer"
              onClick={handleAddAssessment}
            >
              <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center mb-4 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-black mb-2">Create Assessment</h3>
              <p className="text-gray-600 text-sm">Start a new student code assessment</p>
            </div>
            
            {/* Card 2: Previous Assessments */}
            <div 
              className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-all flex flex-col items-center justify-center min-h-[180px] cursor-pointer"
              onClick={() => handleSidebarItemClick("previous-assessments")}
            >
              <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center mb-4 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-black mb-2">Previous Assessments</h3>
              <p className="text-gray-600 text-sm">View and manage past assessments</p>
            </div>
            
            {/* Card 3: Student Statistics */}
            <div 
              className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-all flex flex-col items-center justify-center min-h-[180px] cursor-pointer"
              onClick={() => handleSidebarItemClick("student-stats")}
            >
              <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center mb-4 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-black mb-2">Student Statistics</h3>
              <p className="text-gray-600 text-sm">View student data and metrics</p>
            </div>
            
            {/* Card 4: Total Assessments */}
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-all flex flex-col items-center justify-center min-h-[180px]">
              <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center mb-4 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-black mb-2">Total Assessments</h3>
              <div className="text-4xl font-bold text-green-600">{assessments.length}</div>
            </div>
            
            {/* Card 5: Total Students */}
            <div 
              className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-all flex flex-col items-center justify-center min-h-[180px] cursor-pointer"
              onClick={() => setShowStudentsModal(true)}
              role="button"
              tabIndex="0"
              aria-label="View student details"
              onKeyPress={(e) => e.key === 'Enter' && setShowStudentsModal(true)}
            >
              <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center mb-4 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-black mb-2">Total Students</h3>
              <div className="text-4xl font-bold text-green-600">{studentStats.total}</div>
            </div>
          </div>
        )}
      </>
    );
  };

  return (
    <div className="flex min-h-screen bg-white">
      <Sidebar activeView={activeView} />
      
      <div className="flex-1 p-8 ml-0 md:ml-64">
        <div className="max-w-7xl mx-auto">
          {loading && (
            <div className="flex flex-col items-center justify-center p-8 text-black">
              <div className="w-10 h-10 border-4 border-green-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p>Loading dashboard data...</p>
            </div>
          )}
          
          {error && (
            <div className="text-center p-8 bg-red-50 rounded-lg border border-red-200 m-8">
              <div className="text-red-500 mb-4">{error}</div>
              <button 
                className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded transition-colors"
                onClick={() => window.location.reload()}
                aria-label="Retry loading assessments"
              >
                Retry
              </button>
            </div>
          )}
          
          {!loading && !error && (
            activeView === "assessments" ? renderAssessmentsList() : renderDashboardOverview()
          )}
          
          {/* Student Statistics Modal */}
          {showStudentsModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
                <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                  <h2 className="text-2xl font-bold text-black">Student Statistics</h2>
                  <button 
                    onClick={() => setShowStudentsModal(false)}
                    className="text-gray-500 hover:text-gray-700"
                    aria-label="Close modal"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                      <h3 className="text-lg font-semibold text-black mb-2">Total Students</h3>
                      <div className="text-3xl font-bold text-green-600">{studentStats.total}</div>
                    </div>
                    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                      <h3 className="text-lg font-semibold text-black mb-2">Total Groups</h3>
                      <div className="text-3xl font-bold text-green-600">{Object.keys(studentStats.groups).length}</div>
                    </div>
                    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                      <h3 className="text-lg font-semibold text-black mb-2">Total Projects</h3>
                      <div className="text-3xl font-bold text-green-600">{Object.keys(studentStats.projects).length}</div>
                    </div>
                  </div>
                  
                  <h3 className="text-xl font-semibold text-black mb-4">Student List</h3>
                  {studentStats.students.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Group</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">GitHub</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {studentStats.students.map((student, index) => (
                            <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{student.name}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{student.group}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{student.project}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{student.score}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {student.github ? (
                                  <a 
                                    href={student.github} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-green-600 hover:text-green-800"
                                  >
                                    View GitHub
                                  </a>
                                ) : (
                                  'N/A'
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center p-8 bg-gray-50 rounded-lg">
                      <p className="text-gray-600">No student data available</p>
                    </div>
                  )}
                </div>
                <div className="p-6 border-t border-gray-200 flex justify-end">
                  <button 
                    onClick={() => setShowStudentsModal(false)}
                    className="bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
