from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.models import User
from src.schemas import UserCreate , UserUpdate
from src.schemas.response import ResponseModel
from src.services.dependencies import get_db
from src.services.task import get_password_hash
from src.services.crud import get_item_by_id, create_item
from src.routers.auth import format_response

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

router = APIRouter()



@router.post("/users",
             response_model=ResponseModel,
             status_code=status.HTTP_201_CREATED,
             summary="Create a User",
             description="Register a new user by providing a unique username, "
                         "email, and password.",
             responses={
                 400: {"description": "Bad Request - User already exists"},
                 422: {"description": "Validation Error"},
                 500: {"description": "Internal Server Error"},
             },
)
def create_user(
        user: UserCreate,
        db: Session = Depends(get_db)
    ) -> ResponseModel:
    # Validate if username and email are unique
    existing_user = db.query(User).filter(
        or_(User.username == user.username, User.email == user.email)
    ).first()
    if existing_user:
        logger.warning(f"Create user failed: Username '{user.username}' "
                       f"or Email '{user.email}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already exists"
        )

    # Hash the password securely
    hashed_password = get_password_hash(user.password)

    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "disabled": user.disabled,
    }
    logger.info(f"Creating user with sanitized data: '{user_data['username']}', "
                f"'{user_data['email']}'")

    # Create user
    new_user = create_item(User, user_data, db)

    logger.info(f"User '{new_user.username}' created successfully with ID {new_user.id}")
    return format_response(
        status="success",
        message=f"User created successfully",
        data={"id": new_user.id, "username": new_user.username, "email": new_user.email}
    )


@router.get("/users/{user_id}",
            response_model=ResponseModel,
            summary="Get a User by ID",
            description="Fetch a user's details by their unique ID. Returns a 404 error "
                        "if the user is not found.",
            responses={
                404: {"description": "User Not Found"},
                500: {"description": "Internal Server Error"},
            },
)
def get_user(
        user_id: int,
        db: Session = Depends(get_db)
    ) -> ResponseModel:
    try:
        user = get_item_by_id(User, user_id, db)

        if user is None:
            logger.warning(f"User with ID '{user_id}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found"
            )

        logger.info(f"Retrieved user with ID: {user_id}")
        return format_response(
            status="success",
            message=f"User retrieved successfully",
            data={"id": user.id, "username": user.username, "email": user.email}
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Failed to retrieve user with ID: {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the user"
        )


@router.put("/users/{user_id}",
            response_model=ResponseModel,
            summary="Update a User",
            description="Update the details of a user by their unique ID.",
            responses={
                404: {"description": "User not found"},
                400: {"description": "Bad request - Validation Error"},
                500: {"description": "Internal Server Error"},
            },
)
def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: Session = Depends(get_db)
    ) -> ResponseModel:
    """
    Update a user details by their unique ID.
    """
    try:
        # Öog the received payload
        logger.debug(f"Received update payload for user ID {user_id}: {user_update}")

        # Ensure the user exists
        user = get_item_by_id(User, user_id, db)
        if user is None:
            logger.warning(f"User with ID '{user_id}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_id}' not found"
            )


        # Check for duplicate username or email
        if user_update.username or user_update.email:
            duplicate_check = db.query(User).filter(
                or_(
                    User.username == user_update.username,
                    User.email == user_update.email
                ),
                User.id != user_id
            ).first()
            if duplicate_check:
                logger.warning(f"Duplicate username '{user_update.username}' "
                               f"or email '{user_update.email}' detected")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or Email already exists"
                )

        # Check for empty update payload
        if not any([
            user_update.username,
            user_update.email,
            user_update.disabled,
            user_update.password,
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )

        # Update fields
        if user_update.username is not None:
            user.username = user_update.username
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.disabled is not None:
            user.disabled = user_update.disabled
        if user_update.password is not None:
            user.hashed_password = get_password_hash(user_update.password)

        # Commit changes
        db.commit()
        db.refresh(user)

        logger.info(f"User with ID '{user_id}' updated successfully.")
        return format_response(
            status="success",
            message=f"User updated successfully",
            data={"id": user.id, "username": user.username, "email": user.email}
        )

    except HTTPException as e:
        logger.error(f"Error updating user with ID: {user_id}: {e}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error while updating user with ID: {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the user"
        )

@router.delete("/users/{user_id}",
               response_model=ResponseModel,
               summary="Delete a User",
               description="Delete a user by their unique ID.",
               responses={
                   404: {"description": "User Not Found"},
                   500: {"description": "Internal Server Error"},
               },
)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db)
) -> ResponseModel:
    """
    Delete a user by their unique ID.
    """
    try:
        # Ensure the user exists
        user = get_item_by_id(User, user_id, db)
        if user is None:
            logger.warning(f"User with ID '{user_id}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_id}' not found"
            )

        # Delete the user
        db.delete(user)
        logger.info(f"User with ID '{user_id}' deleted successfully.")
        db.commit()

        logger.info(f"User with ID '{user_id}' deleted successfully.")
        return format_response(
            status="success",
            message=f"User with ID '{user_id}' deleted successfully",
            data=None
        )

    except HTTPException as e:
        logger.error(f"Error deleting user with ID: {user_id}: {e}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error while deleting user with ID: {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting user"
        )