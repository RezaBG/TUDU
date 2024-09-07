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
    return db_todo

