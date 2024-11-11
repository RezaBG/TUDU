from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.schemas import TaskCreate, TaskUpdate, UserCreate
from src.models import Task, User
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Task CRUD operations
def get_user_todos(db: Session, user_id: int):
    return db.query(Task).filter_by(owner_id=user_id).all()

def create_todo(db: Session, todo: TaskCreate, user_id: int):
    db_todo = Task(title=todo.title, description=todo.description, owner_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo: TaskUpdate, user_id: int):
    db_todo = db.query(Task).filter_by(id=todo_id, owner_id=user_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found or you do not have permission to update this todo")
    db_todo.title = todo.title
    db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int, user_id: int):
    db_todo = db.query(Task).filter_by(id=todo_id, owner_id=user_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted"}

def create_user(db: Session, user: UserCreate):
    existing_user = db.query(User).filter_by(username=user.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        disabled=user.disabled,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Other user-related CRUD functions
def get_user(db: Session, user_id: int):
    return db.query(User).filter_by(id=user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter_by(username=username).first()
