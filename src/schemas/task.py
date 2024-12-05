from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict
from src.schemas.user import UserRead


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[Literal["pending", "in-progress", "completed"]] = None  # Enum values directly


class TaskCreate(TaskBase):
    owner_id: int


class TaskRead(TaskBase):
    id: int
    owner: Optional[UserRead] = None

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["pending", "in-progress", "completed"]] = None
