import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { assessApi } from '../services/api';

const StudentData = () => {
  const { id } = useParams();
  const [studentData, setStudentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStudentData = async () => {
      setLoading(true);
      try {
        const response = await assessApi.getStudentData(id);
        if (response.success) {
          setStudentData(response.data);
        } else {
          throw new Error(response.error || 'Failed to fetch student data');
        }
      } catch (err) {
        console.error('Error fetching student data:', err);
        setError(err.message || 'Failed to load student data');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchStudentData();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
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
          onClick={() => window.location.reload()} 
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!studentData) {
    return (
      <div className="p-4 bg-yellow-100 text-yellow-700 rounded-md">
        <h2 className="text-xl font-bold">No Data Found</h2>
        <p>No data available for this student.</p>
        <Link to="/students" className="mt-2 inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Back to Students
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <Link to="/students" className="text-blue-600 hover:text-blue-800">
          &larr; Back to Students
        </Link>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">{studentData.name}</h1>
            {studentData.email && <p className="text-gray-600 mb-1">Email: {studentData.email}</p>}
            {studentData.github_username && (
              <p className="text-gray-600">
                GitHub: 
                <a 
                  href={`https://github.com/${studentData.github_username}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 ml-1"
                >
                  {studentData.github_username}
                </a>
              </p>
            )}
          </div>
          
          <div className="bg-gray-100 rounded-lg p-4 text-center">
            <p className="text-sm text-gray-500 uppercase font-semibold">Overall Performance</p>
            <p className={`text-2xl font-bold ${studentData.overall_passing ? 'text-green-600' : 'text-red-600'}`}>
              {studentData.overall_percentage ? `${studentData.overall_percentage.toFixed(1)}%` : 'N/A'}
            </p>
            <p className={`text-sm font-medium ${studentData.overall_passing ? 'text-green-600' : 'text-red-600'}`}>
              {studentData.overall_passing ? 'PASSING' : 'NEEDS IMPROVEMENT'}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white shadow-md rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2">Assessments</h3>
          <p className="text-3xl font-bold text-blue-600">{studentData.assessments?.length || 0}</p>
          <p className="text-sm text-gray-500">Total assessments completed</p>
        </div>
        
        <div className="bg-white shadow-md rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2">Passing Rate</h3>
          <p className="text-3xl font-bold text-green-600">
            {studentData.passing_count || 0}/{studentData.assessments?.length || 0}
          </p>
          <p className="text-sm text-gray-500">Assessments passed</p>
        </div>
        
        <div className="bg-white shadow-md rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2">Average Score</h3>
          <p className="text-3xl font-bold text-purple-600">
            {studentData.average_score ? `${studentData.average_score.toFixed(1)}%` : 'N/A'}
          </p>
          <p className="text-sm text-gray-500">Across all assessments</p>
        </div>
      </div>

      <h2 className="text-xl font-bold mb-4">Assessment Results</h2>
      
      {(!studentData.assessments || studentData.assessments.length === 0) ? (
        <p className="text-gray-500">No assessment results available.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-200 rounded-lg overflow-hidden">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assessment</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {studentData.assessments.map((assessment) => {
                const isPassing = assessment.passing || (assessment.percentage >= 80);
                
                return (
                  <tr key={assessment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{assessment.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {new Date(assessment.date).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {assessment.total_points}/{assessment.max_points} ({assessment.percentage.toFixed(1)}%)
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        isPassing 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {isPassing ? 'PASS' : 'FAIL'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Link 
                        to={`/assessments/${assessment.id}`} 
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {studentData.assessments && studentData.assessments.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Criteria Performance</h2>
          
          <div className="bg-white shadow-md rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Performance by Criteria</h3>
            
            {studentData.criteria_performance ? (
              <div className="space-y-4">
                {Object.entries(studentData.criteria_performance).map(([criterion, data]) => (
                  <div key={criterion} className="border-b pb-4">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-medium">{criterion}</h4>
                      <span className="text-sm font-semibold">
                        {data.average_percentage.toFixed(1)}% ({data.average_points.toFixed(1)}/{data.max_points})
                      </span>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div 
                        className={`h-2.5 rounded-full ${
                          data.average_percentage >= 80 ? 'bg-green-600' : 
                          data.average_percentage >= 60 ? 'bg-yellow-500' : 'bg-red-600'
                        }`}
                        style={{ width: `${data.average_percentage}%` }}
                      ></div>
                    </div>
                    
                    <p className="text-sm text-gray-500 mt-1">
                      {data.average_percentage >= 80 
                        ? 'Strong performance' 
                        : data.average_percentage >= 60 
                          ? 'Satisfactory performance' 
                          : 'Needs improvement'}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No criteria performance data available.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentData;