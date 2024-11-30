from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, constr

class UserBase(BaseModel):
    username: constr(
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )
    """Must be 3-32 characters long, only letters, digits, '_', '-', or '.' are allowed."""

    email: EmailStr
    disabled: Optional[bool] = False


class UserCreate(UserBase):
    password: constr(
        min_length=8,
    )
    """Password must be at least 8 characters long."""


class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Optional[constr(
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )] = None
    """Username is optional, but if provided, it must be 3-32 characters long, containing only letters, digits, '_', '-', or '.'."""

    email: Optional[EmailStr] = None
    disabled: Optional[bool] = None
    password: Optional[constr(
        min_length=8,
    )] = None
    """Password must be at least 8 characters long, but it’s optional for updates."""


class CurrentUser(BaseModel):
    username: str


