import { useState, useEffect } from 'react';
import axios from 'axios';

// Your Flask API is running on this address
const API_URL = "http://127.0.0.1:5000";

function App() {
  // We'll use state to store our data
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // This "useEffect" hook runs once when the component loads
  useEffect(() => {
    // Define an async function to fetch the data
    const fetchProblems = async () => {
      try {
        setLoading(true);
        // Use axios to call your Flask API
        const response = await axios.get(`${API_URL}/api/problems/all`);
        
        // Save the data from the API into our state
        setProblems(response.data.data);
        setError(null);
        
      } catch (err) {
        // Handle any errors
        console.error("Error fetching data:", err);
        setError("Failed to fetch data from the server.");
      } finally {
        setLoading(false);
      }
    };

    // Call the function
    fetchProblems();
  }, []); // The empty array [] means "only run this once"

  // Render the component's HTML (JSX)
  return (
    <div className="App" style={{ padding: '2rem' }}>
      <h1>LeetCode Revision Dashboard</h1>
      <hr />
      
      {/* Show a loading message */}
      {loading && <p>Loading data from Flask...</p>}
      
      {/* Show an error message if something broke */}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {/* Show the data when it's loaded */}
      {!loading && !error && (
        <div>
          <h2>🚀 Connection Successful!</h2>
          <p>
            Successfully fetched <strong>{problems.length}</strong> solved problems from your MongoDB database via Flask.
          </p>
          
          <h3>Sample Data:</h3>
          <pre style={{ background: '#f4f4f4', padding: '1rem', borderRadius: '8px' }}>
            {/* Just show the first problem as a test */}
            {JSON.stringify(problems[0], null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;