from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import time
import logging

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.auth import get_current_user
from app.schemas.health import HealthResponse

app = FastAPI(
    title="E-commerce Recommendation Engine API",
    description="Cloud-Native recommendation engine for e-commerce platforms",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for the API"""
    return {
        "status": "healthy",
        "version": app.version,
        "timestamp": time.time()
    }

# Include API routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )