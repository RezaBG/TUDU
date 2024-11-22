import pytest
import uuid

import pytest_asyncio


# @pytest.fixture
@pytest_asyncio.fixture
async def setup_user(client):
    unique_id = uuid.uuid4().hex[:8]
    response = await client.post(
        "/users",
        json={
            "username": f"testuser_{unique_id}",
            "email": f"testuser_{unique_id}@example.com",
            "password": "password123",
        }
    )
    assert response.status_code == 201  # Ensure the user was created successfully
    return response.json()

@pytest.mark.asyncio
async def test_create_user(client):
    # Use a unique username
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    response = await client.post(
        "/users", json={"username": username, "email": f"{username}@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == username


@pytest.mark.asyncio
async def test_get_user(client, setup_user):  # Use the setup_user fixture
    user_id = setup_user["id"]
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == setup_user["username"]
