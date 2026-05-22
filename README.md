# LeetBuddy - Company-Focused Interview Prep Tracker

A full-stack web application that helps developers prepare for technical interviews by tracking LeetCode progress across company-specific problem sets with intelligent study plan generation.

## Features

### Core Functionality
- **Company-Specific Problem Banks** - Browse 3000+ LeetCode problems organized by company (Google, Amazon, Meta, etc.)
- **Smart Plan Generator** - AI-driven study plans filtered by difficulty, solved status, and frequency
- **Progress Tracking** - Real-time sync with your LeetCode account via API integration
- **Readiness Score** - Calculate interview readiness percentage per company based on top 120 problems
- **Spaced Repetition** - Review system for previously solved problems
- **Multi-User Support** - Each user has isolated data with secure authentication

### Authentication & Security
- **JWT-based Authentication** - Secure login with access tokens (15min) and refresh tokens (7 days)
- **Password Encryption** - Bcrypt hashing with cost factor 12
- **Credential Encryption** - LeetCode session tokens encrypted with Fernet symmetric encryption
- **Protected Routes** - All API endpoints require valid JWT tokens
- **Rate Limiting** - 5 req/min on auth endpoints, 200/day globally
- **CORS Protection** - Restricted origins with credential support

## Tech Stack

**Backend:**
- Flask (Python 3.13+)
- MongoDB Atlas (NoSQL database)
- PyJWT (JSON Web Tokens)
- Bcrypt (Password hashing)
- Cryptography (Fernet encryption)
- Flask-CORS & Flask-Limiter

**Frontend:**
- React 19 with Hooks
- React Router v6
- Axios (HTTP client with interceptors)
- Tailwind CSS
- Framer Motion (animations)

**Infrastructure:**
- Docker & Docker Compose
- MongoDB Atlas (Cloud database)

## Quick Start

### Prerequisites
```bash
# Backend
Python 3.13+
pip

# Frontend
Node.js 16+
npm

# Database
MongoDB Atlas account (free tier works)
```

### 1. Clone Repository
```bash
git clone <repository-url>
cd leetcode_tracker-main
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env and add your MongoDB URI and generate keys:
# JWT_SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))"
# ENCRYPTION_KEY: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Start backend server
python app.py
```

Backend runs on: `http://localhost:5000`

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend runs on: `http://localhost:3000`

### 4. Create Your Account
1. Navigate to `http://localhost:3000`
2. Click "Register here"
3. Fill in:
   - Email
   - Username (use existing username if migrating data)
   - Password (min 8 chars, uppercase, lowercase, digit)
4. Optional: Add LeetCode credentials for automatic sync
5. Login with your credentials

## Environment Variables

### Backend (.env)
```env
# MongoDB Configuration
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0
DB_NAME=new_lp

# JWT Authentication (generate secure keys)
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_REFRESH_SECRET_KEY=your_jwt_refresh_secret_key_here

# Encryption Key (generate with Fernet)
ENCRYPTION_KEY=your_encryption_key_here

# Application
FLASK_ENV=development
FRONTEND_URL=http://localhost:3000,http://localhost:3005
```

### Frontend (package.json)
```json
{
  "proxy": "http://localhost:5000"
}
```

## Project Structure

```
leetcode_tracker-main/
├── backend/
│   ├── routes/
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── summary.py        # User statistics
│   │   ├── companies.py      # Company data & smart plans
│   │   └── problems.py       # Problem search & review
│   ├── middleware/
│   │   └── auth.py           # JWT authentication decorator
│   ├── utils/
│   │   ├── db.py             # MongoDB connection
│   │   ├── crypto.py         # Encryption utilities
│   │   ├── validation.py     # Input validation
│   │   └── errors.py         # Error handlers
│   ├── services/
│   │   ├── leetcode_client.py # LeetCode GraphQL API
│   │   └── queries.py        # GraphQL queries
│   ├── scripts/
│   │   └── migrate_existing_user.py # Data migration
│   ├── app.py                # Flask application
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
├── frontend/
│   ├── src/
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx    # Authentication state
│   │   ├── pages/
│   │   │   ├── Login.jsx          # Login page
│   │   │   ├── Register.jsx       # Registration page
│   │   │   ├── Dashboard.jsx      # Main dashboard
│   │   │   ├── Companies.jsx      # Company list
│   │   │   ├── CompanyView.jsx    # Company detail & plans
│   │   │   └── Review.jsx         # Spaced repetition
│   │   ├── components/
│   │   │   ├── Navbar.jsx         # Navigation bar
│   │   │   ├── ProtectedRoute.jsx # Route guard
│   │   │   ├── CompanyCard.jsx    # Company card
│   │   │   ├── StatCard.jsx       # Statistics card
│   │   │   └── ProblemRow.jsx     # Problem display
│   │   ├── utils/
│   │   │   └── api.js             # Axios client with interceptors
│   │   ├── App.js                 # Main app with routing
│   │   └── index.js               # Entry point
│   ├── package.json          # Node dependencies
│   └── tailwind.config.js    # Tailwind CSS config
├── docker-compose.yml        # Docker orchestration
└── README.md                 # This file
```

## API Endpoints

### Authentication
```http
POST   /api/auth/register      # Register new user
POST   /api/auth/login         # Login and get tokens
POST   /api/auth/refresh       # Refresh access token
POST   /api/auth/logout        # Logout (clear cookies)
GET    /api/auth/me            # Get current user (protected)
```

### Companies & Problems
```http
GET    /api/summary            # User statistics (protected)
GET    /api/insights           # Topic insights (protected)
GET    /api/companies/top      # Top companies with readiness (protected)
GET    /api/companies/<name>   # Company problems (protected)
POST   /api/companies/<name>/smart_plan  # Generate study plan (protected)
GET    /api/problems/search    # Search problems (protected)
GET    /api/review/today       # Daily review list (protected)
```

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique),
  password_hash: String,
  username: String (unique),
  leetcode_username: String,
  leetcode_session_encrypted: String,
  leetcode_csrf_encrypted: String,
  ingestion_status: String,
  last_ingested_at: Number,
  created_at: Number,
  updated_at: Number
}
```

### Problems Master Collection
```javascript
{
  _id: String (problem slug),
  title: String,
  difficulty: String,
  companies: [String],
  topics: [String],
  num_occur: Number,
  acRate: Number,
  paidOnly: Boolean
}
```

### User Solved Collection (archive_solved_{username})
```javascript
{
  slug: String,
  title: String,
  archived_at: Number,
  updated_at: Number
}
```

## Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Access:
# Frontend: http://localhost:3005
# Backend: http://localhost:5001
```

## Authentication Flow

1. **Registration**: User provides email, username, password → Backend hashes password with bcrypt → User document created in MongoDB
2. **Login**: User provides credentials → Backend verifies password → Returns JWT access token (15min) and httpOnly refresh token (7 days)
3. **Protected Requests**: Frontend includes `Authorization: Bearer <token>` header → Backend validates JWT → Request processed
4. **Token Refresh**: Access token expires → Frontend receives 401 → Automatically calls `/auth/refresh` with refresh token cookie → New access token issued → Original request retried
5. **Logout**: User clicks logout → Frontend calls `/auth/logout` → Refresh token cookie cleared → User redirected to login

## Security Best Practices

✅ Passwords hashed with bcrypt (cost factor 12)  
✅ JWTs with short expiry (15 minutes)  
✅ HttpOnly cookies for refresh tokens (XSS protection)  
✅ LeetCode credentials encrypted with Fernet  
✅ Rate limiting on authentication endpoints  
✅ CORS restricted to specific origins  
✅ Input validation on all user inputs  
✅ SQL injection protection (NoSQL with parameterized queries)  
✅ Environment variables for sensitive data  

## Migration from Single-User to Multi-User

If you have existing data under username "nandhan_rao":

```bash
cd backend
python scripts/migrate_existing_user.py
```

Follow prompts to:
1. Set email and password
2. Optionally add LeetCode credentials
3. Link existing solved problems collection

## Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.13+

# Reinstall dependencies
pip install -r requirements.txt

# Check MongoDB connection
# Verify MONGO_URI in .env is correct
```

**Frontend won't load:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check proxy configuration in package.json
```

**Login fails:**
```bash
# Check backend is running on port 5000
curl http://localhost:5000/api/auth/me

# Check proxy in frontend/package.json
"proxy": "http://localhost:5000"

# Open browser console (F12) for detailed errors
```

**MongoDB connection issues:**
- Verify IP whitelist in MongoDB Atlas (allow your IP or 0.0.0.0/0 for testing)
- Check username/password in MONGO_URI
- Ensure database name matches DB_NAME in .env

## Performance Optimization

- **Database Indexes**: email (unique), username (unique), companies, difficulty, topics
- **API Caching**: Browser cache with ETag support
- **Lazy Loading**: React Router code splitting
- **Connection Pooling**: MongoDB connection reuse
- **Rate Limiting**: Prevents API abuse

## Future Enhancements

- [ ] Real spaced repetition algorithm (SM-2)
- [ ] Progress charts and analytics
- [ ] Company comparison tool
- [ ] Daily challenges
- [ ] Social features (study groups)
- [ ] Mobile app (React Native)
- [ ] LeetCode webhook integration for real-time sync
- [ ] OAuth login (Google, GitHub)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is open source and available for educational purposes.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

---

**Built with ❤️ for interview preparation**
