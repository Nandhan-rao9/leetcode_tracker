import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import axios from 'axios';

// Import your components
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Topics from './pages/Topics';
import Revision from './pages/Revision'; // <-- 1. IMPORT THE NEW PAGE

// Your Flask API is running on this address
export const API_URL = "http://127.0.0.1:5000";

// Style for the main content area
const mainContentStyle = {
  maxWidth: '1200px',
  margin: '0 auto',
  padding: '2rem'
};

function App() {
  // We'll keep all our data here in the main App
  const [allProblems, setAllProblems] = useState([]);
  const [topicStats, setTopicStats] = useState([]);
  const [summaryStats, setSummaryStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // This hook runs once and fetches all our data
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [problemsResponse, statsResponse, summaryResponse] = await Promise.all([
          axios.get(`${API_URL}/api/problems/all`),
          axios.get(`${API_URL}/api/stats/topic-analysis`),
          axios.get(`${API_URL}/api/stats/summary`)
        ]);
        
        setAllProblems(problemsResponse.data.data);
        setTopicStats(statsResponse.data.data);
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
  }, []); // The empty array [] means "only run this once"

  return (
    <div>
      <Navbar />
      <main style={mainContentStyle}>
        {loading && <p>Loading data...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        
        {/* Once data is loaded, render the correct page */}
        {!loading && !error && (
          <Routes>
            <Route 
              path="/" 
              element={<Dashboard solvedProblems={allProblems} summaryStats={summaryStats} />} 
            />
            {/* --- 2. ADD THE NEW ROUTE --- */}
            <Route 
              path="/revision" 
              element={<Revision solvedProblems={allProblems} />} 
            />
            <Route 
              path="/topics" 
              element={<Topics topicStats={topicStats} />} 
            />
          </Routes>
        )}
      </main>
    </div>
  );
}

export default App;