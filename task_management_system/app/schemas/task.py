from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.task import TaskPriority, TaskStatus
from app.schemas.user import UserBrief


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    creator: UserBrief
    assignee: Optional[UserBrief]

    model_config = {"from_attributes": True}


class PaginatedTasks(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[TaskResponse]
