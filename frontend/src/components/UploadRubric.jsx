import React, { useState } from "react";
import './FormCard.css';

const UploadRubric = ({ onRubric }) => {
  
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [rubric, setRubric] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a rubric file.");
      return;
    }
    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/upload_rubric", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setRubric(data.result);
      if (onRubric) onRubric(data.result);
    } catch (err) {
      setError("Failed to upload rubric. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card jungle-green-bg animate-fadein">
      <h2>Upload Rubric</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".txt"
          onChange={handleFileChange}
          className="input-file"
        />
        <button className="jungle-btn" type="submit" disabled={loading}>
          {loading ? "Uploading..." : "Upload Rubric"}
        </button>
      </form>
      {error && <div className="error-msg">{error}</div>}
      {rubric && (
        <div className="rubric-box animate-slidein">
          <pre>{rubric}</pre>
        </div>
      )}
    </div>
  );
};

export default UploadRubric;