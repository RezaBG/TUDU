import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/users", json={"username": "testuser_unique", "email": "uniqueuser@example.com", "password": "password123"}
    )
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json()}")
    assert response.status_code == 201
    assert response.json()["username"] == "testuser_unique"

@pytest.mark.asyncio
async def test_get_user(client):
    response = await client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"