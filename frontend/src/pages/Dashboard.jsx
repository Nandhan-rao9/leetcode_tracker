import React, { useState, useMemo } from 'react';

// --- All styles and functions above this line are unchanged ---
// (Copy/paste the entire file)

const PAGE_SIZE = 10; 

const summaryCardStyle = {
  background: '#fff',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '1.5rem',
  boxShadow: '0 1px 3px 0 rgba(0,0,0,0.05)',
  textAlign: 'center'
};
const summaryContainerStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(4, 1fr)',
  gap: '1rem',
  marginBottom: '2rem'
};
const problemTableContainerStyle = {
  background: '#fff',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  boxShadow: '0 1px 3px 0 rgba(0,0,0,0.05)',
  overflow: 'hidden'
};
const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
};
const thStyle = {
  padding: '0.75rem 1.5rem',
  textAlign: 'left',
  background: '#f9fafb',
  borderBottom: '1px solid #e5e7eb',
  color: '#4b5563',
  fontSize: '0.875rem',
  fontWeight: '600',
  cursor: 'pointer' 
};
const tdStyle = {
  padding: '1rem 1.5rem',
  borderBottom: '1px solid #e5e7eb',
  color: '#111827',
  verticalAlign: 'top'
};
const lastTdStyle = {
  ...tdStyle,
  borderBottom: 'none'
};
const filterContainerStyle = {
  display: 'flex',
  gap: '1.5rem',
  marginBottom: '1rem',
  padding: '1.5rem',
  background: '#fff',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  alignItems: 'center' 
};
const inputStyle = {
  width: '100%',
  padding: '0.75rem 1rem',
  fontSize: '1rem',
  borderRadius: '6px',
  border: '1px solid #d1d5db'
};
const selectStyle = {
  ...inputStyle,
  width: '300px'
};
const difficultyFilterContainerStyle = {
  display: 'flex',
  gap: '1rem',
  alignItems: 'center',
  paddingLeft: '1.5rem'
};
const checkboxLabelStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.5rem',
  cursor: 'pointer',
  fontWeight: '500'
};
const paginationContainerStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '1rem 1.5rem',
  background: '#fff',
  borderTop: '1px solid #e5e7eb',
  marginTop: '1.5rem',
  borderRadius: '8px'
};
const paginationButtonStyle = {
  padding: '0.5rem 1rem',
  border: '1px solid #d1d5db',
  borderRadius: '6px',
  background: '#fff',
  fontWeight: '600',
  cursor: 'pointer'
};
const tagStyle = {
  display: 'inline-block',
  background: '#e0e7ff', // Simple, consistent blue tag
  color: '#4338ca',
  padding: '0.25rem 0.75rem',
  borderRadius: '99px',
  fontSize: '0.875rem',
  fontWeight: '500',
  marginRight: '0.5rem',
  marginBottom: '0.5rem' 
};

const getDifficultyColor = (difficulty) => {
  switch (difficulty) {
    case 'Easy': return '#22c55e';
    case 'Medium': return '#f59e0b';
    case 'Hard': return '#ef4444';
    default: return '#6b7280';
  }
};


function Dashboard({ solvedProblems, summaryStats }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('All');
  const [sortConfig, setSortConfig] = useState({ key: 'submittedDate', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const [difficultyFilters, setDifficultyFilters] = useState({
    Easy: true,
    Medium: true,
    Hard: true,
  });
  
  const handleDifficultyChange = (e) => {
    const { name, checked } = e.target;
    setDifficultyFilters(prevFilters => ({
      ...prevFilters,
      [name]: checked,
    }));
    setCurrentPage(1); 
  };
  
  const allTopics = useMemo(() => {
    const topics = new Set();
    solvedProblems.forEach(problem => {
      problem.all_topics.forEach(tag => topics.add(tag));
    });
    return ['All', ...[...topics].sort()];
  }, [solvedProblems]);

  const filteredProblems = useMemo(() => {
    let problems = [...solvedProblems];

    if (searchTerm) {
      problems = problems.filter(p => 
        p.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedTopic !== 'All') {
      problems = problems.filter(p =>
        p.all_topics.includes(selectedTopic)
      );
    }
    
    problems = problems.filter(p => difficultyFilters[p.difficulty]);
    
    problems.sort((a, b) => {
      let aVal = a[sortConfig.key];
      let bVal = b[sortConfig.key];

      if (sortConfig.key === 'difficulty') {
        const order = { 'Easy': 1, 'Medium': 2, 'Hard': 3 };
        aVal = order[aVal] || 0;
        bVal = order[bVal] || 0;
      }
      
      if (aVal < bVal) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aVal > bVal) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });

    return problems;
  }, [solvedProblems, searchTerm, selectedTopic, sortConfig, difficultyFilters]); 
  
  const paginatedProblems = useMemo(() => {
    const startIndex = (currentPage - 1) * PAGE_SIZE;
    const endIndex = startIndex + PAGE_SIZE;
    return filteredProblems.slice(startIndex, endIndex);
  }, [filteredProblems, currentPage]);

  const totalPages = Math.ceil(filteredProblems.length / PAGE_SIZE);

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };
  
  const getSortArrow = (key) => {
    if (sortConfig.key !== key) return ' ';
    return sortConfig.direction === 'asc' ? ' ▲' : ' ▼';
  }

  return (
    <div>
      {/* --- 1. SUMMARY CARDS (Unchanged) --- */}
      {summaryStats && (
        <div style={summaryContainerStyle}>
           <div style={summaryCardStyle}>
            <h3 style={{margin: '0 0 0.5rem 0', color: '#111827'}}>Total Solved</h3>
            <span style={{fontSize: '2rem', fontWeight: 'bold'}}>{summaryStats.total}</span>
          </div>
          <div style={summaryCardStyle}>
            <h3 style={{margin: '0 0 0.5rem 0', color: getDifficultyColor('Easy')}}>Easy</h3>
            <span style={{fontSize: '2rem', fontWeight: 'bold'}}>{summaryStats.Easy}</span>
          </div>
          <div style={summaryCardStyle}>
            <h3 style={{margin: '0 0 0.5rem 0', color: getDifficultyColor('Medium')}}>Medium</h3>
            <span style={{fontSize: '2rem', fontWeight: 'bold'}}>{summaryStats.Medium}</span>
          </div>
          <div style={summaryCardStyle}>
            <h3 style={{margin: '0 0 0.5rem 0', color: getDifficultyColor('Hard')}}>Hard</h3>
            <span style={{fontSize: '2rem', fontWeight: 'bold'}}>{summaryStats.Hard}</span>
          </div>
        </div>
      )}
      
      {/* --- 2. FILTERS & SEARCH (Unchanged) --- */}
      <div style={filterContainerStyle}>
        <input 
          type="text"
          placeholder="Search by problem name..."
          style={inputStyle}
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1); 
          }}
        />
        <select
          style={selectStyle}
          value={selectedTopic}
          onChange={(e) => {
            setSelectedTopic(e.target.value);
            setCurrentPage(1); 
          }}
        >
          {allTopics.map(topic => (
            <option key={topic} value={topic}>{topic}</option>
          ))}
        </select>
      </div>

      <div style={{...filterContainerStyle, justifyContent: 'center', marginTop: 0}}>
         <div style={difficultyFilterContainerStyle}>
          {['Easy', 'Medium', 'Hard'].map(difficulty => (
            <label key={difficulty} style={checkboxLabelStyle}>
              <input
                type="checkbox"
                name={difficulty}
                checked={difficultyFilters[difficulty]}
                onChange={handleDifficultyChange}
                style={{width: '1.25rem', height: '1.25rem'}}
              />
              <span style={{color: getDifficultyColor(difficulty)}}>{difficulty}</span>
            </label>
          ))}
        </div>
      </div>

      {/* --- 3. PROBLEM LIST TABLE --- */}
      <div style={problemTableContainerStyle}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle} onClick={() => requestSort('title')}>
                Problem{getSortArrow('title')}
              </th>
              <th style={thStyle} onClick={() => requestSort('difficulty')}>
                Difficulty{getSortArrow('difficulty')}
              </th>
              <th style={thStyle}>Tags</th>
              <th style={thStyle} onClick={() => requestSort('submittedDate')}>
                Solved On{getSortArrow('submittedDate')}
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedProblems.map((problem, index) => {
              const isLastRow = index === paginatedProblems.length - 1;
              const rowTdStyle = isLastRow ? lastTdStyle : tdStyle;
              
              return (
                <tr key={problem._id}>
                  <td style={rowTdStyle}>
                    <a 
                      href={problem.link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{color: '#007bff', fontWeight: '600'}}
                    >
                      {problem.title}
                    </a>
                  </td>
                  <td style={rowTdStyle}>
                    <span style={{color: getDifficultyColor(problem.difficulty), fontWeight: '600'}}>
                      {problem.difficulty}
                    </span>
                  </td>
                  
                  {/* --- THIS IS THE SIMPLIFIED LOGIC --- */}
                  <td style={rowTdStyle}>
                    {problem.all_topics.map(tag => (
                      <span key={tag} style={tagStyle}>{tag}</span>
                    ))}
                  </td>
                  
                  <td style={rowTdStyle}>
                    {problem.submittedDate.split(' ')[0]}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* --- 4. PAGINATION CONTROLS (Unchanged) --- */}
      <div style={paginationContainerStyle}>
        <div>
          <span style={{color: '#4b5563', fontWeight: '500'}}>
            Page {currentPage} of {totalPages} (Total: {filteredProblems.length} problems)
          </span>
        </div>
        <div style={{display: 'flex', gap: '0.5rem'}}>
          <button 
            style={paginationButtonStyle}
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <button 
            style={paginationButtonStyle}
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
        </div>
      </div>

    </div>
  );
}

export default Dashboard;