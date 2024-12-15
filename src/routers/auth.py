from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
import logging
import os

from src.services.dependencies import get_db, get_current_user
from src.services.auth import create_access_token
from src.models.user import User
from src.schemas.user import CurrentUser
from src.schemas.response import ResponseModel

# Initialize router and logger
router = APIRouter()
logger = logging.getLogger("auth")
logger.setLevel(logging.INFO)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper function to verify the user's password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# Helper function to get a user by username
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Fetch an active user by username."""
    return db.query(User).filter(User.username == username, User.disabled == False).first()

# New function to hash a password before storing it
def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

# New function to create a user with hashed password
def create_user(db: Session, username: str, email: str, password: str, is_admin: bool = False):
    """Fetch a new user with hashed password."""
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password, is_admin=is_admin)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post(
    "/token",
    response_model=ResponseModel,
    summary="Login and get access token"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> ResponseModel:
    """
    Login to the application and return a JWT token.
    """
    # Log the username for debugging
    if os.getenv("ENVIRONMENT") == "development":
        logger.debug(f"Login attempt for username: {form_data.username}")

    # Validate user credentials
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Invalid credentials for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate and return JWT Token
    access_token = create_access_token(data={"sub": user.username})
    logger.debug(f"Token generated successfully for user name: {user.username}")
    return ResponseModel(
        status="success",
        message="Authentication successful.",
        data={"access_token": access_token, "token_type": "bearer"},
    )


@router.get(
    "/protected",
    response_model=ResponseModel,
    summary="Protected route"
)
async def protected_route(
        current_user: CurrentUser = Depends(get_current_user),
) -> ResponseModel:
    """
    Protected endpoint that requires authentication
    """
    logger.info(f"Protected route assessed by user: {current_user.username}")
    return ResponseModel(
        status="success",
        message=f"Hello, {current_user.username}! You have access to this protected route.",
    )
