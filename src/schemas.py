from pydantic import BaseModel
from typing import Optional

# Todo Schemas
class TodoBase(BaseModel):
    title: str
    description: str


class TodoCreate(TodoBase):
    pass


class TodoRead(TodoBase):
    id: int
    owner: Optional["UserRead"]

    class Config:
        orm_mode = True


class TodoUpdate(TodoBase):
    title: str
    description: str


# User Schemas
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    disabled: bool

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    disabled: bool

# Import the UserRead at the bottom - Avoid circular imports
from .schemas import UserRead