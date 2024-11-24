import logging
import uuid

import pytest

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
async def test_get_user(client, setup_user):
    """
    Tests retrieving an existing user by ID.
    """
    user_id = setup_user["id"]
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == setup_user["username"]
    logger.info("Get user passed for ID: %s", user_id)


@pytest.mark.asyncio
async def test_get_user_invalid_id(client):
    """
    Tests fetching a user with an invalid ID.
    """
    response = await client.get("/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User with ID 9999 not found"
    logger.info("Get user invalid ID test passed.")