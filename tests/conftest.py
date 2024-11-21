# pytest_plugins = ["pytest_asyncio"]
import pytest_asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.services.database import Base, engine
import os

# Fetch test database URL from environment variable
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

# Set up the SQLAlchemy engine for the test database
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {})

# Set up session maker for the test database
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Test setup: Create a test database
@pytest.fixture(scope="module")
# @pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    
# Async client fixture for tests
@pytest_asyncio.fixture(scope="module")
async def client(setup_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

