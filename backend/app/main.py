"""
Main FastAPI application for the Finance Tracker.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import time
import logging
from app.core.config import settings
from app.db.session import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A modern finance tracker with AI-powered insights and Plaid integration",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods, including OPTIONS
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Finance Tracker API...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Finance Tracker API...")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Finance Tracker API",
        "version": settings.app_version,
        "status": "healthy",
        "docs": "/docs" if settings.debug else "Documentation disabled in production"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version
    }


# Include API routers
from app.api import auth, users, accounts, transactions, plaid_api, ml_api

app.include_router(
    auth.router,
    prefix=f"{settings.api_prefix}/auth",
    tags=["authentication"]
)

app.include_router(
    users.router,
    prefix=f"{settings.api_prefix}/users",
    tags=["users"]
)

app.include_router(
    accounts.router,
    prefix=f"{settings.api_prefix}/accounts",
    tags=["accounts"]
)

app.include_router(
    transactions.router,
    prefix=f"{settings.api_prefix}/transactions",
    tags=["transactions"]
)

app.include_router(
    plaid_api.router,
    prefix=f"{settings.api_prefix}/plaid",
    tags=["plaid"]
)

app.include_router(
    ml_api.router,
    prefix=f"{settings.api_prefix}/ml",
    tags=["machine-learning"]
) 