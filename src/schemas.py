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
    pass

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    disabled: bool = False

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserUpdate(UserBase):
    disabled: bool

# Import the UserRead at the bottom - Avoid circular imports
# from .schemas import UserRead
TodoRead.update_forward_refs()
