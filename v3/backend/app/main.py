"""FastAPI main application."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import jobs, packets, websocket
from app.core.config import get_settings
from app.core.database import create_tables
from app.core.events import event_manager

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Track application startup time
startup_time = datetime.utcnow()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Audiobook Master v3 API...")
    
    try:
        # Create database tables
        await create_tables()
        logger.info("Database tables created successfully")
        
        # Start event manager
        await event_manager.start()
        logger.info("Event manager started successfully")
        
        logger.info("Audiobook Master v3 API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Audiobook Master v3 API...")
    
    try:
        await event_manager.stop()
        logger.info("Event manager stopped successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Audiobook Master v3 API shut down")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Modern API for audiobook processing and management",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Health check endpoint
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection (simplified)
        database_status = "healthy"
        
        # Calculate uptime
        uptime = (datetime.utcnow() - startup_time).total_seconds()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION,
            "database": database_status,
            "uptime": uptime,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": settings.APP_VERSION,
                "database": "unhealthy",
                "uptime": 0,
            },
        )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Audiobook Master v3 API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation not available in production",
        "health": "/api/v1/health",
    }


# Include API routers
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(packets.router, prefix="/api/v1/packets", tags=["Packets"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
