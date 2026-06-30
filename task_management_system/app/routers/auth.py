from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud import user as user_crud
from app.database import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_crud.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    return user_crud.create_user(db, payload)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Accepts username or email in the `username` field."""
    user = user_crud.get_user_by_username(db, form_data.username)
    if not user:
        user = user_crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled")

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
