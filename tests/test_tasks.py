import pytest
import pytest_asyncio
import logging
from tests.test_users import setup_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest_asyncio.fixture
async def setup_task(client, setup_user):
    # Create the task
    owner_id = setup_user["id"]
    response = await client.post(
        "/tasks", json={"title": "Test Task", "description": "Task Description", "owner_id": owner_id}
    )
    logger.info(f"Task creation response: {response.status_code}")
    logger.info(f"Task creation content: {response.json()}")
    assert response.status_code == 201
    return response.json()

@pytest.mark.asyncio
async def test_create_task(client, setup_task):
    assert setup_task["title"] == "Test Task"


@pytest.mark.asyncio
async def test_get_task(client, setup_task):
    task_id = setup_task["id"]
    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


@pytest.mark.asyncio
async def test_update_task(client, setup_task):
    task_id = setup_task["id"]
    owner_id = setup_task["owner_id"]
    response = await client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Task", "description": "Updated Description", "owner_id": owner_id},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"

@pytest.mark.asyncio
async def test_delete_task(client, setup_task):
    task_id = setup_task["id"]
    logger.info(F"Deleting task with ID: {task_id}")

    response = await client.delete(f"/tasks/{task_id}")

    logger.info(f"Delete response status: {response.status_code}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_task_invalid_id(client):
    response = await client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_update_task_invalid_id(client, setup_task):
    owner_id = setup_task["owner_id"]
    invalid_id = 9999
    logger.info(f"Testing PUT /tasks/{invalid_id} with an invalid ID")
    response = await client.put(
        f"/tasks/{invalid_id}",
        json={"title": "Updated Task", "description": "Updated Description", "owner_id": owner_id},
    )
    logger.info(f"Response: {response.status_code}, Detail: {response.json("detail")}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

@pytest.mark.asyncio
async def test_delete_task_invalid_id(client):
    response = await client.delete("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
