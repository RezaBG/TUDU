from typing import Optional
from pydantic import BaseModel
from src.enums.task_status import TaskStatus
from src.schemas.user import UserRead

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

    class Config:
        orm_mode = True
        use_enum_values = True

class TaskCreate(TaskBase):
    owner_id: int


class TaskRead(TaskBase):
    id: int
    owner: Optional[UserRead] = None


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
