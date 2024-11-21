import pytest
import pytest_asyncio

@pytest_asyncio.fixture
async def setup_task(client):
    # Create the task
    response = await client.post(
        "/tasks", json={"title": "Test Task", "description": "Task Description", "owner_id": 1}
    )
    print(f"Task creation response: {response.status_code}")
    print(f"Task creation content: {response.json()}")
    assert response.status_code == 201
    return response.json()

@pytest.mark.asyncio
async def test_create_task(client):
    response = await client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "owner_id": "1",
            "description": "Task task",
        },
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"

@pytest.mark.asyncio
async def test_get_task(client, setup_task):
    task_id = setup_task["id"]
    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

@pytest.mark.asyncio
async def test_update_task(client, setup_task):
    task_id = setup_task["id"]
    response = await client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Task", "description": "Updated Description", "owner_id": 1},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"

@pytest.mark.asyncio
async def test_delete_task(client, setup_task):
    task_id = setup_task["id"]
    response = await client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
