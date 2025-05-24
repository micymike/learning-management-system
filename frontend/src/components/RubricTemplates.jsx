import React, { useState, useEffect } from 'react';
import './FormCard.css';

const RubricTemplates = ({ onSelectRubric }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [rubricContent, setRubricContent] = useState('');

  // Fetch available templates
  useEffect(() => {
    const fetchTemplates = async () => {
      setLoading(true);
      try {
        const response = await fetch('/rubric_templates');
        const data = await response.json();
        if (data.success) {
          setTemplates(data.templates);
        } else {
          setError('Failed to load templates');
        }
      } catch (err) {
        setError('Error connecting to server');
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  // Load template content when selected
  const handleTemplateSelect = async (templateName) => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`/rubric_templates/${templateName}`);
      const data = await response.json();
      if (data.success) {
        setRubricContent(data.content);
        setSelectedTemplate(templateName);
        if (onSelectRubric) {
          onSelectRubric(data.content);
        }
      } else {
        setError('Failed to load template');
      }
    } catch (err) {
      setError('Error loading template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card blue-bg animate-fadein">
      <h2>Rubric Templates</h2>
      
      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error-msg">{error}</div>}
      
      <div className="template-list">
        {templates.map((template, index) => (
          <div 
            key={index} 
            className={`template-item ${selectedTemplate === template.path.split('.')[0] ? 'selected' : ''}`}
            onClick={() => handleTemplateSelect(template.path.split('.')[0])}
          >
            <h3>{template.name}</h3>
            <p>{template.description}</p>
          </div>
        ))}
      </div>
      
      {rubricContent && (
        <div className="rubric-preview animate-slidein">
          <h3>Rubric Preview</h3>
          <pre className="rubric-content">{rubricContent}</pre>
          <button 
            className="jungle-btn"
            onClick={() => onSelectRubric && onSelectRubric(rubricContent)}
          >
            Use This Rubric
          </button>
        </div>
      )}
    </div>
  );
};

export default RubricTemplates;