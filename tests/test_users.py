import pytest
import uuid

@pytest.fixture
async def setup_user(client):
    response = await client.post(
        "/users", json={"username": "testuser", "email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == 201  # Ensure the user was created successfully

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
    response = await client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
