from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserRoleUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])

# every route here requires admin role
AdminOnly = Depends(require_roles(UserRole.admin))


@router.get("/users", response_model=List[UserResponse], dependencies=[AdminOnly])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    return db.query(User).order_by(User.created_at.desc()).offset(offset).limit(page_size).all()


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Admins cannot change their own role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Admins cannot deactivate themselves")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()
    db.refresh(user)
    return user
