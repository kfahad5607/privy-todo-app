from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.endpoints import auth
from app.core.exceptions import BaseAppException
from app.db.database import init_db, close_db

# Set up central logging
log_file = os.path.join(settings.LOG_DIR, f"{settings.PROJECT_NAME.lower()}.log") if settings.LOG_DIR else None
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=log_file,
    console_output=settings.DEBUG
)

# Get a logger for this module
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    logger.info("Application startup: Initializing database")
    await init_db()
    yield
    # Cleanup database resources on shutdown
    logger.info("Application shutdown: Closing database connections")
    await close_db()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Bloo Soar Backend API",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handlers
@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Application error: {exc.message}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "path": request.url.path, 
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )    

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

logger.info(f"Application {settings.PROJECT_NAME} initialized successfully")