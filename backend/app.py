"""
FinVis - AI-Powered Financial Risk Analysis System

Main FastAPI application for BIST30 stock risk analysis.

## Features
- KAP (Public Disclosure Platform) scraping
- Financial news analysis
- Turkish NLP sentiment analysis
- Event detection
- Risk scoring engine
- RESTful API

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints
- GET /api/v1/risk/{stock_symbol} - Analyze stock risk
- GET /api/v1/risk/batch - Batch analysis
- GET /api/v1/stocks - List available stocks
- GET /api/v1/health - Health check
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time

from utils.config import get_settings
from utils.logger import get_logger
from routes.risk import router as risk_router
from routes.market import router as market_router

# Initialize logger
logger = get_logger("app")

# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description="AI-powered financial risk analysis for BIST30 companies",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(risk_router)
app.include_router(market_router)


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        Basic API information
    """
    return {
        "name": "FinVis - Financial Risk Analysis API",
        "version": settings.API_VERSION,
        "description": "AI-powered financial risk analysis for BIST30 companies",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/health",
            "stocks": "/api/v1/stocks",
            "risk_analysis": "/api/v1/risk/{stock_symbol}"
        },
        "example": "/api/v1/risk/THYAO"
    }


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "timestamp": time.time()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Args:
        request: The request that caused the exception
        exc: The exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.API_DEBUG else "An error occurred"
        }
    )


@app.on_event("startup")
async def startup_event():
    """Application startup handler."""
    logger.info("=" * 50)
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Debug mode: {settings.API_DEBUG}")
    logger.info(f"Host: {settings.HOST}:{settings.PORT}")
    logger.info("=" * 50)
    
    # Log available endpoints
    logger.info("Available endpoints:")
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            methods = list(route.methods - {"HEAD", "OPTIONS"})
            if methods:
                logger.info(f"  {methods[0]} {route.path}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown handler."""
    logger.info("Shutting down FinVis API")


# For running with: uvicorn app:app
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.API_DEBUG,
        log_level="info"
    )
