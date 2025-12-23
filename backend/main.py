"""
Flourisha AI Brain - FastAPI Backend
Multi-tenant content intelligence platform
"""
import os
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/root/.claude/.env')

# Add AI Brain root to path for imports
AI_BRAIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_BRAIN_ROOT not in sys.path:
    sys.path.insert(0, AI_BRAIN_ROOT)

# Import routers from api/ folder
from api import projects, content, youtube

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Flourisha Backend starting up...")
    yield
    # Shutdown
    print("👋 Flourisha Backend shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Flourisha API",
    description="Multi-tenant content intelligence platform with AI-powered processing",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server (local)
        "http://localhost:5173",  # Vite dev server (local)
        "http://localhost:5174",  # Vite dev server (local - alternate port)
        "http://100.66.28.67:5173",  # Vite dev server (Tailscale)
        "http://100.66.28.67:5174",  # Vite dev server (Tailscale - alternate port)
        "http://localhost:8081",  # React Native Expo
        "https://flourisha-d959a.web.app",  # Firebase hosting
        "https://flourisha-d959a.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "flourisha-ai-brain",
        "version": "0.1.0"
    }

# Protected test endpoint
@app.get("/api/v1/me")
async def get_current_user_info():
    """Get current user info (protected route - to be implemented)"""
    # This will use Firebase auth middleware once implemented
    return {"message": "Protected route - auth middleware to be added"}

# Include routers
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])
app.include_router(youtube.router, prefix="/api/v1", tags=["youtube"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
