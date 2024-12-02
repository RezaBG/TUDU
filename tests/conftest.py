import os

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import ASGITransport

from src.main import app
from src.services.database import Base

# Fetch test database URL from environment variable
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

# Set up the SQLAlchemy engine for the test database
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
)

# Set up session maker for the test database
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Test setup: Create a test database
@pytest.fixture(scope="module")
def setup_db():
    """
    Sets up the test database for the duration of the test module.
    Creates tables at the start and drops them at the end.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest_asyncio.fixture(scope="module")
async def client(setup_db):
    """
    Provides an HTTP client for testing FastAPI endpoints.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def setup_user(client):
    """
    Creates a user for use in tests that depend on a user.
    """
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    payload = {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "password123",
    }
    response = await client.post("/users", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture(autouse=True)
def reset_database():
    """
    Resets the database before each test to ensure isolation.
    """
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
