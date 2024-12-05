from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi import Path


from src.models import Task, User, TaskStatus
from src.schemas import TaskCreate, TaskRead, TaskUpdate
from src.services.dependencies import get_db
from src.services.crud import get_item_by_id, create_item


import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/tasks",
             response_model=TaskRead,
             status_code=status.HTTP_201_CREATED,
             summary="Create a Task",
             description="Create a new task by providing the title, "
                         "description, and owner ID.",
             responses={
                 400: {"description": "Bad Request - Invalid Task Data"},
                 404: {"description": "Owner Not Found"},
                 500: {"description": "Internal Server Error"},
             },
)
def create_task(
        task: TaskCreate,
        db: Session = Depends(get_db),
):
    logger.info(f"Creating task with title: {task.title} and status: {task.status}")

    # Validate what the owner exists
    owner = db.query(User).filter_by(id=task.owner_id).first()
    if not owner:
        logger.error(f"Owner with ID {task.owner_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner with ID {task.owner_id} not found",
        )

    task_data = {
        "title": task.title,
        "description": task.description,
        "owner_id": task.owner_id,
        "status": task.status,
    }
    new_task = create_item(Task, task_data, db)
    logger.info(f"Task '{new_task.title}' created successfully with ID {new_task.id}"
                f" and status: {new_task.status}")
    return new_task



@router.get("/tasks/{task_id}",
            response_model=TaskRead,
            summary="Get a Task by ID",
            description="Retrieve a task by unique ID. If the task is not found, a 404 error is returned",
            responses={
                404: {"description": "Task Not Found"},
                500: {"description": "Internal Server Error"},
            },
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = get_item_by_id(Task, task_id, db)
    logger.info(f"Retrieved task with ID {task_id}: {task.title}")
    return task


@router.put("/tasks/{task_id}",
            response_model=TaskRead,
            summary="Update a Task",
            description="Update an existing task by its ID. Requires the updated title and description",
            responses={
                400: {"description": "Bad Request - Invalid Task Update Data"},
                404: {"description": "Task Not Found"},
                500: {"description": "Internal Server Error"},
            },
)
def update_task(
        task_id: int,
        task: TaskUpdate,
        db: Session = Depends(get_db)
):
    """
    Update an existing task by its unique ID.
    """
    try:
        # Log the received payload
        logger.debug(f"Received update payload for task ID {task_id}: {task}")

        # Ensure the task exists
        existing_task = get_item_by_id(
            Task,
            task_id,
            db,
        )
        if existing_task is None:
            logger.warning(f"Task with ID '{task_id}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID '{task_id}' not found",
            )

        # Check for empty update payload
        if not any([
            task.title,
            task.description,
            task.status,
            ]):
            logger.warning(f"No valid fields provided for update on Task ID '{task_id}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No valid fields provided for update on Task ID '{task_id}'",
            )

        # Update fields
        if task.title:
            existing_task.title = task.title
        if task.description:
            existing_task.description = task.description
        if task.status:
            existing_task.status = task.status

        # Commit changes
        db.commit()
        db.refresh(existing_task)

        logger.info(f"Task ID {task_id} updated successfully")
        return existing_task

    except HTTPException as e:
        logger.error(f"Error updating task with ID {task_id}: {e}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error while updating task with ID {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the task"
        )

@router.delete("/tasks/{task_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete task",
               description="Delete an existing task by its ID."
                           " Returns a 204 status code if successful.",
               responses={
                   204: {"description": "Task Deleted Successfully"},
                   404: {"description": "Task Not Found"},
                   500: {"description": "Internal Server Error"},
               },
)
def delete_task(
        task_id: int,
        db: Session = Depends(get_db)
):
    """
    Delete an existing task by its unique ID.
    """
    logger.info(f"Attempting to delete Task ID {task_id}")

    # Validation that the task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        logger.warning(f"Task with ID '{task_id}' not found. Deletion aborted.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found",
        )

    # Proceed with deletion
    db.delete(task)
    db.commit()

    logger.info(f"Task ID '{task_id}' deleted successfully")


@router.get("/tasks/user/{user_id}",
            response_model=list[TaskRead],
            summary="Get all tasks by user",
            description="Get all tasks by user belonging to a specific user.",
            responses={
                404: {"description": "Task not found for this user"},
                500: {"description": "Internal Server Error"},
            },)
def get_tasks_by_user(
        user_id: int,
        db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.owner_id == user_id).all()
    if not tasks:
        logger.info(f"No tasks found for user with ID {user_id}")
        raise HTTPException(
            status_code=404,
            detail="No tasks found for this user",
        )
    logger.info(f"Task found for your ID {user_id}: {tasks}")
    return tasks


@router.get("/tasks/status/{task_status}",
            response_model=list[TaskRead],
            summary="Get all tasks by status",
            description="Retrieve all tasks with a specific status"
                        " (e.g., 'completed', 'pending', 'in-progress').",
            responses={
                404: {"description": "No tasks found with the specified status"},
                500: {"description": "Internal Server Error"},
            },
)
def get_tasks_by_status(
        task_status: str = Path(..., description="The status to filter task by"),
        db: Session = Depends(get_db)
):
    logger.debug(f"Filtering tasks by status: {task_status}")
    tasks = db.query(Task).filter(Task.status == task_status).all()
    if not tasks:
        logger.info(f"No tasks found for status: {task_status}")
        raise HTTPException(status_code=404, detail=f"No tasks found with"
                                                    f" status '{task_status}'")
    logger.info(f"Found tasks: {tasks}")
    return tasks
