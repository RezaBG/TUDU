from fastapi import APIRouter, Depends, status, HTTPException, Path
from sqlalchemy.orm import Session

from src.models import Task, User
from src.schemas import TaskCreate, TaskUpdate
from src.schemas.response import ResponseModel
from src.schemas.user import CurrentUser
from src.services.dependencies import get_db, get_current_user
from src.services.crud import get_item_by_id, create_item
from src.enums.task_status import TaskStatus

import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Helper function for task validation
def validate_task_existence(task_id: int, db: Session, current_user: CurrentUser) -> Task:
    """
    Ensure that a task exists and belongs to the current user.
    """
    task = get_item_by_id(Task, task_id, db)
    if not task:
        logger.warning(f"Task with ID '{task_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found."
        )
    if task.owner_id != current_user.id:
        logger.warning(f"Unauthorized access: Task ID '{task_id}' is not owned by User ID '{current_user.id}'.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this task."
        )
    return task


@router.post("/tasks",
             response_model=ResponseModel,
             status_code=status.HTTP_201_CREATED,
             summary="Create a Task")
def create_task(
        task: TaskCreate,
        db: Session = Depends(get_db)
) -> ResponseModel:
    """
    Create a new task for the authenticated user.
    """
    owner = db.query(User).filter_by(id=task.owner_id).first()
    if not owner:
        logger.warning(f"Task creation failed: Owner with ID '{task.owner_id}' not found.")
        raise HTTPException(
            status_code=404,
            detail=f"Owner with ID '{task.owner_id}' not found."
        )
    logger.debug(f"Received task status: {task.status}")

    task_status = task.status.lower()
    logger.debug(f"Task status after conversion: {task_status}")

    try:
        # Make sure to use TaskStatus enum properly (ensure it's using the correct value)
        task_status = TaskStatus[task.status.lower()]
        logger.debug(f"Task status after conversion: {task_status}")
    except KeyError:
        logger.warning(f"Invalid task status: {task.status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task status: '{task.status}'. Allowed values are: 'pending', 'in-progress', 'completed'."
        )

    task_data = {
        "title": task.title,
        "description": task.description,
        "owner_id": task.owner_id,
        "status": task_status.value,
    }

    new_task = create_item(Task, task_data, db)
    logger.info(f"Task '{new_task.title}' created successfully with ID {new_task.id} and status: {new_task.status}")
    return ResponseModel(
        status="success",
        message="Task created successfully.",
        data={"id": new_task.id, "title": new_task.title, "status": new_task.status}
    )


@router.get("/tasks",
            response_model=ResponseModel,
            summary="Get all tasks"
            )
def get_tasks(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> ResponseModel:
    """
    Retrieve all tasks belonging to the authenticated user.
    """
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    if not tasks:
        logger.info(f"No tasks found for User ID '{current_user.id}'.")
        return ResponseModel(
            status="success",
            message="No tasks found.",
            data=[]
        )

    task_data = [{"id": task.id, "title": task.title, "status": task.status, "description": task.description} for task in tasks]
    logger.info(f"Retrieved {len(tasks)} tasks for User ID '{current_user.id}'.")
    return ResponseModel(
        status="success",
        message="Tasks retrieved successfully.",
        data=task_data
    )


@router.get("/tasks/{task_id}",
            response_model=ResponseModel,
            summary="Get a Task by ID",
)
def get_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> ResponseModel:
    """
    Retrieve a Task by its unique ID.
    """
    # Fetch the task from the database
    task = validate_task_existence(task_id, db, current_user)
    logger.info(f"Task with ID '{task_id}' retrieved successfully.")
    return ResponseModel(
        status="success",
        message="Task retrieved successfully.",
        data={"id": task.id, "title": task.title, "status": task.status, "description": task.description}
    )


@router.put("/tasks/{task_id}",
            response_model=ResponseModel,
            summary="Update a Task",
)
def update_task(
        task_id: int,
        task_update: TaskUpdate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> ResponseModel:
    """
    Update an existing task by its unique ID.
    """
    task = validate_task_existence(task_id, db, current_user)

    if not any([task_update.title, task_update.description, task_update.status]):
        logger.warning(f"No valid fields provided for update on Task ID '{task_id}'.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update."
        )

    if task_update.title:
        task.title = task_update.title
    if task_update.description:
        task.description = task_update.description
    if task_update.status:
        task.status = task_update.status

    db.commit()
    db.refresh(task)
    logger.info(f"Task with ID '{task.title}' updated successfully.")
    return ResponseModel(
        status="success",
        message="Task updated successfully.",
        data={"id": task.id, "title": task.title, "status": task.status, "description": task.description}
    )


@router.delete("/tasks/{task_id}",
               response_model=ResponseModel,
               summary="Delete task",
)
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    """
    Delete an existing task by its unique ID.
    """
    # Validation that the task exists
    task = validate_task_existence(task_id, db, current_user)
    db.delete(task)
    db.commit()
    logger.info(f"Task ID '{task_id}' deleted successfully by user ID '{current_user.id}'")
    return ResponseModel(
        status="success",
        message="Task deleted successfully.",
        data=None
    )


@router.get("/tasks/status/{task_status}",
            response_model=ResponseModel,
            summary="Get all tasks by status",
)
def get_tasks_by_status(
        task_status: str = Path(..., description="The status to filter task by"),
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> ResponseModel:
    """
    Retrieve all tasks with a specific status.
    """
    if task_status not in [s.value for s in TaskStatus]:
        logger.warning(f"Invalid task status '{task_status}'.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task status: '{task_status}'."
        )

    tasks = db.query(Task).filter(Task.status == task_status, Task.owner_id == current_user.id).all()

    if not tasks:
        logger.info(f"No tasks found for status '{task_status}'")
        return ResponseModel(
            status="success",
            message="No tasks found with the specified status.",
            data=[]
        )

    task_data = [{"id": task.id, "title": task.title, "status": task.status, "description": task.description} for task in tasks]
    logger.info(f"Found tasks for status '{task_status}': {len(tasks)}")
    return ResponseModel(
        status="success",
        message="Tasks retrieved successfully.",
        data=task_data
    )
