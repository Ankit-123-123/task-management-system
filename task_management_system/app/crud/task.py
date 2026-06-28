from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, payload: TaskCreate, created_by_id: int) -> Task:
    task = Task(
        **payload.model_dump(exclude_unset=False),
        created_by_id=created_by_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Session, task: Task, payload: TaskUpdate) -> Task:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def list_tasks_for_member(
    db: Session,
    *,
    user_id: int,
    search: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[int, List[Task]]:
    """Returns only tasks the member created or is assigned to."""
    query = db.query(Task).filter(
        or_(Task.created_by_id == user_id, Task.assigned_to_id == user_id)
    )
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(Task.title.ilike(pattern), Task.description.ilike(pattern))
        )
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    total = query.count()
    tasks = (
        query.order_by(Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, tasks


def list_tasks(
    db: Session,
    *,
    search: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assigned_to_id: Optional[int] = None,
    created_by_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[int, List[Task]]:
    query = db.query(Task)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(Task.title.ilike(pattern), Task.description.ilike(pattern))
        )
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assigned_to_id is not None:
        query = query.filter(Task.assigned_to_id == assigned_to_id)
    if created_by_id is not None:
        query = query.filter(Task.created_by_id == created_by_id)

    total = query.count()
    tasks = (
        query.order_by(Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, tasks
