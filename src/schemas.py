from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoRead(TodoCreate):
    id: int

    class Config:
        orm_mode = True

