from typing import List
from fastapi import APIRouter, Depends
from app.schemas import DeviceCreate, DeviceRead, DeviceUpdateStatus
from app.deps import get_current_user
from app.sql import queries

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=DeviceRead, summary="Создать устройство")
def create_device(device_in: DeviceCreate, user: dict = Depends(get_current_user)):
    device = queries.create_device(
        home_id=device_in.home_id,
        type_=device_in.type,
        name=device_in.name,
        status=device_in.status,
    )
    queries.create_log(user["id"], f"Created device: {device_in.name}")
    return device


@router.get("/home/{home_id}", response_model=List[DeviceRead], summary="Устройства дома")
def list_devices(home_id: int, user: dict = Depends(get_current_user)):
    return queries.get_devices_by_home(home_id)


@router.get("/{device_id}", response_model=DeviceRead, summary="Получить устройство")
def get_device(device_id: int, user: dict = Depends(get_current_user)):
    device = queries.get_device_by_id(device_id)
    if not device:
        return {"detail": "Device not found"}
    return device


@router.patch("/{device_id}/status", response_model=DeviceRead, summary="Изменить статус")
def update_status(device_id: int, update: DeviceUpdateStatus, user: dict = Depends(get_current_user)):
    queries.update_device_status(device_id, update.status)
    device = queries.get_device_by_id(device_id)
    queries.create_log(user["id"], f"Updated device {device_id} status to {update.status}")
    return device
