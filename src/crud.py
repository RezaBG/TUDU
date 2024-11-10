from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
from src.models import Todo
from passlib.context import CryptContext

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str: 
    return pwd_context.hash(password)

# Get all todos for a specific user
def get_user_todos(db: Session, user_id: int):
    return db.query(models.Todo).filter(models.Todo.owner_id == user_id).all()

# Create a new todo for a user
def create_todo(db: Session, todo: schemas.TodoCreate, user_id: int):
    db_todo = models.Todo(title=todo.title, description=todo.description, owner_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Update a todo based on its ID
def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate, user_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found or you do not have permission to update this todo")

    db_todo.title = todo.title
    db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Delete a todo
def delete_todo(db:Session, todo_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        return None
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted"}

# Create a new user
def create_user(db: Session, user: schemas.UserCreate):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password,
        disabled=user.disabled
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Create a single user by their ID
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Get all users with pagination
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# Update a user
def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    db_user.username = user.username
    db_user.email = user.email
    db_user.disabled = user.disabled
    db.commit()
    db.refresh(db_user)
    return db_user

# Delete a user
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
### this 
