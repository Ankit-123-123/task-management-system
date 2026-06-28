import enum
from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Enum, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    done = "done"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(TaskStatus), default=TaskStatus.todo, nullable=False, index=True
    )
    priority = Column(
        Enum(TaskPriority), default=TaskPriority.medium, nullable=False, index=True
    )
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    comments = Column(Text, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    creator = relationship("User", foreign_keys=[created_by_id], back_populates="created_tasks")
    assignee = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
