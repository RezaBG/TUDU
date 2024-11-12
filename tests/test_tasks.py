from http.client import responses

import pytest

@pytest.mark.asyncio
async def test_create_task(client):

    response = await client.post(
        "/users", json={"username": "testuser", "email": "testuser@example.com", "password": "password123"}
    )

    assert response.status_code == 201
    assert response.json()["username"] == "testuser_unique"

@pytest.mark.asyncio
async def test_get_task(client):
    response = await client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

@pytest.mark.asyncio
async def test_update_task(client):
    response = await client.put(
        "/tasks/1",
        json={"title": "Update Test Task", "description": "Updated task description", "owner_id": 1},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Update Test Task"

@pytest.mark.asyncio
async def test_delete_task(client):
    response = await client.delete("/tasks/1")
    assert response.status_code == 204