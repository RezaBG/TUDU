from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.models import User
from src.schemas import UserCreate , UserUpdate
from src.schemas.response import ResponseModel
from src.schemas.user import CurrentUser
from src.services import get_current_user
from src.services.dependencies import get_db
from src.services.task import get_password_hash
from src.services.crud import get_item_by_id, create_item

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

router = APIRouter()

def validate_user_existence(
        db: Session,
        user_id: int
) -> User:
    """
    Ensure that a user with the given ID exists in the database.
    """
    user = get_item_by_id(User, user_id, db)
    if user is None:
        logger.warning(f"User with ID '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )
    return user


@router.get(
    "/users",
    response_model=ResponseModel,
    summary="Get all users"
)
async def get_all_users(
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
) -> ResponseModel:
    """
    Fetch all users from the database.
    """
    logger.info(f"Fetching users requested by: {current_user.username}")

    users = db.query(User).all()

    if not users:
        logger.info("No users found")
        return ResponseModel(
            status="success",
            message="No users found",
            data=[]
        )

    # Construct response data from user records
    users_data = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    logger.info(f"Found {len(users)} user(s).")
    return ResponseModel(
        status="success",
        message="Users retrieved successfully",
        data=users_data
    )


@router.post("/user",
             response_model=ResponseModel,
             status_code=status.HTTP_201_CREATED,
             summary="Create a User",
)
def create_user(
        user: UserCreate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> ResponseModel:
    """
    Register a new user (requires authentication).
    """
    logger.info(f"User creation requested by admin: {current_user.username} (ID: {getattr(current_user, 'id', 'unknown')})")

    # Authorization check: Ensure the user is in admin
    if not getattr(current_user, "is_admin", False):
        logger.warning(f"Unauthorized user '{current_user.username}' attempted to create a user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User '{current_user.username}' is not authorized to create users."
        )

    # Check if username or email already exists
    existing_user = db.query(User).filter(
        or_(
            User.username == user.username,
            User.email.ilike(user.email)
        )
    ).first()

    if existing_user:
        logger.warning(f"Create user failed: Username '{user.username}' or Email '{user.email}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already exists"
        )

    # Hash the password and prepare user data
    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "email": user.email.lower(),
        "hashed_password": hashed_password,
        "disabled": user.disabled,
    }

    # Insert user into the database
    new_user = create_item(User, user_data, db)
    logger.info(f"User '{new_user.username}' created successfully with ID {new_user.id}")
    return ResponseModel(
        status="success",
        message=f"User created successfully",
        data={
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    )


@router.get("/users/{user_id}",
            response_model=ResponseModel,
            summary="Get a User by ID",
)
def get_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> ResponseModel:
    """
    Retrieve a user's details by their unique ID.
    """
    logger.info(f"Retrieve user: {current_user}")
    user = validate_user_existence(db, user_id)
    logger.info(f"User with ID '{user_id}' retrieved successfully")
    return ResponseModel(
        status="success",
        message="User retrieved successfully",
        data={"id": user.id, "username": user.username, "email": user.email},
    )


@router.put("/users/{user_id}",
            response_model=ResponseModel,
            summary="Update a User",
)
def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> ResponseModel:
    """
    Update a user details by their unique ID.
    """
    logger.info(f"Update the user: {current_user}")
    user = validate_user_existence(db, user_id)

    # Added validation for empty update payload
    if not any([user_update.username, user_update.email, user_update.disabled, user_update.password]):
        logger.warning(f"No valid fields provided for update on User ID '{user_id}'.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update."
        )

    # Improved duplicate validation logic
    if user_update.username or user_update.email:
        duplicate_check = db.query(User).filter(
            or_(
                User.username == user_update.username,
                User.email == user_update.email
            ),
            User.id != user_id,
        ).first()
        if duplicate_check:
            logger.warning(f"Duplicate user '{user_update.username}' or Email '{user_update.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or Email already exists"
            )

    # Apply updates to the user
    if user_update.username:
        user.username = user_update.username
    if user_update.email:
        user.email = user_update.email
    if user_update.disabled is not None:
        user.disabled = user_update.disabled
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(user)

    logger.info(f"User with ID '{user_id}' updated successfully.")
    return ResponseModel(
        status="success",
        message="User updated successfully",
        data={"id": user.id, "username": user.username, "email": user.email},
    )


@router.delete("/users/{user_id}",
               response_model=ResponseModel,
               summary="Delete a User",
)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
) -> ResponseModel:
    """
    Delete a user by their unique ID.
    """
    logger.info(f"Delete user: {current_user}")
    user = validate_user_existence(db, user_id)

    db.delete(user)
    db.commit()

    logger.info(f"User with ID '{user_id}' deleted successfully.")
    return ResponseModel(
        status="success",
        message=f"User with ID '{user_id}' deleted successfully",
        data=None
    )
