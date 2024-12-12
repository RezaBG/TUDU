import os
import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.routers import task_router, user_router, auth_router
from src.services.database import Base, engine


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(user_router, tags=["Users"])
app.include_router(task_router, tags=["Tasks"])

# Enforce HTTPS in production
@app.middleware("http")
async def enforce_https_in_production(request: Request, call_next):
    environment = os.getenv("ENVIRONMENT", "development")
    if environment not in ["development", "production"]:
        raise ValueError(f"Invalid ENVIRONMENT value: {environment}")

    if environment == "production" and request.url.scheme != "https":
        raise HTTPException(
            status_code=400,
            detail="HTTPS is required for secure communication"
        )
    response = await call_next(request)
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation failed.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error at {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred. Please try again later.",
        },
    )
