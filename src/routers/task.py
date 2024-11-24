from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.models import Task
from src.schemas import TaskCreate, TaskRead, TaskUpdate
from src.services.dependencies import get_db
from src.services.crud import get_item_by_id, create_item, delete_item

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
    task_data = {
        "title": task.title,
        "description": task.description,
        "owner_id": task.owner_id,
    }
    new_task = create_item(Task, task_data, db)
    logger.info(f"Task '{new_task.title}' created successfully with ID {new_task.id}")
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
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    existing_task = get_item_by_id(Task, task_id, db)
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
    logger.info(f"Deleting Task ID {task_id}")
    delete_item(Task, task_id, db)
    logger.info(f"Task ID {task_id} deleted successfully")
    return {"message": "Task deleted"}
