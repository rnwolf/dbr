import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dbr.api.work_items import router as work_items_router
from dbr.api.schedules import router as schedules_router
from dbr.api.system import router as system_router
from dbr.api.auth import router as auth_router
from scalar_fastapi import get_scalar_api_reference

# Import logging configuration
from dbr.core.logging_config import setup_logging, get_logger
from dbr.core.middleware import (
    RequestLoggingMiddleware,
    AuthLoggingMiddleware,
    DatabaseLoggingMiddleware,
    ErrorLoggingMiddleware
)

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "logs/dbr_api.log")
enable_sql_logging = os.getenv("ENABLE_SQL_LOGGING", "false").lower() == "true"

setup_logging(
    log_level=log_level,
    log_file=log_file,
    enable_sql_logging=enable_sql_logging
)

# Get application logger
logger = get_logger("main")

# Initialize database
from dbr.core.database import init_db
logger.info("Initializing database...")
init_db()
logger.info("Database initialization complete")

app = FastAPI(
    title="DBR Buffer Management System API",
    version="1.0.0",
    description="API for managing Collections, Work Items, and Schedules within a Drum Buffer Rope (DBR) system",
    servers=[
        {"url": "http://127.0.0.1:8000", "description": "Local server"},
    ],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware (order matters!)
# Temporarily disable complex middleware to isolate the issue
# app.add_middleware(ErrorLoggingMiddleware)
# app.add_middleware(DatabaseLoggingMiddleware)
# app.add_middleware(AuthLoggingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

logger.info("DBR API starting up", extra={
    "version": "1.0.0",
    "log_level": log_level,
    "sql_logging": enable_sql_logging
})

# Include API routers
app.include_router(work_items_router, prefix="/api/v1")
app.include_router(schedules_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "DBR Buffer Management System API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring and frontend connectivity tests"""
    logger.debug("Health check endpoint accessed")
    return {
        "status": "healthy",
        "service": "DBR Buffer Management System API",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
    }


@app.get("/api/v1/health")
def api_health_check():
    """API-specific health check endpoint"""
    logger.debug("API health check endpoint accessed")
    return {
        "status": "healthy",
        "api_version": "v1",
        "endpoints": ["workitems", "schedules", "system", "auth"],
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
