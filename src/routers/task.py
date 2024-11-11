from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.services import task
from src.schemas import TodoCreate, TodoRead, TodoUpdate, UserRead
from src.services.dependencies import get_current_user, get_db

router = APIRouter()

# Get route to retrieve todos
@router.get("/todos", response_model=list[TodoRead])
async def read_todos(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    return task.get_user_todos(db=db, user_id=current_user.id)

@router.post("/todos", response_model=TodoRead)
async def create(todo: TodoCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    return task.create_todo(db=db, todo=todo, user_id=current_user.id)

@router.put("/todos/{todo_id}", response_model=TodoRead)
async def update(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    return task.update_todo(db=db, todo_id=todo_id, todo=todo, user_id=current_user.id)

@router.delete("/todos/{todo_id}")
async def delete(todo_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    return task.delete_todo(db=db, todo_id=todo_id, user_id=current_user.id)