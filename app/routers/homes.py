from typing import List
from fastapi import APIRouter, Depends
from app.schemas import HomeCreate, HomeRead
from app.deps import get_current_admin
from app.sql import queries

router = APIRouter(prefix="/homes", tags=["homes"])


@router.post("/", response_model=HomeRead, summary="Создать дом (admin)")
def create_home(home_in: HomeCreate, admin: dict = Depends(get_current_admin)):
    home = queries.create_home(name=home_in.name, address=home_in.address)
    return home


@router.get("/", response_model=List[HomeRead], summary="Список домов (admin)")
def list_homes(admin: dict = Depends(get_current_admin)):
    return queries.get_all_homes()


@router.get("/{home_id}", response_model=HomeRead, summary="Получить дом (admin)")
def get_home(home_id: int, admin: dict = Depends(get_current_admin)):
    home = queries.get_home_by_id(home_id)
    if not home:
        return {"detail": "Home not found"}
    return home
