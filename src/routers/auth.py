from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src.services.dependencies import get_db, get_current_user
from src.services.auth import create_access_token
from src.models.user import User
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.user import CurrentUser
from src.schemas.response import ResponseModel
from typing import Optional
import logging
import os

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper function to verify the user's password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Helper function to get a user by username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter_by(username=username).first()


def format_response(status: str, message: str, data: Optional[dict] = None):
    if data is None:
        data = {}
    return {
        "status": status,
        "message": message,
        "data": data,
    }

@router.post("/token", response_model=ResponseModel)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login to the application and return a JWT token
    """
    try:
        if os.getenv("ENVIRONMENT", "development") == "development":
            logging.debug(f"Received username: {form_data.username}")

        # Fetch user
        user = get_user_by_username(db, form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            logging.debug(f"Invalid credentials or user not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate JWT Token
        access_token = create_access_token(data={"sub": user.username})
        logging.debug(f"Generated token for user: {user.username}")
        return format_response(
            status="success",
            message="Authentication successful.",
            data={"access_token": access_token, "token_type": "bearer"},
        )

    except ValueError as ve:
        logging.error(f"Validation error during authentication: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data. Please verify and try again.",
        )
    except Exception as e:
        logging.error(f"Unexpected error during authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please try again later.",
        )


@router.get("/protected", response_model=ResponseModel)
async def protected_route(
        current_user: CurrentUser = Depends(get_current_user),
):
    """
    Protected endpoint that requires authentication
    """
    try:
        logging.info(f"Access granted to user: {current_user.username}")
        return format_response(
            status="success",
            message=f"Hello, {current_user.username}! You have access to this protected route.",
        )
    except Exception as e:
        logging.error(f"Error in protected route for user : {current_user.username}, Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred, Please try again later.",
        )