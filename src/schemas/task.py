from typing import Optional

from pydantic import BaseModel

from src.schemas.user import UserRead


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    owner_id: int


class TaskRead(TaskBase):
    id: int
    owner: Optional[UserRead] = None

    class Config:
        from_attributes = True


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
