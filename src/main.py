from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from src import crud, models, schemas  
from src.database import SessionLocal, engine 

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to get all todos
@app.get("/todos", response_model=list[schemas.TodoRead])
async def read_todos(db: Session = Depends(get_db)):
    todos = crud.get_todo(db)
    return todos

# Route to create a new todo
@app.post("/todos", response_model=schemas.TodoRead)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db=db, todo=todo)

