from sqlalchemy.orm import Session
from . import models, schemas
from src.models import Todo

def get_todo(db: Session):
    return db.query(Todo).all()


def create_todo(db: Session, todo: schemas.TodoCreate):
    db_todo = models.Todo(title=todo.title, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        return None
    db_todo.title = todo.title
    db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db:Session, todo_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        return None
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted"}


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, email=user.email, disabled=user.disabled)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

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

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
