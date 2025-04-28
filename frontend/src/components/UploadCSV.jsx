import React, { useState } from "react";
import './FormCard.css';

const UploadCSV = ({ onReport }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a CSV file.");
      return;
    }
    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/upload_csv", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.results) {
        onReport(data.results);
      } else {
        setError("Unexpected response from server.");
      }
    } catch (err) {
      setError("Failed to upload CSV. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card jungle-green-bg animate-fadein">
      <h2>Upload Students CSV</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="input-file"
        />
        <button className="jungle-btn" type="submit" disabled={loading}>
          {loading ? "Uploading..." : "Upload & Assess"}
        </button>
      </form>
      {error && <div className="error-msg">{error}</div>}
    </div>
  );
};

export default UploadCSV;
