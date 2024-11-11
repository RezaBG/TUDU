# pytest_plugins = ["pytest_asyncio"]
import pytest_asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from src.main import app
from src.services.database import Base, engine

# Test setup: Create a test database
@pytest.fixture(scope="module")
# @pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))

# Async client fixture for tests
@pytest_asyncio.fixture(scope="module")
async def client(setup_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
