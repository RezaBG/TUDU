from fastapi import FastAPI, Request, HTTPException
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.routers import task_router, user_router, auth_router
from src.services.database import Base, engine
import os

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
    if os.getenv("ENVIRONMENT", "development") == "production":
        if request.url.scheme != "https":
            raise HTTPException(
                status_code=400,
                detail="HTTPS is required for secure communication"
            )
    response = await call_next(request)
    return response


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return JSONResponse(
#         status_code=422,
#         content={"detail": exc.errors(), "message": "Validation failed"},
#     )
