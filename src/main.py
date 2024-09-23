from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from fastapi.openapi.utils import get_openapi


from src import crud, models, schemas  
from src.database import SessionLocal, engine 

# Secret key, algorithms, and expriation time for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password haching context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Custom security definition for Bearer token
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API that uses Bearer token",
        routes=app.routes,
    )
    # Add custom security scheme to OpenAPI schema
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # Add global security requirement for all endpoints
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Set the custom OpenAPI schema
app.openapi = custom_openapi


# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)

# Function to create JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Funciton to get user by username
def get_user(db, username: str):
    return crud.get_user_by_username(db, username=username)

# Authenticate user
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# Get current user using the JWT token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db=db, username=username)
    if user is None:
        raise credentials_exception
    return user

# Route to create a token (login)
@app.post("/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect user or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
        )
    return {"access_token": access_token, "token_type": "bearer"}


# Route to get the current logged-in user:
@app.get("/users/me", response_model=schemas.UserRead)
async def read_users_me(current_user: schemas.UserRead = Depends(get_current_user)):
    return current_user

# Rouet a get all todos for the logged-in user
@app.get("/todos", response_model=list[schemas.TodoRead])
async def read_todos(db: Session = Depends(get_db), current_user: schemas.UserRead = Depends(get_current_user)):
    return crud.get_user_todos(db=db, user_id=current_user.id)

# Route to create a new todo
@app.post("/todos", response_model=schemas.TodoRead)
async def create(todo: schemas.TodoCreate, db: Session = Depends(get_db), current_user: schemas.UserRead = Depends(get_current_user)):
    return crud.create_todo(db=db, todo=todo, user_id=current_user.id)

# Route to update an existing todo
@app.put("/todos/{todo_id}", response_model=schemas.TodoRead)
async def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db), current_user: schemas.UserRead = Depends(get_current_user)):
    updated_todo = crud.update_todo(db=db, todo_id=todo_id, todo=todo, user_id=current_user.id)
    if updated_todo is None:
        raise HTTPException(status_code= 404, detail="Todo not found - 404")
    return updated_todo

# Route for delete todo
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    deleted_todo = crud.delete_todo(db=db, todo_id=todo_id)
    if deleted_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found - 404") 
    return deleted_todo

# Route for create a new user
@app.post("/register", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

# Route to get all users with paginaiton
@app.get("/users/", response_model=list[schemas.UserRead])
async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db=db, skip=skip, limit=limit)

# Route to get a single user by their ID
@app.get("/users/{user_id}", response_model=schemas.UserRead)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    read_user = crud.get_user(db=db, user_id=user_id)
    if read_user is None:
        raise HTTPException(status_code=404, detail="user not found - 404")
    return read_user

# Route to update a user
@app.put("/users/{user_id}", response_model=schemas.UserRead)
async def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(db=db, user_id=user_id, user=user)

# Route to delete a user
@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.delete_user(db=db, user_id=user_id)
