from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column


from src.services.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)

    # Relationship to user
    owner = relationship("User", back_populates="todos")
