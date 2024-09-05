from sqlalchemy.orm import Session

from .import models, schemas

def get_todos(db: Session):
    return db.query(Todo).all()


def create_todo(db: Session, todos: schemas.TodoCreate):
    db_todo = models.Todo(title=todo.title, description=todo.description)
    db_add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo