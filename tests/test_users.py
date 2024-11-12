import pytest
import pytest_asyncio

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/users", json={"username": "testuser", "email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_user(client):
    response = await client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"