from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas import UserCreate, UserRead
from src.models import User
from src.services.dependencies import get_db
from src.services.task import get_password_hash


router = APIRouter()

@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate , db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing_user:
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already exist")
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = get_password_hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        disabled=user.disabled,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IndentationError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create user due to a database constraint")

    return new_user

@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user