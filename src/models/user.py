from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from src.services.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)

    # Relationship to user
    todos = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
