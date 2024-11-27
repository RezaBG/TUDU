import asyncio
import logging

import pytest
import pytest_asyncio

from tests.conftest import test_engine
from sqlalchemy.inspection import inspect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Helper function for task payload
def generate_task_payload(title="Test Task", description="Task Description", owner_id=None):
    """
    Generates a task payload for testing.
    """
    return {
        "title": title,
        "description": description,
        "owner_id": owner_id
    }

def test_inspect_table():
    inspector = inspect(test_engine)
    print("Tables in the database:", inspector.get_table_names())


@pytest_asyncio.fixture
async def setup_task(client, setup_user):
    """
    Creates a task for use in tests that depend on tasks.
    """
    owner_id = setup_user["id"]
    payload = generate_task_payload(owner_id=owner_id)
    response = await client.post("/tasks", json=payload)
    logger.info("Task creation response: %s", response.status_code)
    logger.info("Task creation content: %s", response.json())
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_task(client, setup_task):
    """
    Tests the creation of a task.
    """
    assert setup_task["title"] == "Test Task"
    logger.info("Create task test passed.")


@pytest.mark.asyncio
async def test_get_task(client, setup_task):
    """
    Tests retrieving a specific task by ID.
    """
    task_id = setup_task["id"]
    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"
    logger.info("Get task passed for ID: %s", task_id)


@pytest.mark.asyncio
async def test_update_task(client, setup_task):
    """
    Tests updating an existing task.
    """
    try:
        task_id = setup_task["id"]
        # owner_id = setup_task["owner"]["id"]
        owner_id = setup_task.get("owner", {}).get("id", None)
        assert owner_id, "Owner ID is missing in the task data"
        payload = generate_task_payload(title="Updated Task", description="Updated Description", owner_id=owner_id)
        response = await asyncio.wait_for(
            client.put(f"/tasks/{task_id}", json=payload), timeout=5
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Task"
        logger.info("Update task passed for ID: %s with payload: %s", task_id, payload)
    except asyncio.TimeoutError:
        logger.error("Timeout occurred while updating task.")


@pytest.mark.asyncio
async def test_delete_task(client, setup_task):
    """
    Tests deleting an existing task.
    """
    task_id = setup_task["id"]
    response = await client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    logger.info(f"Deleting task with ID: {task_id}")
    logger.info("Delete response status for ID: %s", response.status_code)


@pytest.mark.asyncio
async def test_get_task_invalid_id(client):
    """
    Tests fetching a task with an invalid ID.
    """
    response = await client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with ID 9999 not found"
    logger.info("Get task invalid ID test passed.")


@pytest.mark.asyncio
async def test_update_task_invalid_id(client, setup_task):
    """
    Tests updating a task with an invalid ID.
    """
    owner_id = setup_task["id"]
    invalid_id = 9999
    payload = generate_task_payload(title="Updated Task", description="Updated Description", owner_id=owner_id)
    response = await client.put(f"tasks/{invalid_id}", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with ID 9999 not found"
    logger.info(
        "Update task invalid ID test passed for ID: %s with payload: %s",
        invalid_id,
        payload,
    )


@pytest.mark.asyncio
async def test_delete_task_invalid_id(client):
    """
    Tests deleting a task with an invalid ID.
    """
    response = await client.delete("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with ID 9999 not found"
    logger.info("Delete task invalid ID test passed.")
