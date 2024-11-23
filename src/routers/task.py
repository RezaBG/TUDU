from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models import Task
from src.schemas import TaskCreate, TaskRead, TaskUpdate
from src.services.dependencies import get_db

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
             description="Create a new task by providing the title, description, and owner ID.",
             responses={
                 400: {"description": "Bad Request - Invalid Task Data"},
                 500: {"description": "Internal Server Error"},
             },
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating task with title: {task.title}")
    new_task = Task(
        title=task.title,
        description=task.description,
        owner_id=task.owner_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    logger.info(f"Task '{task.title}' created successfully with ID {new_task.id}")
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
    task = db.query(Task).filter_by(id=task_id).first()
    if task is None:
        logger.info(f"Task with ID {task_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
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
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    existing_task = db.query(Task).filter_by(id=task_id).first()
    if existing_task is None:
        logger.warning(f"Update failed: Task with ID {task_id} not found")
        raise HTTPException(status_code=404, detail="Task not found")

    logger.info(f"Updating Task ID {task_id}. Old title: {existing_task.title}, new title: {task.title}")

    existing_task.title = task.title
    existing_task.description = task.description
    db.commit()
    db.refresh(existing_task)

    logger.info(f"Task ID {task_id} updated successfully")
    return existing_task


@router.delete("/tasks/{task_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete task",
               description="Delete an existing task by its ID. Returns a 204 status code if successful.",
               responses={
                   404: {"description": "Task Not Found"},
                   500: {"description": "Internal Server Error"},
               },
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter_by(id=task_id).first()
    if task is None:
        logger.warning(f"Delete failed: Task with ID {task_id} not found")
        raise HTTPException(status_code=404, detail="Task not found")

    logger.info(f"Deleting Task ID {task_id}. Title: {task.title}")

    db.delete(task)
    db.commit()

    logger.info(f"Task ID {task_id} deleted successfully")
    return {"message": "Task deleted"}
