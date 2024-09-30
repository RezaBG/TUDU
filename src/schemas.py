from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    disabled: bool = False

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserUpdate(UserBase):
    disabled: bool


# Todo Schemas
class TodoBase(BaseModel):
    title: str
    description: str

class TodoCreate(TodoBase):
    #user_id: int
    pass

class TodoRead(TodoBase):
    id: int
    owner: Optional["UserRead"]

    class Config:
        from_attributes = True

class TodoUpdate(TodoBase):
    pass

# Import the UserRead at the bottom - Avoid circular imports
# from .schemas import UserRead
TodoRead.update_forward_refs()
