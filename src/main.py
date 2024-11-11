from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import task_router
from src.services.database import Base, engine

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

# Include task router
app.include_router(task_router)