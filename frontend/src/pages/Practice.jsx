import React, { useState, useMemo } from 'react';
import axios from 'axios';
import { API_URL } from '../App';

// --- Styles ---
const cardStyle = {
  background: '#fff',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '1.5rem',
  boxShadow: '0 1px 3px 0 rgba(0,0,0,0.05)',
};
const configContainerStyle = {
  ...cardStyle,
  marginBottom: '2rem'
};
const topicGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
  gap: '1rem',
  maxHeight: '300px',
  overflowY: 'auto',
  border: '1px solid #e5e7eb',
  padding: '1rem',
  borderRadius: '8px'
};
const topicCheckboxStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.5rem',
  cursor: 'pointer'
};
const formRowStyle = {
  display: 'flex',
  gap: '1rem',
  alignItems: 'center',
  marginTop: '1.5rem'
};
const numberInputStyle = {
  width: '100px',
  padding: '0.75rem 1rem',
  fontSize: '1rem',
  borderRadius: '6px',
  border: '1px solid #d1d5db'
};
const buttonStyle = {
  padding: '0.75rem 1.5rem',
  border: 'none',
  borderRadius: '6px',
  background: '#007bff',
  color: 'white',
  fontWeight: '600',
  cursor: 'pointer',
  fontSize: '1rem'
};
const resultsGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(2, 1fr)', // 2 columns!
  gap: '1.5rem',
};
const problemCardStyle = {
  ...cardStyle,
  position: 'relative',
  paddingTop: '2.5rem'
};
const problemTypeLabel = (type) => ({
  position: 'absolute',
  top: '0',
  left: '1.5rem',
  background: type === 'New' ? '#22c55e' : '#f59e0b',
  color: 'white',
  padding: '0.25rem 0.75rem',
  borderRadius: '0 0 6px 6px',
  fontSize: '0.875rem',
  fontWeight: '600'
});
const tagStyle = {
  display: 'inline-block',
  background: '#e0e7ff',
  color: '#4338ca',
  padding: '0.25rem 0.75rem',
  borderRadius: '99px',
  fontSize: '0.875rem',
  fontWeight: '500',
  marginRight: '0.5rem',
  marginTop: '0.5rem'
};
const problemLinkStyle = {
  textDecoration: 'none',
  color: '#007bff',
  fontWeight: '600',
  fontSize: '1.25rem'
};
const getDifficultyColor = (difficulty) => {
  switch (difficulty) {
    case 'Easy': return '#22c55e';
    case 'Medium': return '#f59e0b';
    case 'Hard': return '#ef4444';
    default: return '#6b7280';
  }
};

// --- The Page Component ---
function Practice({ allTopics }) { // We get allTopics from App.jsx
  const [selectedTopics, setSelectedTopics] = useState({});
  const [revisionCount, setRevisionCount] = useState(2);
  const [newCount, setNewCount] = useState(3);
  
  const [generatedProblems, setGeneratedProblems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTopicChange = (e) => {
    const { name, checked } = e.target;
    setSelectedTopics(prev => ({
      ...prev,
      [name]: checked,
    }));
  };

  const handleGenerateSet = async () => {
    // 1. Validate inputs
    const total = revisionCount + newCount;
    if (total <= 0) {
      setError("Total problems must be greater than 0.");
      return;
    }
    if (total > 5) {
      setError("You can generate a maximum of 5 problems at a time.");
      return;
    }
    
    // 2. Get the list of selected topic names
    const topics = Object.keys(selectedTopics).filter(topic => selectedTopics[topic]);
    if (topics.length === 0) {
      setError("Please select at least one topic.");
      return;
    }

    // 3. Call the API
    setError(null);
    setLoading(true);
    setGeneratedProblems([]);
    
    try {
      const response = await axios.post(`${API_URL}/api/problems/generate-set`, {
        topics: topics,
        revision_count: revisionCount,
        new_count: newCount
      });
      setGeneratedProblems(response.data.data);
    } catch (err) {
      console.error("Error generating set:", err);
      setError("Failed to generate practice set.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* --- 1. CONFIGURATION CARD --- */}
      <div style={configContainerStyle}>
        <h2>Create a Practice Set</h2>
        
        <label style={{display: 'block', fontWeight: '600', marginBottom: '0.5rem'}}>
          1. Select Topics
        </label>
        <div style={topicGridStyle}>
          {allTopics.map(topic => (
            <label key={topic} style={topicCheckboxStyle}>
              <input
                type="checkbox"
                name={topic}
                checked={!!selectedTopics[topic]}
                onChange={handleTopicChange}
                style={{width: '1rem', height: '1rem'}}
              />
              {topic}
            </label>
          ))}
        </div>

        <label style={{display: 'block', fontWeight: '600', marginBottom: '0.5rem', marginTop: '1.5rem'}}>
          2. Select Ratio (Max 5 Total)
        </label>
        <div style={formRowStyle}>
          <div>
            <label>Revision Problems (Solved)</label>
            <input
              type="number"
              min="0"
              max="5"
              value={revisionCount}
              onChange={(e) => setRevisionCount(parseInt(e.target.value) || 0)}
              style={numberInputStyle}
            />
          </div>
          <div>
            <label>New Problems (Unsolved)</label>
            <input
              type="number"
              min="0"
              max="5"
              value={newCount}
              onChange={(e) => setNewCount(parseInt(e.target.value) || 0)}
              style={numberInputStyle}
            />
          </div>
          <button style={buttonStyle} onClick={handleGenerateSet} disabled={loading}>
            {loading ? 'Generating...' : `Generate ${revisionCount + newCount} Problems`}
          </button>
        </div>
        {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
      </div>
      
      {/* --- 2. RESULTS GRID --- */}
      <div style={resultsGridStyle}>
        {generatedProblems.map(problem => (
          <div key={problem._id} style={problemCardStyle}>
            <span style={problemTypeLabel(problem.type)}>{problem.type}</span>
            <a href={problem.link} target="_blank" rel="noopener noreferrer" style={problemLinkStyle}>
              {problem.title}
            </a>
            <div style={{marginTop: '0.5rem'}}>
              <span style={{color: getDifficultyColor(problem.difficulty), fontWeight: '600'}}>
                {problem.difficulty}
              </span>
            </div>
            <div style={{marginTop: '1rem'}}>
              {problem.all_topics.map(tag => (
                <span key={tag} style={tagStyle}>{tag}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Practice;