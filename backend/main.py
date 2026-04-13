import asyncio
import json
import os
import sys
import httpx
import re
import bcrypt
import jwt
import tiktoken
import redis
import shutil
import subprocess
import socket
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import base64
import io

# Third-party imports
from google import genai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
from pptx import Presentation
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from prometheus_fastapi_instrumentator import Instrumentator

# Optional imports with fallbacks
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# ============================================================================
# CONFIGURATION & ENVIRONMENT SETUP
# ============================================================================

# Load Gemini API Key
GEMINI_KEY = ""
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "GEMINI_API_KEY=" in line:
                GEMINI_KEY = line.strip().split("=", 1)[1].strip()
                break

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # SQLite fallback for local development
    DATABASE_URL = "sqlite:///./youth_sexuality_hub.db"
    print(f"⚠️ WARNING: DATABASE_URL not set, using SQLite: {DATABASE_URL}")

# Fix Railway's postgres:// URL format
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Redis Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# JWT Configuration
SECRET_KEY = os.environ.get("JWT_SECRET", "super_secret_enterprise_key_2026_change_this_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="YouthSexualityHub - AI Consultant & Educator",
    version="1.0.0",
    description="Accurate, scientifically-grounded sexuality education for young adults"
)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

def get_allowed_origins():
    """Get allowed origins from environment or use defaults"""
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",")]
    
    # Default origins including Vercel preview URLs
    return [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://youth-sexuality-hub-frontend.vercel.app",
        "https://youth-sexuality-hub-fron-git-349d66-mayintake351-5529s-projects.vercel.app",
        "https://youth-sexuality-hub-frontend-adhmgo4ak.vercel.app",
        "https://youth-hub-backend-production.up.railway.app"
    ]

# Add CORS middleware with regex support for Vercel preview URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_origin_regex=r"https://youth-sexuality-hub.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# ============================================================================
# DATABASE SETUP
# ============================================================================

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy Base class
class Base(DeclarativeBase):
    pass

# Redis cache connection
try:
    cache = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=5)
    # Test connection
    cache.ping()
    print("✅ Redis connected successfully")
except Exception as e:
    print(f"⚠️ Redis connection failed: {e}")
    cache = None

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    plan_name = Column(String)
    stripe_id = Column(String, unique=True)
    active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class UsageLog(Base):
    __tablename__ = "usage_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    tokens_used = Column(Integer, default=0)
    model = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ArtifactVersion(Base):
    __tablename__ = "artifact_versions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    filename = Column(String)
    content = Column(String)
    commit_message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    event_date = Column(DateTime)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class PeriodTracker(Base):
    __tablename__ = "period_tracker"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    intensity = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SymptomLog(Base):
    __tablename__ = "symptom_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    log_date = Column(DateTime, default=datetime.utcnow)
    mood = Column(String)
    energy = Column(Integer)
    symptoms = Column(String)
    notes = Column(String, nullable=True)

# ============================================================================
# PYDANTIC MODELS (Request/Response)
# ============================================================================

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class CalendarEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: datetime
    category: str

class PeriodTrackerCreate(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None
    intensity: Optional[str] = None
    notes: Optional[str] = None

class SymptomLogCreate(BaseModel):
    mood: str
    energy: int
    symptoms: str
    notes: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    gemini: str

# ============================================================================
# MONITORING & OBSERVABILITY
# ============================================================================

Instrumentator().instrument(app).expose(app)

# ============================================================================
# CONSTANTS & GLOBAL STATE
# ============================================================================

MODELS = [
    "models/gemini-2.0-flash-exp",  # Fastest, most reliable
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro",
    "models/gemini-2.5-pro-exp-03-25"
]

LOCAL_MODEL = "gemma3:1b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", Path(__file__).parent.parent))
OUTPUT_ROOT = PROJECT_ROOT / "output"
KNOWLEDGE_FILE = PROJECT_ROOT / "persistent_brain.json"

# Create output directory
if not OUTPUT_ROOT.exists():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

# Session storage
session_memories: Dict[str, List[Dict[str, str]]] = {}
session_knowledge: Dict[str, str] = {}
session_sources: Dict[str, List[str]] = {}
active_servers: Dict[str, subprocess.Popen] = {}

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
if not GEMINI_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY not set. Falling back to local models only.")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def estimate_tokens(text: str) -> int:
    """Estimate token count for usage tracking"""
    try:
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(enc.encode(text))
    except Exception:
        return len(text) // 4

def load_persistence():
    """Load persistent knowledge from disk"""
    global session_knowledge, session_sources
    if KNOWLEDGE_FILE.exists():
        try:
            data = json.loads(KNOWLEDGE_FILE.read_text(encoding="utf-8"))
            session_knowledge = data.get("knowledge", {})
            session_sources = data.get("sources", {})
            print(f"✅ Loaded knowledge for {len(session_knowledge)} sessions")
        except Exception as e:
            print(f"⚠️ Failed to load persistence: {e}")

def save_persistence():
    """Save knowledge to disk"""
    try:
        KNOWLEDGE_FILE.write_text(
            json.dumps({
                "knowledge": session_knowledge,
                "sources": session_sources
            }, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"⚠️ Failed to save persistence: {e}")

def get_project_index(session_id: str) -> str:
    """Get list of files in session workspace"""
    session_dir = OUTPUT_ROOT / session_id
    if not session_dir.exists():
        return "Empty Workspace"
    
    files = [
        f.name for f in session_dir.iterdir()
        if f.is_file() and f.name not in ["server.log", "ecommerce.db", "elearning.db"]
    ]
    
    if not files:
        return "No generated files yet."
    
    return "CURRENT WORKSPACE FILES: " + ", ".join(files)

def get_expert_system_prompt(session_id: str, knowledge: str = "") -> str:
    """Generate the system prompt for the AI"""
    workspace_context = get_project_index(session_id)
    knowledge_context = ""
    
    if knowledge:
        knowledge_context = f"""
--- EDUCATIONAL KNOWLEDGE BASE ---
{knowledge[-100000:]}
----------------------
"""
    
    return f"""You are the Lead Youth Sexuality Consultant & Educator for YouthSexualityHub.

CORE MISSION:
Provide accurate, scientifically-grounded, and empathetic information regarding sexuality, sexual health, identity, and relationships for young adults. Maintain a safe, non-judgmental, and confidential space.

CRITICAL PRINCIPLES:
1. EMPATHY FIRST: Use supportive, inclusive language. Avoid medical jargon unless explaining it simply.
2. PRIVACY & SAFETY: Never ask for real names or identifiable locations.
3. BOUNDARIES: If a user shares something suggesting immediate danger, provide professional resources/hotlines.
4. EVIDENCE-BASED: Cite reputable sources like WHO, CDC, Planned Parenthood when appropriate.
5. AGE-APPROPRIATE: Tailor responses to young adults (16-25).

CAPABILITIES:
1. EDUCATIONAL CONTENT: Generate summaries, guides, Q&A, and interactive learning materials.
2. CALENDAR MANAGEMENT: Help users organize health appointments and track cycles.
3. HEALTH TRACKING: Support period tracking, symptom logging, and wellness monitoring.
4. RESOURCE SHARING: Provide links to verified health resources and support services.

CALENDAR AWARENESS:
- You have access to the user's personal health calendar.
- Reference their calendar when asked about reminders or upcoming events.
- Suggest adding important dates to their calendar.

WORKSPACE CONTEXT:
{workspace_context}
{knowledge_context}

IMPORTANT: Always prioritize user safety and well-being. If you're unsure about something, acknowledge it and guide users to professional healthcare providers."""

def log_usage(session_id: str, prompt_text: str, response_text: str, model_name: str):
    """Log token usage to database"""
    try:
        tokens = estimate_tokens(prompt_text) + estimate_tokens(response_text)
        db = SessionLocal()
        new_log = UsageLog(
            session_id=session_id,
            tokens_used=tokens,
            model=model_name
        )
        db.add(new_log)
        db.commit()
        db.close()
    except Exception as e:
        print(f"⚠️ Usage tracking error: {e}")

def profile_data(filename: str, content: str) -> str:
    """Create a profile summary of uploaded data"""
    try:
        lines = content.split('\n')
        header = lines[0] if lines else ""
        sample = "\n".join(lines[1:6]) if len(lines) > 1 else ""
        return f"FILE: {filename}\nHEADER: {header}\nSAMPLE DATA:\n{sample}"
    except Exception:
        return f"FILE: {filename} (Summary unavailable)"

# ============================================================================
# AI MODEL CALLING FUNCTIONS
# ============================================================================

async def call_ollama(prompt: str) -> tuple[str, str]:
    """Call local Ollama model"""
    try:
        async with httpx.AsyncClient(timeout=120.0, trust_env=False) as client:
            resp = await client.post(OLLAMA_URL, json={
                "model": LOCAL_MODEL,
                "prompt": prompt,
                "stream": False
            })
            
            if resp.status_code != 200:
                return f"Local AI error ({resp.status_code}). Please ensure Ollama is running.", "OFFLINE"
            
            data = resp.json()
            return data.get("response", "Model returned no data."), LOCAL_MODEL
    except Exception as e:
        return f"Local AI error: {str(e)[:100]}", "OFFLINE"

async def call_llm(prompt: str, session_id: str, websocket: WebSocket = None) -> tuple[str, str]:
    """Main LLM calling function with fallback chain"""
    
    # Get user context from database
    db = SessionLocal()
    try:
        calendar_events = db.query(CalendarEvent).filter(
            CalendarEvent.session_id == session_id
        ).order_by(CalendarEvent.event_date).limit(10).all()
        
        period_logs = db.query(PeriodTracker).filter(
            PeriodTracker.session_id == session_id
        ).order_by(PeriodTracker.start_date.desc()).limit(5).all()
    finally:
        db.close()
    
    # Build context
    context_data = ""
    if calendar_events:
        context_data += "\n\n--- USER CALENDAR ---\n"
        context_data += "\n".join([
            f"- {e.event_date.strftime('%Y-%m-%d')}: {e.title} ({e.category})"
            for e in calendar_events
        ])
    
    if period_logs:
        context_data += "\n\n--- HEALTH LOGS (PERIODS) ---\n"
        context_data += "\n".join([
            f"- Started: {p.start_date.strftime('%Y-%m-%d')}, Intensity: {p.intensity or 'N/A'}"
            for p in period_logs
        ])
    
    # Get knowledge base
    knowledge = session_knowledge.get(session_id, "")
    system_prompt = get_expert_system_prompt(session_id, knowledge)
    
    # Initialize session memory
    if session_id not in session_memories:
        session_memories[session_id] = []
    
    # Add user message with context
    enriched_prompt = prompt + context_data
    session_memories[session_id].append({"role": "user", "content": enriched_prompt})
    
    # Keep history manageable
    history = session_memories[session_id][-15:]
    
    # Try Gemini models
    if client:
        # Convert to Gemini format
        contents = []
        for m in history:
            role = "model" if m["role"] == "assistant" else m["role"]
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        
        for model_name in MODELS:
            try:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=model_name,
                    contents=contents,
                    config={
                        "system_instruction": system_prompt,
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "max_output_tokens": 4096
                    }
                )
                
                ai_text = response.text
                session_memories[session_id].append({"role": "assistant", "content": ai_text})
                
                # Log usage asynchronously
                asyncio.create_task(
                    asyncio.to_thread(log_usage, session_id, str(contents), ai_text, model_name)
                )
                
                return ai_text, model_name
                
            except Exception as e:
                print(f"[GEMINI ERROR] {model_name}: {str(e)[:100]}")
                continue
    
    # Fallback to Ollama
    full_context = f"SYSTEM: {system_prompt}\n\n"
    full_context += "\n".join([f"{m['role']}: {m['content']}" for m in history])
    
    ai_text, model_used = await call_ollama(full_context)
    session_memories[session_id].append({"role": "assistant", "content": ai_text})
    
    # Log usage
    asyncio.create_task(
        asyncio.to_thread(log_usage, session_id, full_context, ai_text, model_used)
    )
    
    return ai_text, model_used

# ============================================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        print(f"✅ Client connected to session {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        print(f"👋 Client disconnected from session {session_id}")
    
    async def send_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"⚠️ Failed to send message: {e}")
    
    async def broadcast(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            # Clean up dead connections
            for conn in disconnected:
                self.active_connections[session_id].remove(conn)

manager = ConnectionManager()

# ============================================================================
# DATABASE DEPENDENCY
# ============================================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# LIFECYCLE EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting YouthSexualityHub Backend...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
    
    # Load persistent knowledge
    load_persistence()
    
    # Check Gemini API
    if client:
        print("✅ Gemini API client initialized")
    else:
        print("⚠️ Gemini API not configured - using local models only")
    
    print("✅ Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down...")
    save_persistence()
    
    # Terminate any running servers
    for session_id, proc in active_servers.items():
        try:
            proc.terminate()
            print(f"🛑 Terminated server for session {session_id}")
        except Exception:
            pass

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    # Check database
    db_status = "disconnected"
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception:
        pass
    
    # Check Redis
    redis_status = "disconnected"
    if cache:
        try:
            cache.ping()
            redis_status = "connected"
        except Exception:
            pass
    
    # Check Gemini
    gemini_status = "configured" if client else "not_configured"
    
    return HealthResponse(
        status="ok",
        version="1.0.0",
        database=db_status,
        redis=redis_status,
        gemini=gemini_status
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouthSexualityHub API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.options("/api/auth/login")
async def options_login():
    """CORS preflight for login"""
    return {"message": "OK"}

@app.options("/api/auth/register")
async def options_register():
    """CORS preflight for register"""
    return {"message": "OK"}

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
       new_user = User(
        email=user.email,
        name=user.name,
        username=user.name,  # 🔥 ADD THIS LINE
        hashed_password=get_password_hash(user.password),
        is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate token
        access_token = create_access_token(data={"sub": new_user.email, "user_id": new_user.id})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=new_user.id,
                email=new_user.email,
                name=new_user.name
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login existing user"""
    try:
        # Find user
        db_user = db.query(User).filter(User.email == user.email).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if active
        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Generate token
        access_token = create_access_token(data={"sub": db_user.email, "user_id": db_user.id})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=db_user.id,
                email=db_user.email,
                name=db_user.name
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

# ============================================================================
# CALENDAR ENDPOINTS
# ============================================================================

@app.get("/api/calendar/{session_id}")
async def get_calendar(session_id: str, db: Session = Depends(get_db)):
    """Get calendar events for a session"""
    events = db.query(CalendarEvent).filter(
        CalendarEvent.session_id == session_id
    ).order_by(CalendarEvent.event_date).all()
    
    return events

@app.post("/api/calendar/{session_id}")
async def add_calendar_event(
    session_id: str,
    event: CalendarEventCreate,
    db: Session = Depends(get_db)
):
    """Add a calendar event"""
    try:
        db_event = CalendarEvent(
            session_id=session_id,
            title=event.title,
            description=event.description,
            event_date=event.event_date,
            category=event.category
        )
        
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        return db_event
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add event: {str(e)}"
        )

@app.delete("/api/calendar/event/{event_id}")
async def delete_calendar_event(event_id: int, db: Session = Depends(get_db)):
    """Delete a calendar event"""
    db_event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(db_event)
    db.commit()
    
    return {"status": "success", "message": "Event deleted"}

# ============================================================================
# PERIOD TRACKER ENDPOINTS
# ============================================================================

@app.get("/api/period/{session_id}")
async def get_periods(session_id: str, db: Session = Depends(get_db)):
    """Get period tracking entries"""
    periods = db.query(PeriodTracker).filter(
        PeriodTracker.session_id == session_id
    ).order_by(PeriodTracker.start_date.desc()).all()
    
    return periods

@app.post("/api/period/{session_id}")
async def add_period_entry(
    session_id: str,
    entry: PeriodTrackerCreate,
    db: Session = Depends(get_db)
):
    """Add a period tracking entry"""
    try:
        db_entry = PeriodTracker(
            session_id=session_id,
            start_date=entry.start_date,
            end_date=entry.end_date,
            intensity=entry.intensity,
            notes=entry.notes
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        return db_entry
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add period entry: {str(e)}"
        )

# ============================================================================
# SYMPTOM LOG ENDPOINTS
# ============================================================================

@app.get("/api/symptoms/{session_id}")
async def get_symptoms(session_id: str, db: Session = Depends(get_db)):
    """Get symptom logs"""
    logs = db.query(SymptomLog).filter(
        SymptomLog.session_id == session_id
    ).order_by(SymptomLog.log_date.desc()).all()
    
    return logs

@app.post("/api/symptoms/{session_id}")
async def add_symptom_log(
    session_id: str,
    entry: SymptomLogCreate,
    db: Session = Depends(get_db)
):
    """Add a symptom log"""
    try:
        db_entry = SymptomLog(
            session_id=session_id,
            mood=entry.mood,
            energy=entry.energy,
            symptoms=entry.symptoms,
            notes=entry.notes
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        return db_entry
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add symptom log: {str(e)}"
        )

# ============================================================================
# FILE DOWNLOAD ENDPOINT
# ============================================================================

@app.get("/download/{session_id}")
async def download_session(session_id: str):
    """Download session workspace as ZIP"""
    session_dir = OUTPUT_ROOT / session_id
    
    if not session_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    zip_path = OUTPUT_ROOT / f"{session_id}.zip"
    
    try:
        shutil.make_archive(
            str(OUTPUT_ROOT / session_id),
            'zip',
            str(session_dir)
        )
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"{session_id}_workspace.zip"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create archive: {str(e)}"
        )

# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Main WebSocket endpoint for chat and collaboration"""
    await manager.connect(websocket, session_id)
    
    # Create session directory
    session_dir = OUTPUT_ROOT / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Send initial sources
    await manager.send_message({
        "type": "sources",
        "sources": session_sources.get(session_id, [])
    }, websocket)
    
    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            
            # Handle cursor position broadcasting
            if data.get("type") == "cursor":
                await manager.broadcast(data, session_id)
                continue
            
            # Handle data feed (URLs, files)
            if data.get("type") == "feed":
                content = ""
                title = data.get("filename", "Source")
                
                try:
                    if data["feed_type"] == "url":
                        url = data["content"]
                        headers = {"User-Agent": "Mozilla/5.0"}
                        
                        async with httpx.AsyncClient(
                            headers=headers,
                            follow_redirects=True,
                            timeout=30.0
                        ) as client:
                            resp = await client.get(url)
                            soup = BeautifulSoup(resp.content, "html.parser")
                            
                            for script in soup(["script", "style"]):
                                script.decompose()
                            
                            content = soup.get_text(separator="\n", strip=True)
                            title = url.split("//")[-1].split("/")[0]
                            
                    elif data["feed_type"] == "file":
                        file_data = data["content"].split(",")[1]
                        decoded = base64.b64decode(file_data)
                        
                        if title.lower().endswith(".pdf") and PdfReader:
                            reader = PdfReader(io.BytesIO(decoded))
                            content = "\n".join([
                                p.extract_text() for p in reader.pages if p.extract_text()
                            ])
                        elif title.lower().endswith((".xlsx", ".xls")):
                            df = pd.read_excel(io.BytesIO(decoded))
                            content = df.to_string()
                        elif title.lower().endswith(".csv"):
                            df = pd.read_csv(io.BytesIO(decoded))
                            content = df.to_string()
                        else:
                            content = decoded.decode("utf-8", errors="ignore")
                    
                    if content:
                        # Create profile and store
                        profile = profile_data(title, content)
                        
                        if session_id not in session_sources:
                            session_sources[session_id] = []
                        if title not in session_sources[session_id]:
                            session_sources[session_id].append(title)
                        
                        # Update knowledge base
                        session_knowledge[session_id] = (
                            session_knowledge.get(session_id, "") +
                            f"\n\nSOURCE PROFILE: {profile}\nFULL CONTENT:\n{content}"
                        )[-500000:]
                        
                        # Save to disk
                        save_persistence()
                        
                        # Reset memory with new context
                        session_memories[session_id] = [{
                            "role": "system",
                            "content": get_expert_system_prompt(
                                session_id,
                                session_knowledge[session_id]
                            )
                        }]
                        
                        await manager.send_message({
                            "type": "status",
                            "text": "✅ Information Absorbed!"
                        }, websocket)
                        
                        await manager.send_message({
                            "type": "sources",
                            "sources": session_sources[session_id]
                        }, websocket)
                        
                except Exception as e:
                    await manager.send_message({
                        "type": "status",
                        "text": f"❌ Error: {str(e)[:50]}"
                    }, websocket)
                
                continue
            
            # Handle server start request
            if data.get("type") == "start_server":
                try:
                    # Kill existing server
                    if session_id in active_servers:
                        try:
                            active_servers[session_id].terminate()
                        except:
                            pass
                    
                    # Check port availability
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        if s.connect_ex(('127.0.0.1', 8080)) == 0:
                            await manager.send_message({
                                "type": "status",
                                "text": "⚠️ Port 8080 is busy!"
                            }, websocket)
                            continue
                    
                    # Start server
                    log_path = session_dir / "server.log"
                    log_file = open(log_path, "w", encoding="utf-8")
                    
                    proc = subprocess.Popen(
                        [sys.executable, "main.py"],
                        cwd=session_dir,
                        stdout=log_file,
                        stderr=subprocess.STDOUT,
                        text=True
                    )
                    
                    active_servers[session_id] = proc
                    
                    await asyncio.sleep(2)
                    
                    if proc.poll() is not None:
                        log_file.close()
                        error_output = log_path.read_text(encoding="utf-8")
                        
                        await manager.send_message({
                            "type": "status",
                            "text": "❌ Server Crashed!"
                        }, websocket)
                        
                        await manager.send_message({
                            "type": "result",
                            "role": "assistant",
                            "content": f"Backend server failed to start:\n```\n{error_output[-500:]}\n```",
                            "model_info": "SYSTEM-CHECK"
                        }, websocket)
                    else:
                        await manager.send_message({
                            "type": "status",
                            "text": "✅ Server Started on Port 8080!"
                        }, websocket)
                        log_file.close()
                        
                except Exception as e:
                    await manager.send_message({
                        "type": "status",
                        "text": f"❌ Server Error: {str(e)[:50]}"
                    }, websocket)
                
                continue
            
            # Handle file with message
            user_msg = data.get("message", "")
            
            if data.get("type") == "message_with_file":
                filename = data.get("filename", "data")
                file_content = data.get("file_content", "")
                
                if file_content and "," in file_content:
                    file_data = file_content.split(",")[1]
                    decoded = base64.b64decode(file_data)
                    content = ""
                    
                    try:
                        if filename.lower().endswith(".pdf") and PdfReader:
                            reader = PdfReader(io.BytesIO(decoded))
                            content = "\n".join([
                                p.extract_text() for p in reader.pages if p.extract_text()
                            ])
                        elif filename.lower().endswith((".xlsx", ".xls")):
                            df = pd.read_excel(io.BytesIO(decoded))
                            content = df.to_string()
                        elif filename.lower().endswith(".csv"):
                            df = pd.read_csv(io.BytesIO(decoded))
                            content = df.to_string()
                        else:
                            content = decoded.decode("utf-8", errors="ignore")
                        
                        user_msg = f"ATTACHED DATA ({filename}):\n{content}\n\nUSER REQUEST: {user_msg}"
                    except:
                        pass
            
            # Auto-debug mode
            if data.get("type") == "auto_debug":
                error = data.get("error", "")
                user_msg = f"CRITICAL: Previous code failed with error: {error}. Please diagnose and provide fixed version."
            
            # Generate title for new conversations
            if len(session_memories.get(session_id, [])) <= 1 and client:
                try:
                    resp = await asyncio.to_thread(
                        client.models.generate_content,
                        model="gemini-1.5-flash",
                        contents=f"Generate a short 3-word title for: {user_msg[:100]}"
                    )
                    title = resp.text.strip().replace('"', '')
                    await manager.send_message({
                        "type": "title",
                        "title": title
                    }, websocket)
                except:
                    pass
            
            # Call LLM and respond
            ai_response, model_used = await call_llm(user_msg, session_id, websocket)
            
            await manager.send_message({
                "type": "result",
                "role": "assistant",
                "content": ai_response,
                "model_info": model_used
            }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket, session_id)

@app.websocket("/ws/{session_id}/logs")
async def log_websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming server logs"""
    await websocket.accept()
    
    log_path = OUTPUT_ROOT / session_id / "server.log"
    
    try:
        if not log_path.exists():
            await websocket.send_text("⏳ Waiting for logs...")
            while not log_path.exists():
                await asyncio.sleep(1)
        
        with open(log_path, "r", encoding="utf-8") as f:
            # Send existing logs
            existing = f.read()
            if existing:
                await websocket.send_text(existing)
            
            # Tail new logs
            while True:
                line = f.readline()
                if not line:
                    await asyncio.sleep(0.5)
                    continue
                await websocket.send_text(line)
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"❌ Log WebSocket error: {e}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     YouthSexualityHub - AI Consultant & Educator Backend     ║
╠══════════════════════════════════════════════════════════════╣
║  Starting server on 0.0.0.0:{port}                          ║
║  API Docs: http://localhost:{port}/docs                     ║
║  Health: http://localhost:{port}/api/health                 ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
