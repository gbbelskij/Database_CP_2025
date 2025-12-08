from typing import List
from fastapi import APIRouter, Depends
from app.schemas import RoomCreate, RoomRead
from app.deps import get_current_user
from app.sql import queries

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", response_model=RoomRead, summary="Создать комнату")
def create_room(room_in: RoomCreate, user: dict = Depends(get_current_user)):
    room = queries.create_room(home_id=room_in.home_id, name=room_in.name)
    queries.create_log(user["id"], f"Created room: {room_in.name}")
    return room


@router.get("/home/{home_id}", response_model=List[RoomRead], summary="Комнаты дома")
def list_rooms(home_id: int, user: dict = Depends(get_current_user)):
    return queries.get_rooms_by_home(home_id)
