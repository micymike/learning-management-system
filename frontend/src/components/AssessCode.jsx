import React, { useState } from "react";
import './FormCard.css';

const AssessCode = ({ onResult }) => {
  const [code, setCode] = useState("");
  const [rubric, setRubric] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!code || !rubric) {
      setError("Please provide both code and rubric.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("code", code);
      formData.append("rubric", rubric);
      const res = await fetch("/assess", {
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
      setError("Failed to assess code. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card jungle-green-bg animate-fadein">
      <h2>Direct Code Assessment</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          className="input-area"
          rows={6}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Paste code here..."
        />
        <textarea
          className="input-area"
          rows={3}
          value={rubric}
          onChange={(e) => setRubric(e.target.value)}
          placeholder="Paste rubric here..."
        />
        <button className="jungle-btn" type="submit" disabled={loading}>
          {loading ? "Assessing..." : "Assess Code"}
        </button>
      </form>
      {error && <div className="error-msg">{error}</div>}
    </div>
  );
};

export default AssessCode;
