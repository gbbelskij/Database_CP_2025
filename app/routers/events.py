from typing import List
from fastapi import APIRouter, Depends
from app.schemas import EventCreate, EventRead
from app.deps import get_current_user
from app.sql import queries

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventRead, summary="Создать событие")
def create_event(event_in: EventCreate, user: dict = Depends(get_current_user)):
    event = queries.create_event(
        device_id=event_in.device_id,
        event_type=event_in.event_type,
        value=event_in.value,
    )
    queries.create_log(user["id"], f"Event triggered: {event_in.event_type}")
    return event


@router.get("/device/{device_id}", response_model=List[EventRead], summary="События устройства")
def list_events(device_id: int, user: dict = Depends(get_current_user)):
    return queries.get_events_by_device(device_id)
