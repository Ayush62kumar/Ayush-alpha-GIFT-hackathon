# ALPHA Finance Backend - FastAPI

A comprehensive FastAPI backend for the ALPHA Finance Intelligence Platform, supporting learning modules, progress tracking, and trading simulator functionality.

## 🚀 Features

- **User Management**: Registration, authentication, and profile management
- **Learning Modules**: 15 modules across 3 skill levels (Beginner, Intermediate, Advanced)
- **Progress Tracking**: Detailed progress monitoring with checkpoints and time tracking
- **Trading Simulator**: Virtual trading with real-time price simulation
- **Analytics**: Platform-wide statistics and user analytics
- **RESTful API**: Clean, documented API endpoints

## 📋 Prerequisites

- Python 3.8+
- pip package manager

## 🛠️ Installation

1. **Clone the repository** (if not already done)
2. **Navigate to the project directory**
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Backend

### Development Mode
```bash
python main.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🏗️ API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user

### Learning Modules
- `GET /modules` - Get all available modules
- `GET /modules/{level}` - Get modules by skill level
- `GET /modules/{module_id}/details` - Get module details

### Progress Tracking
- `GET /progress/{user_id}` - Get user progress
- `POST /progress/{user_id}/{module_id}` - Update module progress

### Trading Simulator
- `POST /simulator/{user_id}/initialize` - Initialize simulator
- `GET /simulator/{user_id}/state` - Get simulator state
- `POST /simulator/{user_id}/trade` - Execute trade
- `GET /simulator/{user_id}/trades` - Get trade history
- `POST /simulator/{user_id}/update-prices` - Update stock prices

### User Management
- `GET /user/{user_id}` - Get user profile
- `PUT /user/{user_id}/level` - Update user level

### Analytics
- `GET /analytics/overview` - Get platform analytics

## 🏗️ Data Models

### User
```python
{
    "id": "string",
    "username": "string", 
    "email": "string",
    "created_at": "datetime",
    "current_level": "beginner|intermediate|advanced",
    "total_time_spent": "int (minutes)"
}
```

### Module Progress
```python
{
    "user_id": "string",
    "module_id": "string",
    "progress": "int (checkpoints completed)",
    "total_checkpoints": "int",
    "completed": "bool",
    "time_spent": "int (minutes)",
    "last_accessed": "datetime",
    "checkpoints_completed": ["string"]
}
```

### Trading Simulator State
```python
{
    "user_id": "string",
    "level": "beginner|intermediate|advanced",
    "balance": "float",
    "initial_balance": "float",
    "portfolio": {"symbol": {"shares": "int", "avg_price": "float"}},
    "stock_prices": {"symbol": "float"},
    "trade_count": "int",
    "total_pnl": "float",
    "created_at": "datetime",
    "last_updated": "datetime"
}
```

## 💾 Data Storage

Currently uses in-memory storage for development. In production, integrate with:
- PostgreSQL (recommended)
- MongoDB
- MySQL
- Redis (for caching)

## 🔐 Security

- JWT-based authentication (simplified for demo)
- CORS enabled for frontend integration
- Input validation with Pydantic models
- Error handling with proper HTTP status codes

## 🎯 Trading Simulator Features

### Level-Based Accounts
- **Beginner**: $2,000 virtual balance, 5 stocks
- **Intermediate**: $5,000 virtual balance, 15+ stocks, limit orders
- **Advanced**: $10,000 virtual balance, 30+ stocks, professional tools

### Stock Price Simulation
- Realistic price movements (-2% to +2%)
- Real-time price updates
- Market and limit order support

## 📊 Learning Modules Structure

### Beginner Level (5 modules)
1. Financial Markets Basics
2. Asset Classes Overview  
3. Basic Trading Concepts
4. Risk Management Fundamentals
5. Building Your First Portfolio

### Intermediate Level (5 modules)
1. Technical Analysis
2. Fundamental Analysis
3. Market Psychology
4. Sector Analysis
5. Advanced Trading Strategies

### Advanced Level (5 modules)
1. Options & Derivatives
2. Macro Economics
3. AI & Quant Strategies
4. Advanced Portfolio Management
5. High-Frequency Trading

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file:
```env
# Database Configuration (when implementing persistent storage)
DATABASE_URL=postgresql://user:password@localhost/alpha_db

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 🚀 Deployment

### Docker (Recommended)
1. Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build and run:
```bash
docker build -t alpha-backend .
docker run -p 8000:8000 alpha-backend
```

### Cloud Platforms
- **AWS**: Elastic Beanstalk, ECS, or Lambda
- **Google Cloud**: Cloud Run, App Engine
- **Azure**: App Service, Container Instances
- **Heroku**: Direct deployment

## 🧪 Testing

Run the API tests:
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## 📝 Development Notes

- **In-memory storage**: Replace with database for production
- **Authentication**: Simplified for demo, enhance with proper JWT
- **Error handling**: Comprehensive error responses
- **Logging**: Add structured logging for monitoring
- **Rate limiting**: Implement for production use

## 🤝 Integration with Frontend

The backend is designed to work seamlessly with the ALPHA frontend:

1. **Base URL**: `http://localhost:8000`
2. **Authentication**: Include Bearer token in headers
3. **CORS**: Configured for frontend integration
4. **Data Format**: JSON responses with consistent structure

Example frontend request:
```javascript
const response = await fetch('http://localhost:8000/modules', {
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN_HERE',
        'Content-Type': 'application/json'
    }
});
const data = await response.json();
```

## 📞 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the console logs for error details
3. Verify backend is running on correct port
4. Check CORS configuration if frontend can't connect

---

**🚀 Ready to power your ALPHA Finance platform!**
