import React, { useState } from 'react';

// --- Reusable Styles ---
const cardStyle = {
  background: '#fff',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  marginBottom: '1rem',
  boxShadow: '0 1px 3px 0 rgba(0,0,0,0.05)',
  cursor: 'pointer' 
};

const cardHeaderStyle = {
  padding: '1rem 1.5rem',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
};

const topicNameStyle = {
  fontSize: '1.125rem',
  fontWeight: '600',
  color: '#1f2937'
};

const topicCountStyle = {
  fontSize: '1rem',
  fontWeight: '500',
  color: '#4b5563'
};

const dropdownContentStyle = {
  padding: '0 1.5rem 1.5rem 1.5rem', 
  borderTop: '1px solid #e5e7eb',
  marginTop: '1rem'
};

const solvedProblemStyle = {
  padding: '0.5rem 0',
};

// Add a bottom border to all but the last item
const solvedProblemItemStyle = (isLast) => ({
  ...solvedProblemStyle,
  borderBottom: isLast ? 'none' : '1px solid #f3f4f6'
});


const solvedProblemLinkStyle = {
  textDecoration: 'none',
  color: '#007bff',
  fontWeight: '500'
};

// --- Reusable TopicCard Component ---
const TopicCard = ({ topic }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={cardStyle}>
      <div 
        style={cardHeaderStyle} 
        onClick={() => setIsOpen(!isOpen)}
        role="button"
        tabIndex="0"
        aria-expanded={isOpen}
      >
        <span style={topicNameStyle}>
          {topic.name}
        </span>
        <span style={topicCountStyle}>
          Solved: <strong style={{color: '#111827'}}>{topic.count}</strong>
        </span>
      </div>

      {isOpen && (
        <div style={dropdownContentStyle}>
          <h4 style={{marginTop: 0, marginBottom: '0.5rem', color: '#374151'}}>Problems Solved:</h4>
          {topic.solved.map((problem, index) => (
            <div 
              key={problem.title} 
              style={solvedProblemItemStyle(index === topic.solved.length - 1)}
            >
              {/* --- THIS IS THE FIX --- */}
              <a 
                href={problem.link} 
                target="_blank" 
                rel="noopener noreferrer" 
                style={solvedProblemLinkStyle}
              >
                {problem.title}
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


// --- The Main Topics Page ---
function Topics({ topicStats }) {
  const weakTopics = topicStats.filter(topic => topic.count <= 6);
  const strongTopics = topicStats.filter(topic => topic.count > 6);
  strongTopics.sort((a, b) => b.count - a.count);

  return (
    <div>
      <h2>Your Weak Topics (Solved 6 or less)</h2>
      <p>Click on any topic to see the list of problems you've solved for it.</p>
      
      <div style={{marginTop: '1.5rem'}}>
        {weakTopics.length > 0 ? (
          weakTopics.map(topic => (
            <TopicCard key={topic.name} topic={topic} />
          ))
        ) : (
          <p>No "weak" topics found (all topics have greater than 6 problems solved)!</p>
        )}
      </div>
      
      <hr style={{margin: '3rem 0', border: 'none', borderTop: '1px solid #e5e7eb'}} />
      
      <h2>Your Other Topics (Sorted by strongest)</h2>
      <div style={{marginTop: '1.5rem'}}>
        {strongTopics.map(topic => (
          <TopicCard key={topic.name} topic={topic} />
        ))}
      </div>
    </div>
  );
}

export default Topics;