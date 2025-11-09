import React from 'react';
import { Link } from 'react-router-dom';

// Inline styles for simplicity
const navStyle = {
  background: '#fff',
  padding: '0 2rem',
  borderBottom: '1px solid #e5e7eb',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
};

const navLinksStyle = {
  display: 'flex',
  gap: '1.5rem',
  listStyle: 'none',
};

const linkStyle = {
  textDecoration: 'none',
  color: '#374151',
  fontWeight: '600',
  padding: '1.5rem 0',
  display: 'block'
};

const logoStyle = {
  ...linkStyle,
  color: '#007bff',
  fontSize: '1.25rem',
};

function Navbar() {
  return (
    <nav style={navStyle}>
      <Link to="/" style={logoStyle}>
        LeetCode Revision
      </Link>
      <ul style={navLinksStyle}>
        <li>
          <Link to="/" style={linkStyle}>Dashboard</Link>
        </li>
        <li>
          <Link to="/topics" style={linkStyle}>My Weak Topics</Link>
        </li>
      </ul>
    </nav>
  );
}

export default Navbar;