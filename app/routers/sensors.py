from typing import List
from fastapi import APIRouter, Depends
from app.schemas import SensorCreate, SensorRead, SensorUpdateValue
from app.deps import get_current_user
from app.sql import queries

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.post("/", response_model=SensorRead, summary="Создать датчик")
def create_sensor(sensor_in: SensorCreate, user: dict = Depends(get_current_user)):
    sensor = queries.create_sensor(
        device_id=sensor_in.device_id,
        type_=sensor_in.type,
        value=sensor_in.value,
    )
    queries.create_log(user["id"], f"Created sensor: {sensor_in.type}")
    return sensor


@router.get("/device/{device_id}", response_model=List[SensorRead], summary="Датчики устройства")
def list_sensors(device_id: int, user: dict = Depends(get_current_user)):
    return queries.get_sensors_by_device(device_id)


@router.patch("/{sensor_id}/value", response_model=SensorRead, summary="Обновить значение датчика")
def update_value(sensor_id: int, update: SensorUpdateValue, user: dict = Depends(get_current_user)):
    queries.update_sensor_value(sensor_id, update.value)
    sensor = queries.get_sensor_by_id(sensor_id)
    queries.create_log(user["id"], f"Updated sensor {sensor_id} value to {update.value}")
    return sensor
