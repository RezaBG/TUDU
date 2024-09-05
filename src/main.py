from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from src.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/items/{item_id}")
async def read_item(item_id , db: Session = Depends(get_db)):
    return {"item_id": "Test Database connection"}




