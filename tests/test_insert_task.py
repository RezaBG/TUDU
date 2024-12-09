from sqlalchemy.orm import Session
from src.models import Task, TaskStatus

def test_insert_task(db: Session):
    task = Task(
        title="Test Task",
        description="Task Description",
        owner_id=1,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    assert task.status == TaskStatus.PENDING
