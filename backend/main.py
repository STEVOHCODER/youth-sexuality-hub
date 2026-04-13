import asyncio
import json
import os
import sys
import httpx
from google import genai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from pydantic import BaseModel
from pathlib import Path
import base64
import io
import pandas as pd
from pptx import Presentation
import subprocess
import socket

# Enterprise Additions
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from prometheus_fastapi_instrumentator import Instrumentator
import stripe

try: from bs4 import BeautifulSoup
except ImportError: BeautifulSoup = None
try: from youtube_transcript_api import YouTubeTranscriptApi
except ImportError: YouTubeTranscriptApi = None
try: from pypdf import PdfReader
except ImportError: PdfReader = None

GEMINI_KEY = ""
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "GEMINI_API_KEY=" in line:
                GEMINI_KEY = line.strip().split("=", 1)[1]

app = FastAPI(title="YouthSexualityHub - AI Consultant & Educator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monitoring
Instrumentator().instrument(app).expose(app)

MODELS = [
    "models/gemini-3.1-pro-preview",
    "models/gemini-3-pro-preview",
    "models/gemini-2.5-pro",
    "models/gemini-2.0-flash",
    "models/gemini-1.5-pro",
    "models/gemini-1.5-flash"
]
LOCAL_MODEL = "qwen2.5-coder"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", Path(__file__).parent.parent))
OUTPUT_ROOT = PROJECT_ROOT / "output"
KNOWLEDGE_FILE = PROJECT_ROOT / "persistent_brain.json"

if not OUTPUT_ROOT.exists():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

session_memories: Dict[str, List[Dict[str, str]]] = {}
session_knowledge: Dict[str, str] = {}
session_sources: Dict[str, List[str]] = {}

active_servers: Dict[str, subprocess.Popen] = {}
import redis
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- ENTERPRISE DATABASE SETUP ---
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass

# Redis for high-speed context caching
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
try:
    cache = redis.from_url(REDIS_URL, decode_responses=True)
except:
    cache = None

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    plan_name = Column(String)
    stripe_id = Column(String)
    active = Column(Boolean, default=False)

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
    user_id = Column(Integer)
    session_id = Column(String, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    event_date = Column(DateTime)
    category = Column(String) # e.g., "health", "education", "reminder"
    created_at = Column(DateTime, default=datetime.utcnow)

class PeriodTracker(Base):
    __tablename__ = "period_tracker"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    intensity = Column(String, nullable=True) # e.g., "light", "medium", "heavy"
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    log_date = Column(DateTime, default=datetime.utcnow)
    mood = Column(String)
    energy = Column(Integer)  # 1-10
    symptoms = Column(String)  # comma separated
    notes = Column(String, nullable=True)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
def get_db():
# ... (existing get_db)

    db = SessionLocal()
    try: yield db
    finally: db.close()

# Calendar API Endpoints
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

@app.get("/api/symptoms/{session_id}")
def get_symptoms(session_id: str, db: Session = Depends(get_db)):
    return db.query(SymptomLog).filter(SymptomLog.session_id == session_id).all()

@app.post("/api/symptoms/{session_id}")
def add_symptom_log(session_id: str, entry: SymptomLogCreate, db: Session = Depends(get_db)):
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

@app.get("/api/period/{session_id}")
def get_periods(session_id: str, db: Session = Depends(get_db)):
    return db.query(PeriodTracker).filter(PeriodTracker.session_id == session_id).all()

@app.post("/api/period/{session_id}")
def add_period_entry(session_id: str, entry: PeriodTrackerCreate, db: Session = Depends(get_db)):
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

@app.get("/api/calendar/{session_id}")
def get_calendar(session_id: str, db: Session = Depends(get_db)):
    return db.query(CalendarEvent).filter(CalendarEvent.session_id == session_id).all()

@app.post("/api/calendar/{session_id}")
def add_calendar_event(session_id: str, event: CalendarEventCreate, db: Session = Depends(get_db)):
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

@app.delete("/api/calendar/event/{event_id}")
def delete_calendar_event(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not db_event: raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    return {"status": "success"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0", "uptime": "99.9%"}

from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Token(BaseModel):
    access_token: str
    token_type: str

import bcrypt

def get_password_hash(password):
    # bcrypt requires bytes
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except:
        return False

SECRET_KEY = os.environ.get("JWT_SECRET", "super_secret_enterprise_key_2026")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/api/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user: raise HTTPException(status_code=400, detail="Email already registered")
    # Try to create with name if column exists, otherwise skip
    try:
        new_user = User(email=user.email, name=user.name, hashed_password=get_password_hash(user.password))
    except:
        new_user = User(email=user.email, hashed_password=get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "access_token": create_access_token(data={"sub": new_user.email}),
        "token_type": "bearer",
        "user": {"id": new_user.id, "email": new_user.email, "name": getattr(new_user, 'name', None)}
    }

@app.post("/api/auth/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {
        "access_token": create_access_token(data={"sub": db_user.email}),
        "token_type": "bearer",
        "user": {"id": db_user.id, "email": db_user.email, "name": getattr(db_user, 'name', None)}
    }

@app.post("/api/auth/google")
def google_login(data: dict, db: Session = Depends(get_db)):
    """Google OAuth login endpoint (placeholder for future implementation)"""
    raise HTTPException(status_code=501, detail="Google login coming soon. Use email/password for now.")

# ---------------------------------

def load_persistence():
    global session_knowledge, session_sources
    if KNOWLEDGE_FILE.exists():
        try:
            data = json.loads(KNOWLEDGE_FILE.read_text(encoding="utf-8"))
            session_knowledge = data.get("knowledge", {})
            session_sources = data.get("sources", {})
        except: pass

load_persistence()
client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections and websocket in self.active_connections[session_id]:
            self.active_connections[session_id].remove(websocket)
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    async def broadcast(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try: await connection.send_json(message)
                except: pass

manager = ConnectionManager()

import subprocess
import socket

def get_project_index(session_id: str) -> str:
    session_dir = OUTPUT_ROOT / session_id
    if not session_dir.exists(): return "Empty Workspace"
    files = [f.name for f in session_dir.iterdir() if f.is_file() and f.name not in ["server.log", "ecommerce.db", "elearning.db"]]
    if not files: return "No generated files yet."
    return "CURRENT WORKSPACE FILES: " + ", ".join(files)

def get_expert_system_prompt(session_id: str, knowledge: str = ""):
    workspace_context = get_project_index(session_id)
    knowledge_context = f"\n\n--- EDUCATIONAL KNOWLEDGE BASE ---\n{knowledge[-100000:]}\n----------------------" if knowledge else ""
    
    return f"""You are the Lead Youth Sexuality Consultant & Educator.
    
    CORE MISSION:
    Provide accurate, scientifically-grounded, and empathetic information regarding sexuality, sexual health, identity, and relationships for young adults. 
    Maintain a safe, non-judgmental, and confidential space.
    
    CALENDAR AWARENESS:
    You have access to the user's personal sexuality-related calendar (tracking cycles, appointments, or educational goals).
    - If the user asks "What's next?" or "Any reminders?", refer to their calendar.
    - If they share a date (e.g., "I have a checkup on Friday"), suggest they add it to their calendar.
    
    CRITICAL COGNITION:
    1. EMPATHY FIRST: Use supportive language. Avoid medical jargon unless explaining it simply.
    2. PRIVACY: Never ask for real names or identifiable locations.
    3. BOUNDARIES: If a user shares something that suggests immediate physical danger, provide resources for professional help/hotlines.
    
    CAPABILITIES:
    1. EDUCATIONAL CONTENT: Generate summaries, guides, or interactive Q&A.
    2. CALENDAR MGMT: Help users organize their health and education schedule.
    3. FULL-STACK APPS: If the user wants to build a personal tracker or tool, use FastAPI + HTML/JS.
    
    DISCIPLINE:
    - No judgment. No preaching. Just facts and support.
    - If the user asks about something you don't know, refer them to reputable sources like WHO or Planned Parenthood.
    
    KNOWLEDGE: {knowledge_context}"""

async def summarize_history(session_id: str):
    if len(session_memories.get(session_id, [])) < 10: return
    
    history = session_memories[session_id]
    to_summarize = history[1:-5] # Keep system prompt and last 5 messages
    if not to_summarize: return
    
    summary_prompt = f"Summarize the following technical conversation focusing on USER PREFERENCES and PROJECT PROGRESS. Be extremely concise:\n\n" + \
                     "\n".join([f"{m['role']}: {m['content'][:200]}" for m in to_summarize])
    
    try:
        # Use simple call to Gemini or Ollama for summary
        if client:
            resp = await asyncio.to_thread(client.models.generate_content, model="gemini-1.5-flash", contents=summary_prompt)
            summary = resp.text
        else:
            summary, _ = await call_ollama(summary_prompt)
            
        # Reconstruct memory: [System, Summary, ...last 5]
        new_history = [history[0]] # System prompt
        new_history.append({"role": "assistant", "content": f"CONTEXT_SUMMARY: {summary}"})
        new_history.extend(history[-5:])
        session_memories[session_id] = new_history
    except: pass

LOCAL_MODEL = "gemma3:1b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

async def call_ollama(prompt: str):
    try:
        # trust_env=False bypasses system proxies that cause 502 on local addresses
        async with httpx.AsyncClient(timeout=120.0, trust_env=False) as client:
            resp = await client.post(OLLAMA_URL, json={
                "model": LOCAL_MODEL,
                "prompt": prompt,
                "stream": False
            })
            if resp.status_code != 200:
                return f"Local AI error ({resp.status_code}). Please ensure Ollama is running.", "OFFLINE"

            try:
                data = resp.json()
                return data.get("response", "Model returned no data."), LOCAL_MODEL
            except json.JSONDecodeError:
                return "Model communication error. Please restart Ollama.", "OFFLINE"
    except Exception:
        return "Gemini quota exceeded and Local AI is not responding. Please ensure Ollama is open.", "OFFLINE"


import tiktoken
def estimate_tokens(text: str) -> int:
    try:
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(enc.encode(text))
    except:
        return len(text) // 4

def log_usage(session_id: str, prompt_text: str, response_text: str, model_name: str):
    try:
        tokens = estimate_tokens(prompt_text) + estimate_tokens(response_text)
        db = SessionLocal()
        new_log = UsageLog(session_id=session_id, tokens_used=tokens, model=model_name)
        db.add(new_log)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Usage tracking error: {e}")

async def call_llm(prompt: str, session_id: str, websocket: WebSocket):
    db = SessionLocal()
    calendar_events = db.query(CalendarEvent).filter(CalendarEvent.session_id == session_id).all()
    period_logs = db.query(PeriodTracker).filter(PeriodTracker.session_id == session_id).all()
    db.close()
    
    context_data = ""
    if calendar_events:
        context_data += "\n\n--- USER CALENDAR ---\n" + "\n".join([f"- {e.event_date.strftime('%Y-%m-%d')}: {e.title} ({e.category})" for e in calendar_events])
    
    if period_logs:
        context_data += "\n\n--- HEALTH LOGS (PERIODS) ---\n" + "\n".join([f"- Started: {p.start_date.strftime('%Y-%m-%d')}, Intensity: {p.intensity}, Notes: {p.notes or 'None'}" for p in period_logs])

    knowledge = session_knowledge.get(session_id, "")
    system_prompt = get_expert_system_prompt(session_id, knowledge)

    if session_id not in session_memories:
        session_memories[session_id] = [] # Memory only stores User/Model turns now
    
    # Inject calendar and health context into the active prompt
    enriched_prompt = prompt + context_data
    
    session_memories[session_id].append({"role": "user", "content": enriched_prompt})
    history = session_memories[session_id][-15:] 
    
    # Convert history to new SDK format (MUST NOT include "system" role)
    contents = []
    for m in history:
        role = "model" if m["role"] == "assistant" else m["role"]
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    
    if client:
        for model_name in MODELS:
            try:
                # Proper way to call system prompt in the new SDK
                response = await asyncio.to_thread(
                    client.models.generate_content, 
                    model=model_name, 
                    contents=contents,
                    config={"system_instruction": system_prompt}
                )
                ai_text = response.text
                session_memories[session_id].append({"role": "assistant", "content": ai_text})
                asyncio.create_task(asyncio.to_thread(log_usage, session_id, str(contents), ai_text, model_name))
                return ai_text, model_name
            except Exception as e:
                print(f"[GEMINI ERROR] {model_name}: {e}")
    
    # Fallback to Ollama (gemma3:1b)
    full_context = f"SYSTEM: {system_prompt}\n\n" + "\n".join([f"{m['role']}: {m['content']}" for m in history])
    ai_text, model_used = await call_ollama(full_context)
    session_memories[session_id].append({"role": "assistant", "content": ai_text})
    asyncio.create_task(asyncio.to_thread(log_usage, session_id, full_context, ai_text, model_used))
    
    return ai_text, model_used

from fastapi.responses import FileResponse
import shutil

@app.get("/download/{session_id}")
async def download_session(session_id: str):
    session_dir = OUTPUT_ROOT / session_id
    if not session_dir.exists():
        return {"error": "Session not found"}
    
    zip_path = OUTPUT_ROOT / f"{session_id}.zip"
    shutil.make_archive(str(OUTPUT_ROOT / session_id), 'zip', str(session_dir))
    
    return FileResponse(zip_path, media_type="application/zip", filename=f"{session_id}_project.zip")

def profile_data(filename: str, content: str) -> str:
    try:
        # Simple text-based profiling for small summaries
        lines = content.split('\n')
        header = lines[0] if lines else ""
        sample = "\n".join(lines[1:6])
        return f"FILE: {filename}\nCOLUMNS: {header}\nSAMPLE DATA:\n{sample}"
    except:
        return f"FILE: {filename} (Summary unavailable)"

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    session_dir = OUTPUT_ROOT / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    await manager.send_message({"type": "sources", "sources": session_sources.get(session_id, [])}, websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            
            if data.get("type") == "cursor":
                await manager.broadcast(data, session_id)
                continue
            
            if data.get("type") == "feed":
                content = ""; title = data.get("filename", "Source")
                try:
                    if data["feed_type"] == "url":
                        url = data["content"]
                        headers = {"User-Agent": "Mozilla/5.0"}
                        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
                            resp = await client.get(url)
                            soup = BeautifulSoup(resp.content, "html.parser")
                            for s in soup(["script", "style"]): s.decompose()
                            content = soup.get_text(separator="\n", strip=True)
                            title = url.split("//")[-1].split("/")[0]
                    elif data["feed_type"] == "file":
                        file_data = data["content"].split(",")[1]
                        decoded = base64.b64decode(file_data)
                        if title.lower().endswith(".pdf"):
                            reader = PdfReader(io.BytesIO(decoded))
                            content = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                        elif title.lower().endswith((".xlsx", ".xls")):
                            df = pd.read_excel(io.BytesIO(decoded))
                            content = df.to_string()
                        elif title.lower().endswith(".csv"):
                            df = pd.read_csv(io.BytesIO(decoded))
                            content = df.to_string()
                        else:
                            content = decoded.decode("utf-8", errors="ignore")
                    
                    if content:
                        profile = profile_data(title, content)
                        if session_id not in session_sources: session_sources[session_id] = []
                        if title not in session_sources[session_id]: session_sources[session_id].append(title)
                        session_knowledge[session_id] = (session_knowledge.get(session_id, "") + f"\n\nSOURCE PROFILE: {profile}\nFULL CONTENT:\n{content}")[-500000:]
                        KNOWLEDGE_FILE.write_text(json.dumps({"knowledge": session_knowledge, "sources": session_sources}), encoding="utf-8")
                        session_memories[session_id] = [{"role": "system", "content": get_expert_system_prompt(session_id, session_knowledge[session_id])}]
                        await manager.send_message({"type": "status", "text": "?? Information Absorbed!"}, websocket)
                        await manager.send_message({"type": "sources", "sources": session_sources[session_id]}, websocket)
                except Exception as e:
                    await manager.send_message({"type": "status", "text": f"? Error: {str(e)[:30]}"}, websocket)
                continue
            
            user_msg = data.get("message", "")
            if data.get("type") == "auto_debug":
                error = data.get("error")
                user_msg = f"CRITICAL: The previous code failed with this error in the preview environment: {error}. Please diagnose why it failed and provide a fixed version."

            if data.get("type") == "start_server":
                try:
                    if session_id in active_servers:
                        try: active_servers[session_id].terminate()
                        except: pass
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        if s.connect_ex(('127.0.0.1', 8080)) == 0:
                            if session_id not in active_servers:
                                await manager.send_message({"type": "status", "text": "?? Port 8080 busy!"}, websocket)
                                continue
                    log_path = session_dir / "server.log"
                    log_file = open(log_path, "w", encoding="utf-8")
                    proc = subprocess.Popen([sys.executable, "main.py"], cwd=session_dir, stdout=log_file, stderr=subprocess.STDOUT, text=True)
                    active_servers[session_id] = proc
                    await asyncio.sleep(2)
                    if proc.poll() is not None:
                        log_file.close()
                        error_output = log_path.read_text(encoding="utf-8")
                        await manager.send_message({"type": "status", "text": "? Server Crashed!"}, websocket)
                        await manager.send_message({"type": "result", "role": "assistant", "content": f"The backend server failed to start:\n```\n{error_output}\n```", "model_info": "SYSTEM-CHECK"}, websocket)
                    else:
                        await manager.send_message({"type": "status", "text": "?? Server Started on Port 8080!"}, websocket)
                        log_file.close()
                except Exception as e:
                    await manager.send_message({"type": "status", "text": f"? Server Error: {str(e)}"}, websocket)
                continue

            if data.get("type") == "message_with_file":
                filename = data.get("filename", "data")
                file_data = data.get("file_content").split(",")[1]
                decoded = base64.b64decode(file_data)
                content = ""
                try:
                    if filename.lower().endswith(".pdf"):
                        reader = PdfReader(io.BytesIO(decoded))
                        content = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                    elif filename.lower().endswith((".xlsx", ".xls")):
                        df = pd.read_excel(io.BytesIO(decoded))
                        content = df.to_string()
                    elif filename.lower().endswith(".csv"):
                        df = pd.read_csv(io.BytesIO(decoded))
                        content = df.to_string()
                    else:
                        content = decoded.decode("utf-8", errors="ignore")
                    user_msg = f"ATTACHED DATA ({filename}):\n{content}\n\nUSER REQUEST: {user_msg}"
                except: pass

            if len(session_memories.get(session_id, [])) <= 1:
                try:
                    if client:
                        resp = await asyncio.to_thread(client.models.generate_content, model="gemini-1.5-flash", contents=f"Short 3-word title for: {user_msg[:100]}")
                        await manager.send_message({"type": "title", "title": resp.text.strip().replace('"', '')}, websocket)
                except: pass
            
            ai_response, model_used = await call_llm(user_msg, session_id, websocket)
            await manager.send_message({"type": "result", "role": "assistant", "content": ai_response, "model_info": model_used}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

@app.websocket("/ws/{session_id}/logs")
async def log_websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    log_path = OUTPUT_ROOT / session_id / "server.log"
    try:
        if not log_path.exists():
            await websocket.send_text("No logs available yet.")
            while not log_path.exists():
                await asyncio.sleep(1)
        
        with open(log_path, "r", encoding="utf-8") as f:
            # Send existing logs
            existing = f.read()
            if existing: await websocket.send_text(existing)
            # Tail logs
            while True:
                line = f.readline()
                if not line:
                    await asyncio.sleep(0.5)
                    continue
                await websocket.send_text(line)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Log WS Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
