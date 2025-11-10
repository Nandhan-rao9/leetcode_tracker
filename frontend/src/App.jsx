import React, { useState, useEffect, useMemo } from 'react';
import { Routes, Route } from 'react-router-dom';
import axios from 'axios';

// Import your components
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Revision from './pages/Revision';
import Practice from './pages/Practice'; 

// Your Flask API is running on this address
export const API_URL = "http://127.0.0.1:5000";

// Style for the main content area
const mainContentStyle = {
  maxWidth: '1200px',
  margin: '0 auto',
  padding: '2rem'
};

function App() {
  const [allProblems, setAllProblems] = useState([]);
  // const [topicStats, setTopicStats] = useState([]); // <-- REMOVED
  const [summaryStats, setSummaryStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // --- UPDATED: Only fetch 2 endpoints ---
        const [problemsResponse, summaryResponse] = await Promise.all([
          axios.get(`${API_URL}/api/problems/all`),
          // axios.get(`${API_URL}/api/stats/topic-analysis`), // <-- REMOVED
          axios.get(`${API_URL}/api/stats/summary`)
        ]);
        
        setAllProblems(problemsResponse.data.data);
        // setTopicStats(statsResponse.data.data); // <-- REMOVED
        setSummaryStats(summaryResponse.data.data);
        setError(null);
        
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to fetch data from the server.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const allTopicsList = useMemo(() => {
    const topics = new Set();
    allProblems.forEach(problem => {
      problem.all_topics.forEach(tag => topics.add(tag));
    });
    return [...topics].sort(); 
  }, [allProblems]);

  return (
    <div>
      <Navbar />
      <main style={mainContentStyle}>
        {loading && <p>Loading data...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        
        {!loading && !error && (
          <Routes>
            <Route 
              path="/" 
              element={<Dashboard 
                solvedProblems={allProblems} 
                summaryStats={summaryStats}
                allTopics={allTopicsList}
              />} 
            />
            <Route 
              path="/revision" 
              element={<Revision solvedProblems={allProblems} />} 
            />
            {/* <Route axact path="/topics" element={<Topics topicStats={topicStats} />} /> */} {/* <-- REMOVED */}
            <Route 
              path="/practice" 
              element={<Practice allTopics={allTopicsList} />} 
            />
          </Routes>
        )}
      </main>
    </div>
  );
}

export default App;