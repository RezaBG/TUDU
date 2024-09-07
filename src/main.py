from fastapi import FastAPI, Depends, HTTPException
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

@app.put("/todos/{todo_id}", response_model=schemas.TodoRead)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    updated_todo = crud.update_todo(db=db, todo_id=todo_id, todo=todo)
    if updated_todo is None:
        raise HTTPException(status_code= 404, detail="Todo not found - 404")
    return updated_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    deleted_todo = crud.delete_todo(db=db, todo_id=todo_id)
    if deleted_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found - 404") 
    return deleted_todo
