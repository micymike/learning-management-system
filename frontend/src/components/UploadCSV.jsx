import React, { useState } from "react";
import './FormCard.css';

const UploadCSV = ({ onReport }) => {
  const [file, setFile] = useState(null);
  const [rubricFile, setRubricFile] = useState(null);
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

  const handleRubricChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setRubricFile(selectedFile);
      setError("");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a student CSV file.");
      return;
    }
    if (!rubricFile) {
      setError("Please select a rubric file.");
      return;
    }

    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("rubric", rubricFile);

    try {
      const res = await fetch("/api/agentic/upload_csv", {
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
      <h2>Upload Student Data & Rubric</h2>
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
        <input
          type="file"
          accept=".txt,.json"
          onChange={handleRubricChange}
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
