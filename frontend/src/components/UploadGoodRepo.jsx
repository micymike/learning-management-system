import React, { useState } from 'react';

const UploadGoodRepo = () => {
  const [repoUrl, setRepoUrl] = useState('');
  const [rubric, setRubric] = useState('');
  const [exampleId, setExampleId] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      const response = await fetch('/rag/embed-good-repo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_url: repoUrl,
          rubric,
          example_id: exampleId || undefined,
        }),
      });
      const data = await response.json();
      if (response.ok && data.success) {
        setMessage(data.message || 'Repository embedded successfully!');
        setRepoUrl('');
        setRubric('');
        setExampleId('');
      } else {
        setError(data.error || 'Failed to embed repository.');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Test interface for quick backend testing
  const [testResult, setTestResult] = useState(null);
  const handleTest = async () => {
    setTestResult('Testing...');
    try {
      const response = await fetch('/rag/embed-good-repo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_url: 'https://github.com/octocat/Hello-World',
          rubric: 'Sample rubric for testing',
          example_id: 'test_example_1',
        }),
      });
      const data = await response.json();
      setTestResult(JSON.stringify(data, null, 2));
    } catch (err) {
      setTestResult('Network error');
    }
  };

  return (
    <div className="form-card" style={{ maxWidth: 500, margin: '2rem auto', padding: '2rem', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #eee' }}>
      <h2>Upload Good Repository for Embedding</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 16 }}>
          <label>Repository URL<span style={{ color: 'red' }}>*</span></label>
          <input
            type="url"
            value={repoUrl}
            onChange={e => setRepoUrl(e.target.value)}
            required
            placeholder="https://github.com/username/repo"
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
          />
        </div>
        <div style={{ marginBottom: 16 }}>
          <label>Rubric (optional)</label>
          <textarea
            value={rubric}
            onChange={e => setRubric(e.target.value)}
            rows={5}
            placeholder="Paste rubric text here..."
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
          />
        </div>
        <div style={{ marginBottom: 16 }}>
          <label>Example ID (optional)</label>
          <input
            type="text"
            value={exampleId}
            onChange={e => setExampleId(e.target.value)}
            placeholder="e.g. instructor_example_1"
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
          />
        </div>
        <button type="submit" disabled={loading} style={{ padding: '10px 24px', borderRadius: 4, background: '#2563eb', color: '#fff', border: 'none', fontWeight: 600 }}>
          {loading ? 'Uploading...' : 'Embed Repository'}
        </button>
      </form>
      {message && <div style={{ color: 'green', marginTop: 16 }}>{message}</div>}
      {error && <div style={{ color: 'red', marginTop: 16 }}>{error}</div>}
      <hr style={{ margin: '2rem 0' }} />
      <div>
        <h4>Quick Test</h4>
        <button type="button" onClick={handleTest} style={{ padding: '6px 18px', borderRadius: 4, background: '#10b981', color: '#fff', border: 'none', fontWeight: 600 }}>
          Send Test Request
        </button>
        {testResult && (
          <pre style={{ background: '#f3f3f3', padding: 12, borderRadius: 4, marginTop: 12, fontSize: 13 }}>{testResult}</pre>
        )}
      </div>
    </div>
  );
};

export default UploadGoodRepo; 