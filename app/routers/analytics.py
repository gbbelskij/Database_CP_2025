from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.sql import queries
from app.deps import get_current_user
# from app import models

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/devices/home-summary", summary="Сводка устройств по домам")
def get_devices_home_summary(user: dict = Depends(get_current_user)):
    """
    Представление: агрегированная сводка количества устройств по домам.
    Показывает общее количество и разбор по типам (свет, термостат, камеры).
    """
    try:
        result = queries.get_home_devices_summary()
        return {"status": "ok", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/activity", summary="Активность пользователей")
def get_users_activity(user: dict = Depends(get_current_user)):
    """
    Представление: агрегированная активность пользователей.
    Показывает количество действий каждого пользователя и временные границы активности.
    """
    try:
        result = queries.get_user_activity_summary()
        return {"status": "ok", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/last-events", summary="Последние события по устройствам")
def get_devices_last_events(user: dict = Depends(get_current_user)):
    """
    Представление: последние события по каждому устройству.
    Показывает самое свежее событие для каждого девайса с типом события и значением.
    """
    try:
        result = queries.get_last_device_events()
        return {"status": "ok", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}/events-count", summary="Количество событий за период")
def get_device_events_count(
    device_id: int,
    days: int = 7,
    user: dict = Depends(get_current_user),
):
    """
    Скалярная функция: количество событий устройства за последние N дней.
    
    Query параметры:
    - days: количество дней для анализа (по умолчанию 7)
    """
    try:
        to_dt = datetime.utcnow()
        from_dt = to_dt - timedelta(days=days)
        count = queries.get_events_count_for_device_period(device_id, from_dt, to_dt)
        return {
            "status": "ok",
            "device_id": device_id,
            "period_days": days,
            "events_count": count,
            "from": from_dt.isoformat(),
            "to": to_dt.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}/events-stats", summary="Статистика событий устройства")
def get_device_events_stats(
    device_id: int,
    user: dict = Depends(get_current_user),
):
    """
    Табличная функция: сводка по типам событий устройства.
    Показывает количество событий для каждого типа события.
    """
    try:
        result = queries.get_device_events_stats_fn(device_id)
        return {
            "status": "ok",
            "device_id": device_id,
            "stats": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/homes/{home_id}/events-summary", summary="Агрегированная сводка событий дома (триггер)")
def get_home_events_summary(home_id: int, user: dict = Depends(get_current_user)):
    """
    Таблица home_events_summary автоматически обновляется триггером
    trg_events_insert_summary при вставке новых событий.
    
    Эта ручка показывает, сколько всего событий произошло в доме
    (данные обновляются триггером в реальном времени).
    """
    try:
        query = "SELECT * FROM home_events_summary WHERE home_id = %s"
        result = queries.db.execute_single(query, (home_id,))
        
        if not result:
            return {
                "status": "ok",
                "home_id": home_id,
                "events_total": 0,
                "note": "Нет событий. События создаются триггером при INSERT в events."
            }
        
        return {
            "status": "ok",
            "home_id": home_id,
            "events_total": result["events_total"],
            "note": "Это значение обновляется автоматически триггером trg_events_insert_summary"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
