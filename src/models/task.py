from sqlalchemy import ForeignKey, Integer, String, Enum, event
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.enums.task_status import TaskStatus
from src.services.database import Base

class Task(Base):
    __tablename__ = "tasks"

    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        # default="pending",
        nullable=False)  # Pass enum, not .value


    # Relationship to user
    owner = relationship("User", back_populates="todos")

@event.listens_for(Task, "before_insert")
def debug_before_insert(mapper, connection, target):
    print(f"Task being inserted: {target.title}, {target.status}")
