import React, { useEffect, useState } from "react";
import api from "../services/api";

const Analytics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.getAnalytics();
        if (response.success) {
          setStats(response);
        } else {
          setError(response.error || "Failed to fetch analytics.");
        }
      } catch (err) {
        setError(err.message || "Failed to fetch analytics.");
      }
      setLoading(false);
    };
    fetchAnalytics();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Analytics</h1>
      {loading && <p>Loading analytics...</p>}
      {error && <div className="text-red-600 mb-4">{error}</div>}
      {!loading && !error && stats && (
        <div className="bg-white border rounded-lg p-6 shadow-md max-w-lg">
          <div className="mb-4">
            <span className="font-semibold">Total Students:</span> {stats.total_students}
          </div>
          <div className="mb-4">
            <span className="font-semibold">Total Assessments:</span> {stats.total_assessments}
          </div>
          <div className="mb-4">
            <span className="font-semibold">Average Score:</span> {stats.average_score !== null ? stats.average_score : 'N/A'}
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;
