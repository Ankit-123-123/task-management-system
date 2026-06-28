from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.crud import task as task_crud
from app.crud import user as user_crud
from app.database import get_db
from app.models.task import TaskPriority, TaskStatus
from app.models.user import User, UserRole
from app.schemas.task import PaginatedTasks, TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # members can only assign tasks to themselves
    if payload.assigned_to_id and payload.assigned_to_id != current_user.id:
        if current_user.role == UserRole.member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members can only assign tasks to themselves",
            )

    if payload.assigned_to_id and not user_crud.get_user_by_id(db, payload.assigned_to_id):
        raise HTTPException(status_code=404, detail="Assigned user not found")

    return task_crud.create_task(db, payload, created_by_id=current_user.id)


@router.get("/", response_model=PaginatedTasks)
def list_tasks(
    search: Optional[str] = Query(None, description="Search in title or description"),
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    created_by_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # members only see tasks they created or are assigned to
    if current_user.role == UserRole.member:
        total, tasks = task_crud.list_tasks_for_member(
            db,
            user_id=current_user.id,
            search=search,
            status=status,
            priority=priority,
            page=page,
            page_size=page_size,
        )
    else:
        total, tasks = task_crud.list_tasks(
            db,
            search=search,
            status=status,
            priority=priority,
            assigned_to_id=assigned_to_id,
            created_by_id=created_by_id,
            page=page,
            page_size=page_size,
        )

    return PaginatedTasks(total=total, page=page, page_size=page_size, results=tasks)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = task_crud.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # members can only view tasks they own or are assigned to
    if current_user.role == UserRole.member:
        if task.created_by_id != current_user.id and task.assigned_to_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = task_crud.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # members can only update their own tasks
    if current_user.role == UserRole.member and task.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Members can only edit their own tasks")

    # members cannot reassign tasks to others
    if payload.assigned_to_id and payload.assigned_to_id != current_user.id:
        if current_user.role == UserRole.member:
            raise HTTPException(
                status_code=403,
                detail="Members can only assign tasks to themselves",
            )

    if payload.assigned_to_id and not user_crud.get_user_by_id(db, payload.assigned_to_id):
        raise HTTPException(status_code=404, detail="Assigned user not found")

    return task_crud.update_task(db, task, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = task_crud.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # only admin or the task creator can delete
    is_admin = current_user.role == UserRole.admin
    is_creator = task.created_by_id == current_user.id
    if not is_admin and not is_creator:
        raise HTTPException(
            status_code=403,
            detail="Only admins or the task creator can delete this task",
        )

    task_crud.delete_task(db, task)
