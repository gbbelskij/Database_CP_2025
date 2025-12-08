from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import UserCreate, UserRead
from app.deps import get_current_admin, get_current_user
from app.sql import queries

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/init-admin", response_model=UserRead, summary="Инициализация первого админа")
def init_admin(user_in: UserCreate):
    user = queries.create_user(
        email=user_in.email,
        password=user_in.password,
        role="admin",
        home_id=user_in.home_id,
    )
    return user


@router.post("/", response_model=UserRead, summary="Создать пользователя (admin)")
def create_user(user_in: UserCreate, admin: dict = Depends(get_current_admin)):
    existing = queries.get_user_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = queries.create_user(
        email=user_in.email,
        password=user_in.password,
        role=user_in.role,
        home_id=user_in.home_id,
    )
    return user


@router.get("/me", response_model=UserRead, summary="Информация о текущем пользователе")
def read_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserRead], summary="Список пользователей (admin)")
def list_users(admin: dict = Depends(get_current_admin)):
    return queries.get_all_users()
