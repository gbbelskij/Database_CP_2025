from typing import Optional, List, Dict, Any
from app.db import db
from app.security import hash_password
from datetime import datetime


# ==================== USERS ====================


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Получить пользователя по email"""
    query = "SELECT * FROM users WHERE email = %s"
    return db.execute_single(query, (email,))


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить пользователя по ID"""
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute_single(query, (user_id,))


def create_user(email: str, password: str, role: str = "user", home_id: Optional[int] = None) -> Dict[str, Any]:
    """Создать пользователя"""
    password_hash = hash_password(password)
    query = """
        INSERT INTO users (email, password_hash, role, home_id)
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """
    return db.execute_insert(query, (email, password_hash, role, home_id))


def get_all_users() -> List[Dict[str, Any]]:
    """Получить всех пользователей"""
    query = "SELECT id, email, role, home_id FROM users"
    return db.execute_query(query)


# ==================== HOMES ====================


def create_home(name: str, address: Optional[str] = None) -> Dict[str, Any]:
    """Создать дом"""
    query = """
        INSERT INTO homes (name, address)
        VALUES (%s, %s)
        RETURNING *
    """
    return db.execute_insert(query, (name, address))


def get_home_by_id(home_id: int) -> Optional[Dict[str, Any]]:
    """Получить дом по ID"""
    query = "SELECT * FROM homes WHERE id = %s"
    return db.execute_single(query, (home_id,))


def get_all_homes() -> List[Dict[str, Any]]:
    """Получить все дома"""
    query = "SELECT * FROM homes"
    return db.execute_query(query)


# ==================== ROOMS ====================


def create_room(home_id: int, name: str) -> Dict[str, Any]:
    """Создать комнату"""
    query = """
        INSERT INTO rooms (home_id, name)
        VALUES (%s, %s)
        RETURNING *
    """
    return db.execute_insert(query, (home_id, name))


def get_rooms_by_home(home_id: int) -> List[Dict[str, Any]]:
    """Получить все комнаты дома"""
    query = "SELECT * FROM rooms WHERE home_id = %s"
    return db.execute_query(query, (home_id,))


def get_room_by_id(room_id: int) -> Optional[Dict[str, Any]]:
    """Получить комнату по ID"""
    query = "SELECT * FROM rooms WHERE id = %s"
    return db.execute_single(query, (room_id,))


# ==================== DEVICES ====================


def create_device(home_id: int, type_: str, name: str, status: str) -> Dict[str, Any]:
    """Создать устройство"""
    query = """
        INSERT INTO devices (home_id, type, name, status)
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """
    return db.execute_insert(query, (home_id, type_, name, status))


def get_device_by_id(device_id: int) -> Optional[Dict[str, Any]]:
    """Получить устройство по ID"""
    query = "SELECT * FROM devices WHERE id = %s"
    return db.execute_single(query, (device_id,))


def get_devices_by_home(home_id: int) -> List[Dict[str, Any]]:
    """Получить все устройства дома"""
    query = "SELECT * FROM devices WHERE home_id = %s"
    return db.execute_query(query, (home_id,))


def update_device_status(device_id: int, status: str) -> int:
    """Обновить статус устройства"""
    query = "UPDATE devices SET status = %s WHERE id = %s"
    return db.execute_update(query, (status, device_id))


# ==================== SENSORS ====================


def create_sensor(device_id: int, type_: str, value: Optional[str] = None) -> Dict[str, Any]:
    """Создать датчик"""
    query = """
        INSERT INTO sensors (device_id, type, value)
        VALUES (%s, %s, %s)
        RETURNING *
    """
    return db.execute_insert(query, (device_id, type_, value))


def get_sensor_by_id(sensor_id: int) -> Optional[Dict[str, Any]]:
    """Получить датчик по ID"""
    query = "SELECT * FROM sensors WHERE id = %s"
    return db.execute_single(query, (sensor_id,))


def get_sensors_by_device(device_id: int) -> List[Dict[str, Any]]:
    """Получить все датчики устройства"""
    query = "SELECT * FROM sensors WHERE device_id = %s"
    return db.execute_query(query, (device_id,))


def update_sensor_value(sensor_id: int, value: str) -> int:
    """Обновить значение датчика"""
    query = "UPDATE sensors SET value = %s WHERE id = %s"
    return db.execute_update(query, (value, sensor_id))


# ==================== EVENTS ====================


def create_event(device_id: int, event_type: str, value: Optional[str] = None) -> Dict[str, Any]:
    """Создать событие"""
    query = """
        INSERT INTO events (device_id, event_type, value, timestamp)
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """
    return db.execute_insert(query, (device_id, event_type, value, datetime.utcnow()))


def get_event_by_id(event_id: int) -> Optional[Dict[str, Any]]:
    """Получить событие по ID"""
    query = "SELECT * FROM events WHERE id = %s"
    return db.execute_single(query, (event_id,))


def get_events_by_device(device_id: int) -> List[Dict[str, Any]]:
    """Получить события устройства"""
    query = "SELECT * FROM events WHERE device_id = %s ORDER BY timestamp DESC"
    return db.execute_query(query, (device_id,))


# ==================== RULES ====================


def create_rule(home_id: int, condition: str, action: str) -> Dict[str, Any]:
    """Создать правило автоматики"""
    query = """
        INSERT INTO rules (home_id, condition, action)
        VALUES (%s, %s, %s)
        RETURNING *
    """
    return db.execute_insert(query, (home_id, condition, action))


def get_rule_by_id(rule_id: int) -> Optional[Dict[str, Any]]:
    """Получить правило по ID"""
    query = "SELECT * FROM rules WHERE id = %s"
    return db.execute_single(query, (rule_id,))


def get_rules_by_home(home_id: int) -> List[Dict[str, Any]]:
    """Получить правила дома"""
    query = "SELECT * FROM rules WHERE home_id = %s"
    return db.execute_query(query, (home_id,))


def delete_rule(rule_id: int) -> int:
    """Удалить правило"""
    query = "DELETE FROM rules WHERE id = %s"
    return db.execute_update(query, (rule_id,))


# ==================== LOGS ====================


def create_log(user_id: int, action: str) -> Dict[str, Any]:
    """Создать запись аудита"""
    query = """
        INSERT INTO logs (user_id, action, timestamp)
        VALUES (%s, %s, %s)
        RETURNING *
    """
    return db.execute_insert(query, (user_id, action, datetime.utcnow()))


def get_logs() -> List[Dict[str, Any]]:
    """Получить все логи"""
    query = "SELECT * FROM logs ORDER BY timestamp DESC"
    return db.execute_query(query)


def get_logs_by_user(user_id: int) -> List[Dict[str, Any]]:
    """Получить логи пользователя"""
    query = "SELECT * FROM logs WHERE user_id = %s ORDER BY timestamp DESC"
    return db.execute_query(query, (user_id,))
