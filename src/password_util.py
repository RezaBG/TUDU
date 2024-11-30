import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.user import User

import logging
logging.basicConfig(level=logging.INFO)


# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup (replace with your actual database configuration)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://dev:dev@localhost/tudu")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_password(username: str, plain_password: str):
    session = SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    if user:
        is_valid = pwd_context.verify(plain_password, user.hashed_password)
        logging.info(f"Password for {username} is valid: {is_valid}")
    else:
        logging.warning(f"User {username} does not exist.")
    session.close()

def update_password(username: str, new_password: str):
    session = SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    if user:
        hashed_password = pwd_context.hash(new_password)
        user.hashed_password = hashed_password
        session.commit()
        logging.info(f"Password for {username} has been updated.")
    else:
        logging.info(f"User {username} does not exist. Creating new password.")
        hashed_password = pwd_context.hash(new_password)
        new_user = User(username=username, hashed_password=hashed_password, email=f"{username}@example.com", disabled=False)
        session.add(new_user)
        session.commit()
        logging.info(f"User {username} has been created.")
    session.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  Verify Password: python password_util.py verify <username> <password>")
        print("  Update Password: python password_util.py update <username> <new_password>")
        sys.exit(1)

    action = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    if action == "verify":
        verify_password(username, password)
    elif action == "update":
        update_password(username, password)
    else:
        print("Invalid action. Use 'verify' or 'update'.")