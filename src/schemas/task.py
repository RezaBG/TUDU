from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict
from src.schemas.user import UserRead


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[Literal["pending", "completed", "in-process"]] = None


class TaskCreate(TaskBase):
    owner_id: int


class TaskRead(TaskBase):
    id: int
    owner: Optional[UserRead] = None

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
