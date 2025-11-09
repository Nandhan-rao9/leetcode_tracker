import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { API_URL } from '../App'; // Import the base URL

// --- Reusable Styles ---
const cardStyle = {
  background: '#fff',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '1.5rem',
  marginBottom: '1rem',
  boxShadow: '0 1px 3px 0 rgba(0,0,0,0.05)'
};

const problemTitleStyle = {
  fontSize: '1.25rem',
  fontWeight: '600',
  marginBottom: '0.5rem',
  color: '#111827'
};

const problemLinkStyle = {
  textDecoration: 'none',
  color: '#007bff'
};

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

// --- Reusable Problem Card Component ---
const ProblemCard = ({ problem }) => (
  <div style={cardStyle}>
    <h3 style={problemTitleStyle}>
      <a href={problem.link} target="_blank" rel="noopener noreferrer" style={problemLinkStyle}>
        {problem.title}
      </a>
    </h3>
    <span style={{...tagStyle, background: problem.difficulty === 'Medium' ? '#fef3c7' : '#fecaca', color: problem.difficulty === 'Medium' ? '#92400e' : '#991b1b'}}>
      {problem.difficulty}
    </span>
    <div>
      {problem.topicTags.map(tag => (
        <span key={tag.slug} style={tagStyle}>{tag.name}</span>
      ))}
    </div>
  </div>
);


function Dashboard({ solvedProblems }) {
  const [dailyProblem, setDailyProblem] = useState(null);
  const [similarProblems, setSimilarProblems] = useState([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);

  // 1. Find the "Daily" Problem
  // useMemo ensures this only runs once
  useMemo(() => {
    const hardProblems = solvedProblems.filter(
      p => p.difficulty === 'Medium' || p.difficulty === 'Hard'
    );
    
    if (hardProblems.length === 0) return;

    // "Daily" logic: use the day of the year as a consistent index
    const today = new Date();
    const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
    const dailyIndex = dayOfYear % hardProblems.length;
    const problem = hardProblems[dailyIndex];
    
    setDailyProblem(problem);
  }, [solvedProblems]);

  // 2. Fetch similar problems once we have a daily problem
  useEffect(() => {
    if (dailyProblem) {
      const fetchSimilar = async () => {
        setLoadingSimilar(true);
        // Get the names of the topics
        const tags = dailyProblem.topicTags.map(t => t.name).join(',');
        
        try {
          const response = await axios.get(`${API_URL}/api/problems/find-similar?tags=${tags}`);
          setSimilarProblems(response.data.data);
        } catch (err) {
          console.error("Error fetching similar problems:", err);
        } finally {
          setLoadingSimilar(false);
        }
      };
      
      fetchSimilar();
    }
  }, [dailyProblem]); // This runs when 'dailyProblem' is set

  if (!dailyProblem) {
    return <div>No Medium or Hard problems solved yet. Solve some to get revisions!</div>;
  }

  return (
    <div>
      <h2>Daily Revision Problem</h2>
      <p>Revise this problem you've solved before, then try the similar unsolved problems!</p>
      
      <ProblemCard problem={dailyProblem} />

      <hr style={{margin: '2rem 0', border: 'none', borderTop: '1px solid #e5e7eb'}} />

      <h2>Similar Unsolved Problems (Medium/Hard)</h2>
      {loadingSimilar && <p>Finding similar problems...</p>}
      {!loadingSimilar && similarProblems.length === 0 && (
        <p>No similar unsolved problems found.</p>
      )}
      
      {/* We'll re-use a simplified card for these */}
      {similarProblems.map(prob => (
        <div key={prob.titleSlug} style={{...cardStyle, padding: '1rem 1.5rem'}}>
          <a href={prob.link} target="_blank" rel="noopener noreferrer" style={{...problemLinkStyle, fontWeight: '600'}}>
            {prob.title}
          </a>
          <span style={{...tagStyle, float: 'right', background: prob.difficulty === 'Medium' ? '#fef3c7' : '#fecaca', color: prob.difficulty === 'Medium' ? '#92400e' : '#991b1b'}}>
            {prob.difficulty}
          </span>
        </div>
      ))}
    </div>
  );
}

export default Dashboard;