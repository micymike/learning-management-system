import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const StudentTracking = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStudents = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.getStudents();
        if (response.success && response.students) {
          setStudents(response.students);
        } else {
          setError(response.error || "Failed to fetch students.");
        }
      } catch (err) {
        setError(err.message || "Failed to fetch students.");
      }
      setLoading(false);
    };
    fetchStudents();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Student Tracking</h1>
      {loading && <p>Loading students...</p>}
      {error && <div className="text-red-600 mb-4">{error}</div>}
      {!loading && !error && (
        <table className="min-w-full bg-white border border-gray-200 rounded-lg">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">Name</th>
              <th className="py-2 px-4 border-b">Email</th>
              <th className="py-2 px-4 border-b">GitHub</th>
              <th className="py-2 px-4 border-b">Assessments</th>
            </tr>
          </thead>
          <tbody>
            {students.map(student => (
              <tr key={student.id} className="hover:bg-gray-100 cursor-pointer" onClick={() => navigate(`/students/${student.id}`)}>
                <td className="py-2 px-4 border-b">{student.name}</td>
                <td className="py-2 px-4 border-b">{student.email}</td>
                <td className="py-2 px-4 border-b">{student.github_username}</td>
                <td className="py-2 px-4 border-b text-center">{student.assessments ? student.assessments.length : 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default StudentTracking;
