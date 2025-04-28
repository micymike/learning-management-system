import React from "react";
import './ReportViewer.css';

const ReportViewer = ({ reports }) => {
  if (!reports || reports.length === 0) return null;

  return (
    <div className="report-container animate-slidein">
      {reports.map((r, idx) => (
        <div key={idx} className="report-card jungle-green-border">
          <div className="report-content">
            <div dangerouslySetInnerHTML={{ __html: window.marked ? window.marked.parse(r.report || r.assessment || r.result || "") : (r.report || r.assessment || r.result || "") }} />
          </div>
        </div>
      ))}
    </div>
  );
};

export default ReportViewer;
