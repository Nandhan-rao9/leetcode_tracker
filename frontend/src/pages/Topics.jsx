import React from 'react';

// Card styles
const cardStyle = {
  background: '#fff',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '1rem 1.5rem',
  marginBottom: '1rem',
  boxShadow: '0 1px 3px 0 rgba(0,0,0,0.05)',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
};

function Topics({ topicStats }) {
  return (
    <div>
      <h2>Your Weakest Topics</h2>
      <p>This list is sorted by the fewest problems you've solved for each topic (ignoring common tags like "Array" and "String").</p>
      
      <div style={{marginTop: '1.5rem'}}>
        {topicStats.map(topic => (
          <div key={topic.name} style={cardStyle}>
            <span style={{fontSize: '1.125rem', fontWeight: '600', color: '#1f2937'}}>
              {topic.name}
            </span>
            <span style={{fontSize: '1rem', fontWeight: '500', color: '#4b5563'}}>
              Solved: <strong style={{color: '#111827'}}>{topic.count}</strong>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Topics;