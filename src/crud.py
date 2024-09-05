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