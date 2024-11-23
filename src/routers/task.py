from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models import Task
from src.schemas import TaskCreate, TaskRead, TaskUpdate
from src.services.dependencies import get_db

router = APIRouter()


@router.post("/tasks",
             response_model=TaskRead,
             status_code=status.HTTP_201_CREATED,
             summary="Create a Task",
             description="Create a new task by providing the title, description, and owner ID."
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        owner_id=task.owner_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/tasks/{task_id}",
            response_model=TaskRead,
            summary="Get a Task by ID",
            description="Retrieve a task by unique ID. If the task is not found, a 404 error is returned",
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter_by(id=task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.put("/tasks/{task_id}",
            response_model=TaskRead,
            summary="Update a Task",
            description="Update an existing task by its ID. Requires the updated title and description",
)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    existing_task = db.query(Task).filter_by(id=task_id).first()
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    existing_task.title = task.title
    existing_task.description = task.description
    db.commit()
    db.refresh(existing_task)
    return existing_task


@router.delete("/tasks/{task_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete task",
               description="Delete an existing task by its ID. Returns a 204 status code if successful.",
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter_by(id=task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
