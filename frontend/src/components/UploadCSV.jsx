import React, { useState } from "react";
import './FormCard.css';

const UploadCSV = ({ onReport, rubric }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const fileExt = selectedFile.name.split('.').pop().toLowerCase();
      if (['csv', 'xlsx', 'xls', 'txt'].includes(fileExt)) {
        setFile(selectedFile);
        setError("");
      } else {
        setError("Please select a valid file (CSV, Excel, or TXT)");
        e.target.value = null;
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file.");
      return;
    }
    
    if (!rubric) {
      setError("No rubric available. Please upload or select a rubric first.");
      return;
    }
    
    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("rubric", rubric);
    
    try {
      const res = await fetch("/upload_csv", {
        method: "POST",
        body: formData,
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      if (data.results) {
        onReport({ scores: data.results });
      } else {
        setError("Unexpected response from server.");
      }
    } catch (err) {
      setError(`Failed to upload file: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card jungle-green-bg animate-fadein">
      <h2>Upload Student Data</h2>
      <p className="file-info">
        Supported formats: CSV, Excel (.xlsx, .xls), or TXT
      </p>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".csv,.xlsx,.xls,.txt"
          onChange={handleFileChange}
          className="input-file"
        />
        <button className="jungle-btn" type="submit" disabled={loading}>
          {loading ? (
            <>
              <span className="loading-spinner"></span>
              Uploading...
            </>
          ) : (
            "Upload & Generate Scores"
          )}
        </button>
      </form>
      {error && <div className="error-msg">{error}</div>}
    </div>
  );
};

export default UploadCSV;
