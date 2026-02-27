from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import uuid
import random
import asyncio
from contextlib import asynccontextmanager

# Data Models
class User(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    current_level: str = "beginner"
    total_time_spent: int = 0  # minutes

class ModuleProgress(BaseModel):
    user_id: str
    module_id: str
    progress: int = 0  # checkpoints completed
    total_checkpoints: int
    completed: bool = False
    time_spent: int = 0  # minutes
    last_accessed: datetime
    checkpoints_completed: List[str] = []

class TradingSimulatorState(BaseModel):
    user_id: str
    level: str
    balance: float
    initial_balance: float
    portfolio: Dict[str, Dict[str, Any]]  # symbol -> {shares: int, avg_price: float}
    stock_prices: Dict[str, float]
    trade_count: int = 0
    total_pnl: float = 0.0
    created_at: datetime
    last_updated: datetime

class TradeOrder(BaseModel):
    symbol: str
    action: str  # "buy" or "sell"
    quantity: int
    order_type: str = "market"  # "market" or "limit"
    limit_price: Optional[float] = None

class TradeExecution(BaseModel):
    id: str
    user_id: str
    symbol: str
    action: str
    quantity: int
    price: float
    total_value: float
    timestamp: datetime
    order_type: str

# Learning Module Data
MODULES_DATA = {
    # Beginner Modules
    "financial-basics": {"level": "beginner", "title": "Financial Markets Basics", "checkpoints": 6, "duration": 45},
    "asset-classes": {"level": "beginner", "title": "Asset Classes Overview", "checkpoints": 5, "duration": 40},
    "trading-concepts": {"level": "beginner", "title": "Basic Trading Concepts", "checkpoints": 6, "duration": 35},
    "risk-management": {"level": "beginner", "title": "Risk Management Fundamentals", "checkpoints": 7, "duration": 50},
    "first-portfolio": {"level": "beginner", "title": "Building Your First Portfolio", "checkpoints": 8, "duration": 55},
    
    # Intermediate Modules
    "technical-analysis": {"level": "intermediate", "title": "Technical Analysis", "checkpoints": 8, "duration": 60},
    "fundamental-analysis": {"level": "intermediate", "title": "Fundamental Analysis", "checkpoints": 7, "duration": 55},
    "market-psychology": {"level": "intermediate", "title": "Market Psychology", "checkpoints": 6, "duration": 45},
    "sector-analysis": {"level": "intermediate", "title": "Sector Analysis", "checkpoints": 7, "duration": 50},
    "advanced-strategies": {"level": "intermediate", "title": "Advanced Trading Strategies", "checkpoints": 8, "duration": 65},
    
    # Advanced Modules
    "options-derivatives": {"level": "advanced", "title": "Options & Derivatives", "checkpoints": 9, "duration": 70},
    "macro-economics": {"level": "advanced", "title": "Macro Economics", "checkpoints": 8, "duration": 65},
    "ai-quant-strategies": {"level": "advanced", "title": "AI & Quant Strategies", "checkpoints": 10, "duration": 75},
    "portfolio-management": {"level": "advanced", "title": "Advanced Portfolio Management", "checkpoints": 9, "duration": 80},
    "hft": {"level": "advanced", "title": "High-Frequency Trading", "checkpoints": 10, "duration": 85},
}

# Trading Simulator Stock Data
STOCK_DATA = {
    "beginner": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
    "intermediate": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS"],
    "advanced": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "BAC", "XOM", "CVX", "LLY", "ABBV", "PFE", "KO", "PEP", "TMO", "COST", "AVGO", "LIN", "NKE", "ACN", "CRM"]
}

# Initial Stock Prices
INITIAL_PRICES = {
    "AAPL": 175.50, "GOOGL": 142.80, "MSFT": 378.90, "AMZN": 145.30, "TSLA": 248.70,
    "META": 325.40, "NVDA": 485.20, "JPM": 178.60, "JNJ": 162.40, "V": 265.80,
    "PG": 158.90, "UNH": 542.30, "HD": 356.70, "MA": 398.50, "DIS": 92.40,
    "BAC": 34.20, "XOM": 108.60, "CVX": 146.80, "LLY": 568.90, "ABBV": 158.30,
    "PFE": 28.60, "KO": 62.40, "PEP": 178.90, "TMO": 542.60, "COST": 689.30,
    "AVGO": 892.40, "LIN": 425.60, "NKE": 108.90, "ACN": 342.70, "CRM": 256.80
}

# In-memory storage (in production, use a database)
users_db: Dict[str, User] = {}
progress_db: Dict[str, ModuleProgress] = {}
simulator_db: Dict[str, TradingSimulatorState] = {}
trades_db: List[TradeExecution] = []

# Security
security = HTTPBearer()

# Application Lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 ALPHA Finance Backend Starting Up...")
    yield
    # Shutdown
    print("📴 ALPHA Finance Backend Shutting Down...")

# FastAPI App
app = FastAPI(
    title="ALPHA Finance Intelligence Platform",
    description="Backend API for ALPHA Finance Learning and Trading Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper Functions
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    if token not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return users_db[token]

def generate_user_token() -> str:
    return str(uuid.uuid4())

def simulate_price_change(current_price: float) -> float:
    """Simulate realistic stock price movement (-2% to +2%)"""
    change_percent = random.uniform(-0.02, 0.02)
    return round(current_price * (1 + change_percent), 2)

def calculate_portfolio_value(portfolio: Dict[str, Dict[str, Any]], stock_prices: Dict[str, float]) -> float:
    """Calculate total portfolio value"""
    total = 0.0
    for symbol, holdings in portfolio.items():
        if symbol in stock_prices:
            total += holdings["shares"] * stock_prices[symbol]
    return total

# API Endpoints

# Health Check
@app.get("/")
async def root():
    return {"message": "ALPHA Finance API is running", "status": "active", "version": "1.0.0"}

# Authentication
@app.post("/auth/register")
async def register_user(username: str, email: str) -> Dict[str, str]:
    """Register a new user"""
    token = generate_user_token()
    user = User(
        id=token,
        username=username,
        email=email,
        created_at=datetime.now()
    )
    users_db[token] = user
    return {"token": token, "user_id": token, "message": "User registered successfully"}

@app.post("/auth/login")
async def login_user(username: str) -> Dict[str, str]:
    """Login user (simplified - in production, use proper authentication)"""
    # Find user by username
    for token, user in users_db.items():
        if user.username == username:
            return {"token": token, "user_id": token, "message": "Login successful"}
    
    # If not found, register new user
    return await register_user(username, f"{username}@example.com")

# Learning Modules
@app.get("/modules")
async def get_all_modules() -> Dict[str, Any]:
    """Get all available modules"""
    return {"modules": MODULES_DATA}

@app.get("/modules/{level}")
async def get_modules_by_level(level: str) -> Dict[str, Any]:
    """Get modules by skill level"""
    if level not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail="Invalid level")
    
    modules = {k: v for k, v in MODULES_DATA.items() if v["level"] == level}
    return {"level": level, "modules": modules}

@app.get("/modules/{module_id}/details")
async def get_module_details(module_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific module"""
    if module_id not in MODULES_DATA:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {"module_id": module_id, "details": MODULES_DATA[module_id]}

# Progress Tracking
@app.get("/progress/{user_id}")
async def get_user_progress(user_id: str) -> Dict[str, Any]:
    """Get user's progress across all modules"""
    user_progress = {k: v for k, v in progress_db.items() if v.user_id == user_id}
    
    # Calculate overall statistics
    total_modules = len(MODULES_DATA)
    completed_modules = len([p for p in user_progress.values() if p.completed])
    total_time = sum(p.time_spent for p in user_progress.values())
    
    # Calculate level progress
    level_progress = {"beginner": 0, "intermediate": 0, "advanced": 0}
    level_totals = {"beginner": 0, "intermediate": 0, "advanced": 0}
    
    for module_id, module_data in MODULES_DATA.items():
        level = module_data["level"]
        level_totals[level] += 1
        if module_id in user_progress and user_progress[module_id].completed:
            level_progress[level] += 1
    
    return {
        "user_id": user_id,
        "total_modules": total_modules,
        "completed_modules": completed_modules,
        "overall_progress": round((completed_modules / total_modules) * 100, 1),
        "total_time_minutes": total_time,
        "level_progress": level_progress,
        "level_totals": level_totals,
        "modules": user_progress
    }

@app.post("/progress/{user_id}/{module_id}")
async def update_module_progress(
    user_id: str, 
    module_id: str, 
    progress: int,
    time_spent: int = 0,
    checkpoint: Optional[str] = None
) -> Dict[str, Any]:
    """Update user's progress for a specific module"""
    if module_id not in MODULES_DATA:
        raise HTTPException(status_code=404, detail="Module not found")
    
    module_data = MODULES_DATA[module_id]
    progress_key = f"{user_id}_{module_id}"
    
    if progress_key not in progress_db:
        progress_db[progress_key] = ModuleProgress(
            user_id=user_id,
            module_id=module_id,
            progress=progress,
            total_checkpoints=module_data["checkpoints"],
            last_accessed=datetime.now()
        )
    else:
        progress_entry = progress_db[progress_key]
        progress_entry.progress = progress
        progress_entry.time_spent += time_spent
        progress_entry.last_accessed = datetime.now()
        
        if checkpoint and checkpoint not in progress_entry.checkpoints_completed:
            progress_entry.checkpoints_completed.append(checkpoint)
    
    # Check if module is completed
    progress_entry = progress_db[progress_key]
    if progress >= module_data["checkpoints"]:
        progress_entry.completed = True
    
    return {
        "message": "Progress updated successfully",
        "module_id": module_id,
        "progress": progress,
        "completed": progress_entry.completed,
        "time_spent": progress_entry.time_spent
    }

# Trading Simulator
@app.post("/simulator/{user_id}/initialize")
async def initialize_simulator(user_id: str, level: str = "beginner") -> Dict[str, Any]:
    """Initialize trading simulator for a user"""
    if level not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail="Invalid level")
    
    # Set initial balance based on level
    initial_balances = {"beginner": 2000, "intermediate": 5000, "advanced": 10000}
    initial_balance = initial_balances[level]
    
    # Get available stocks for level
    available_stocks = STOCK_DATA[level]
    stock_prices = {symbol: INITIAL_PRICES[symbol] for symbol in available_stocks}
    
    simulator_state = TradingSimulatorState(
        user_id=user_id,
        level=level,
        balance=initial_balance,
        initial_balance=initial_balance,
        portfolio={},
        stock_prices=stock_prices,
        created_at=datetime.now(),
        last_updated=datetime.now()
    )
    
    simulator_db[user_id] = simulator_state
    
    return {
        "message": "Simulator initialized successfully",
        "level": level,
        "initial_balance": initial_balance,
        "available_stocks": available_stocks,
        "stock_prices": stock_prices
    }

@app.get("/simulator/{user_id}/state")
async def get_simulator_state(user_id: str) -> Dict[str, Any]:
    """Get current simulator state for a user"""
    if user_id not in simulator_db:
        raise HTTPException(status_code=404, detail="Simulator not initialized")
    
    state = simulator_db[user_id]
    portfolio_value = calculate_portfolio_value(state.portfolio, state.stock_prices)
    total_value = state.balance + portfolio_value
    pnl = total_value - state.initial_balance
    
    return {
        "user_id": user_id,
        "level": state.level,
        "balance": state.balance,
        "portfolio": state.portfolio,
        "stock_prices": state.stock_prices,
        "portfolio_value": portfolio_value,
        "total_value": total_value,
        "initial_balance": state.initial_balance,
        "pnl": pnl,
        "trade_count": state.trade_count,
        "last_updated": state.last_updated
    }

@app.post("/simulator/{user_id}/trade")
async def execute_trade(user_id: str, order: TradeOrder) -> Dict[str, Any]:
    """Execute a trade order"""
    if user_id not in simulator_db:
        raise HTTPException(status_code=404, detail="Simulator not initialized")
    
    state = simulator_db[user_id]
    
    if order.symbol not in state.stock_prices:
        raise HTTPException(status_code=400, detail="Stock not available")
    
    current_price = state.stock_prices[order.symbol]
    
    # Handle limit orders
    if order.order_type == "limit":
        if order.limit_price is None:
            raise HTTPException(status_code=400, detail="Limit price required for limit orders")
        if (order.action == "buy" and current_price > order.limit_price) or \
           (order.action == "sell" and current_price < order.limit_price):
            raise HTTPException(status_code=400, detail="Market price not favorable for limit order")
        execution_price = order.limit_price
    else:
        execution_price = current_price
    
    total_value = execution_price * order.quantity
    
    # Execute trade
    if order.action == "buy":
        if state.balance < total_value:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        state.balance -= total_value
        if order.symbol not in state.portfolio:
            state.portfolio[order.symbol] = {"shares": 0, "avg_price": 0}
        
        # Update average price
        current_shares = state.portfolio[order.symbol]["shares"]
        current_avg = state.portfolio[order.symbol]["avg_price"]
        new_shares = current_shares + order.quantity
        new_avg = ((current_shares * current_avg) + (order.quantity * execution_price)) / new_shares
        
        state.portfolio[order.symbol] = {
            "shares": new_shares,
            "avg_price": new_avg
        }
    
    elif order.action == "sell":
        if order.symbol not in state.portfolio or state.portfolio[order.symbol]["shares"] < order.quantity:
            raise HTTPException(status_code=400, detail="Insufficient shares")
        
        state.balance += total_value
        state.portfolio[order.symbol]["shares"] -= order.quantity
        
        # Remove from portfolio if no shares left
        if state.portfolio[order.symbol]["shares"] == 0:
            del state.portfolio[order.symbol]
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Record trade
    trade = TradeExecution(
        id=str(uuid.uuid4()),
        user_id=user_id,
        symbol=order.symbol,
        action=order.action,
        quantity=order.quantity,
        price=execution_price,
        total_value=total_value,
        timestamp=datetime.now(),
        order_type=order.order_type
    )
    trades_db.append(trade)
    
    # Update state
    state.trade_count += 1
    state.last_updated = datetime.now()
    
    portfolio_value = calculate_portfolio_value(state.portfolio, state.stock_prices)
    total_value = state.balance + portfolio_value
    pnl = total_value - state.initial_balance
    state.total_pnl = pnl
    
    return {
        "message": "Trade executed successfully",
        "trade": {
            "id": trade.id,
            "symbol": order.symbol,
            "action": order.action,
            "quantity": order.quantity,
            "price": execution_price,
            "total_value": total_value
        },
        "new_balance": state.balance,
        "portfolio": state.portfolio,
        "total_value": total_value,
        "pnl": pnl
    }

@app.get("/simulator/{user_id}/trades")
async def get_trade_history(user_id: str, limit: int = 50) -> Dict[str, Any]:
    """Get trade history for a user"""
    user_trades = [trade for trade in trades_db if trade.user_id == user_id]
    user_trades.sort(key=lambda x: x.timestamp, reverse=True)
    
    return {
        "user_id": user_id,
        "trades": user_trades[:limit],
        "total_trades": len(user_trades)
    }

@app.post("/simulator/{user_id}/update-prices")
async def update_stock_prices(user_id: str) -> Dict[str, Any]:
    """Update stock prices (simulate market movement)"""
    if user_id not in simulator_db:
        raise HTTPException(status_code=404, detail="Simulator not initialized")
    
    state = simulator_db[user_id]
    old_prices = state.stock_prices.copy()
    
    # Update prices with random movements
    for symbol in state.stock_prices:
        state.stock_prices[symbol] = simulate_price_change(state.stock_prices[symbol])
    
    state.last_updated = datetime.now()
    
    return {
        "message": "Stock prices updated",
        "old_prices": old_prices,
        "new_prices": state.stock_prices,
        "timestamp": state.last_updated
    }

# User Management
@app.get("/user/{user_id}")
async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user profile information"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    progress = await get_user_progress(user_id)
    
    return {
        "user": user,
        "progress": progress
    }

@app.put("/user/{user_id}/level")
async def update_user_level(user_id: str, level: str) -> Dict[str, Any]:
    """Update user's current level"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if level not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail="Invalid level")
    
    users_db[user_id].current_level = level
    
    return {
        "message": "User level updated successfully",
        "user_id": user_id,
        "new_level": level
    }

# Statistics and Analytics
@app.get("/analytics/overview")
async def get_platform_analytics() -> Dict[str, Any]:
    """Get platform-wide analytics"""
    total_users = len(users_db)
    total_modules = len(MODULES_DATA)
    total_progress_entries = len(progress_db)
    completed_modules = len([p for p in progress_db.values() if p.completed])
    active_simulators = len(simulator_db)
    total_trades = len(trades_db)
    
    # Level distribution
    level_distribution = {"beginner": 0, "intermediate": 0, "advanced": 0}
    for user in users_db.values():
        level_distribution[user.current_level] += 1
    
    return {
        "total_users": total_users,
        "total_modules": total_modules,
        "total_progress_entries": total_progress_entries,
        "completed_modules": completed_modules,
        "active_simulators": active_simulators,
        "total_trades": total_trades,
        "level_distribution": level_distribution,
        "completion_rate": round((completed_modules / max(total_progress_entries, 1)) * 100, 1)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
