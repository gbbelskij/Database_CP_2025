from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ==================== AUTH ====================


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==================== USERS ====================


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"
    home_id: Optional[int] = None


class UserRead(BaseModel):
    id: int
    email: str
    role: str
    home_id: Optional[int]


# ==================== HOMES ====================


class HomeCreate(BaseModel):
    name: str
    address: Optional[str] = None


class HomeRead(BaseModel):
    id: int
    name: str
    address: Optional[str]


# ==================== ROOMS ====================


class RoomCreate(BaseModel):
    home_id: int
    name: str


class RoomRead(BaseModel):
    id: int
    home_id: int
    name: str


# ==================== DEVICES ====================


class DeviceCreate(BaseModel):
    home_id: int
    type: str  # 'light' | 'thermostat' | 'camera'
    name: str
    status: str


class DeviceRead(BaseModel):
    id: int
    home_id: int
    type: str
    name: str
    status: str


class DeviceUpdateStatus(BaseModel):
    status: str


# ==================== SENSORS ====================


class SensorCreate(BaseModel):
    device_id: int
    type: str  # 'motion' | 'temp' | 'door'
    value: Optional[str] = None


class SensorRead(BaseModel):
    id: int
    device_id: int
    type: str
    value: Optional[str]


class SensorUpdateValue(BaseModel):
    value: str


# ==================== EVENTS ====================


class EventCreate(BaseModel):
    device_id: int
    event_type: str
    value: Optional[str] = None


class EventRead(BaseModel):
    id: int
    device_id: int
    timestamp: datetime
    event_type: str
    value: Optional[str]


# ==================== RULES ====================


class RuleCreate(BaseModel):
    home_id: int
    condition: str
    action: str


class RuleRead(BaseModel):
    id: int
    home_id: int
    condition: str
    action: str


# ==================== LOGS ====================


class LogCreate(BaseModel):
    user_id: int
    action: str


class LogRead(BaseModel):
    id: int
    user_id: int
    action: str
    timestamp: datetime
