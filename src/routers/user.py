from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models import User
from src.schemas import UserCreate, UserRead
from src.services.dependencies import get_db
from src.services.task import get_password_hash

router = APIRouter()


@router.post("/users",
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED,
             summary="Create a User",
             description="Register a new user by providing a unique username, email, and password."
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter_by(username=user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_password_hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        disabled=user.disabled,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/{user_id}",
            response_model=UserRead,
            summary="Get a User by ID",
            description="Fetch a user's details by their unique ID. Returns a 404 error if the user is not found."
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
