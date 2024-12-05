from sqlalchemy import ForeignKey, Integer, String, Enum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.services.database import Base


class TaskStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)

    # Relationship to user
    owner = relationship("User", back_populates="todos")
