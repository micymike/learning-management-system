import React, { useState } from "react";
import './FormCard.css';

const UploadGithubURL = ({ onResult }) => {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) {
      setError("Please provide a GitHub repo URL.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("url", url);
      const res = await fetch("/upload_github_url", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.result) {
        onResult(data.result);
      } else {
        setError("Unexpected response from server.");
      }
    } catch (err) {
      setError("Failed to analyze repo. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card jungle-green-bg animate-fadein">
      <h2>Analyze GitHub Repository</h2>
      <form onSubmit={handleSubmit}>
        <input
          className="input-field"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter GitHub repo URL..."
        />
        <button className="jungle-btn" type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Repo"}
        </button>
      </form>
      {error && <div className="error-msg">{error}</div>}
    </div>
  );
};

export default UploadGithubURL;
