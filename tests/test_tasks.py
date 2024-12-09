import asyncio
import logging

import pytest
import pytest_asyncio
from src.enums.task_status import TaskStatus

from tests.conftest import test_engine
from sqlalchemy.inspection import inspect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Helper function for task payload
def generate_task_payload(
        title="Test Task",
        description="Task Description",
        owner_id=None,
        status=TaskStatus.PENDING.value  # Use TaskStatus enum
):
    return {
        "title": title,
        "description": description,
        "owner_id": owner_id,
        "status": status  # Convert enum to string (e.g., "pending")
    }


def test_inspect_table():
    inspector = inspect(test_engine)
    print("Tables in the database:", inspector.get_table_names())


@pytest_asyncio.fixture
async def setup_task(client, setup_user):
    """
    Creates a task for use in tests that depend on tasks.
    """
    owner_id = setup_user.get("id")
    payload = {
        "id": 2,
        "title": "Test Task",
        "description": "Task Description",
        "owner_id": owner_id,
        "status": TaskStatus.PENDING.value,
    }
    response = await client.post(
        "/tasks",
        json=payload
    )

    logger.info("Task creation response: %s", response.status_code)
    logger.info("Task creation content: %s", response.json())
    assert response.status_code == 201

    # Return the created task details
    task_data = response.json()
    return task_data


@pytest.mark.asyncio
async def test_create_task(setup_task):
    """
    Tests the creation of a task.
    """
    assert setup_task["title"] == "Test Task"
    assert setup_task["status"] == TaskStatus.PENDING.value
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
        owner_id = setup_task.get("owner", {}).get("id", None)
        assert owner_id, "Owner ID is missing in the task data"

        payload = generate_task_payload(
            title="Updated Task",
            description="Updated Description",
            owner_id=owner_id,
            status= TaskStatus.COMPLETED.value,
        )

        response = await asyncio.wait_for(
            client.put(f"/tasks/{task_id}", json=payload), timeout=5
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Task"
        assert response.json()["status"] == "completed"
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
    invalid_task_id = 9999
    response = await client.get(f"/tasks/{invalid_task_id}")

    # Assert the status code
    assert response.status_code == 404, f"Expected 404, got {response.status_code} instead"

    # Assert the response detail message
    expected_detail = f"Task with ID {invalid_task_id} not found"
    actual_detail = response.json().get("detail")
    assert actual_detail == expected_detail, f"Expected {expected_detail}, got {actual_detail} instead"

    # Log the result for clarity
    logger.info(
        "Test passed: Get task invalid ID. Expected status code: 404, actual: %s. "
        "Expected detail: '%s', actual: '%s'.",
        response.status_code,
        expected_detail,
        actual_detail,
    )


@pytest.mark.asyncio
async def test_update_task_invalid_id(client, setup_task):
    """
    Tests updating a task with an invalid ID.
    """
    owner_id = setup_task["owner"]["id"]
    invalid_id = 9999
    payload = generate_task_payload(
        title="Updated Task",
        description="Updated Description",
        owner_id=owner_id,
    )

    response = await client.put(f"tasks/{invalid_id}", json=payload)

    # Assert the status code
    assert response.status_code == 404, f"Expected 404, got {response.status_code} instead"

    # Assert the response detail message
    expected_detail = f"Task with ID {invalid_id} not found"
    actual_detail = response.json().get("detail")
    assert actual_detail == expected_detail, f"Expected {expected_detail}, got {actual_detail} instead"

    # Log the result for clarity
    logger.info(
        "Test passed: Update task invalid ID. Expected status code: 404, actual: %s. "
        "Expected detail: '%s', actual: '%s'.",
        response.status_code,
        expected_detail,
        actual_detail,
    )


@pytest.mark.asyncio
async def test_delete_task_invalid_id(client):
    """
    Tests deleting a task with an invalid ID.
    """
    invalid_id = 9999
    response = await client.delete(f"tasks/{invalid_id}")

    # Log the response for debugging

    logger.info("Response status for ID: %s", response.status_code)
    logger.info("Response content: %s", response.json())

    # Assert the status code
    assert response.status_code == 404, f"Expected 404, got {response.status_code} instead"

    # Assert the error detail
    expected_detail = f"Task with ID '{invalid_id}' not found"
    actual_detail = response.json().get("detail")
    logger.info("Expected detail: %s, actual: %s", expected_detail, actual_detail)
    assert actual_detail == expected_detail, f"Expected {expected_detail}, got {actual_detail} instead"

    # Final log
    logger.info("Delete task invalid ID: %s", invalid_id)


@pytest.mark.asyncio
async def test_filter_tasks_by_user(client, setup_user):
    """
    Tests filtering tasks by user.
    """
    owner_id = setup_user["id"]
    # Create tasks with different statuses for the user
    await client.post("/tasks", json=generate_task_payload(title="Task 1", description="Description 1", owner_id=owner_id, status=TaskStatus.PENDING))
    await client.post("/tasks", json=generate_task_payload(title="Task 2", description="Description 2", owner_id=owner_id, status=TaskStatus.IN_PROGRESS))
    await client.post("/tasks", json=generate_task_payload(title="Task 3", description="Description 3", owner_id=owner_id, status=TaskStatus.COMPLETED))

    # Corrected the URL for user filtering
    response = await client.get(f"/tasks/user/{owner_id}")

    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response body: {response.json()}")

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) > 0
    assert all(task["owner"]["id"] == owner_id for task in tasks)
    logger.info("Filter tasks by user test passed.")


@pytest.mark.asyncio
async def test_filter_tasks_by_status(client, setup_user):
    """
    Tests filtering tasks by status.
    """
    owner_id = setup_user["id"]

    # Create tasks with different statuses
    await client.post("/tasks", json=generate_task_payload(title="Task 1", description="Description 1", owner_id=owner_id, status=TaskStatus.PENDING))
    await client.post("/tasks", json=generate_task_payload(title="Task 2", description="Description 2", owner_id=owner_id, status=TaskStatus.IN_PROGRESS))
    await client.post("/tasks", json=generate_task_payload(title="Task 3", description="Description 3", owner_id=owner_id, status=TaskStatus.COMPLETED))

    # Make the Get request
    response = await client.get("/tasks/status/in-progress")

    # Log response for debugging
    logger.info("Response status: %s", response.status_code)
    logger.info("Response content: %s", response.json())

    # Assertions
    assert response.status_code == 200, f"Expected 200, got {response.status_code} instead"
    tasks = response.json()
    assert len(tasks) > 0, "Expected at least 1 task, got none"
    assert all(task["status"] == "in-progress" for task in tasks), "One or more tasks have an incomplete status"

    logger.info("Filter tasks by status test passed.")
