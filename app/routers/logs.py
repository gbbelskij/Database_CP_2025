from typing import List
from fastapi import APIRouter, Depends
from app.schemas import LogRead
from app.deps import get_current_admin
from app.sql import queries

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/", response_model=List[LogRead], summary="Все логи (admin)")
def list_logs(admin: dict = Depends(get_current_admin)):
    return queries.get_logs()


@router.get("/user/{user_id}", response_model=List[LogRead], summary="Логи пользователя")
def list_user_logs(user_id: int, admin: dict = Depends(get_current_admin)):
    return queries.get_logs_by_user(user_id)
