import logging
import uuid

import pytest
import pytest_asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_user(client):
    """
    Tests user creation endpoint for valid input.
    """
    unique_id = uuid.uuid4().hex[:8]
    payload = {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "password123",
    }
    response = await client.post("/users", json=payload)
    assert response.status_code == 201
    assert response.json()["username"] == payload["username"]
    logger.info("Create user passed for payload: %s", payload)


@pytest.mark.asyncio
async def test_get_user(client, setup_user):  # Use the setup_user fixture
    """
    Tests retrieving an existing user by ID.
    """
    user_id = setup_user["id"]
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == setup_user["username"]
    logger.info("Get user passed for ID: %s", user_id)
