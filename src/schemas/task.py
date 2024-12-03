from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.models.task import TaskStatus
from src.schemas.user import UserRead


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskCreate(TaskBase):
    owner_id: int


class TaskRead(TaskBase):
    id: int
    owner: Optional[UserRead] = None

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
