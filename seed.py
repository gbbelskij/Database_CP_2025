import psycopg2
from psycopg2.extras import execute_values
import random
from datetime import datetime, timedelta
from app.config import settings
from app.security import hash_password

# Подключение к БД
conn = psycopg2.connect(
    dbname=settings.DATABASE_NAME,
    user=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
)
cur = conn.cursor()

print("🌱 Начинаю заполнение БД тестовыми данными...")

# ==================== HOMES ====================
print("📍 Создаю дома...")
homes_data = [
    ("Дом 1 на Ленина", "ул. Ленина, 10"),
    ("Дом 2 на Красной", "ул. Красная, 25"),
    ("Квартира 3", "ул. Пушкина, 5"),
    ("Офис компании", "ул. Советская, 100"),
    ("Загородный дом", "деревня Заречье, 15"),
]
cur.execute("DELETE FROM homes")  # Очистка
execute_values(cur, "INSERT INTO homes (name, address) VALUES %s", homes_data)
conn.commit()
cur.execute("SELECT id FROM homes ORDER BY id")
home_rows = cur.fetchall()
home_ids = [row[0] for row in home_rows]
print(f"✅ Создано {len(home_ids)} домов")

# ==================== USERS ====================
print("👥 Создаю пользователей...")
cur.execute("DELETE FROM users")
users_data = [
    ("admin@example.com", hash_password("admin123"), "admin", home_ids[0]),
    ("user1@example.com", hash_password("pass1"), "user", home_ids[0]),
    ("user2@example.com", hash_password("pass2"), "user", home_ids[1]),
    ("user3@example.com", hash_password("pass3"), "user", home_ids[2]),
    ("user4@example.com", hash_password("pass4"), "user", home_ids[3]),
    ("user5@example.com", hash_password("pass5"), "user", home_ids[4]),
]
execute_values(cur, 
    "INSERT INTO users (email, password_hash, role, home_id) VALUES %s", 
    users_data)
conn.commit()
cur.execute("SELECT id FROM users ORDER BY id")
user_ids = [row[0] for row in cur.fetchall()]
print(f"✅ Создано {len(user_ids)} пользователей")

# ==================== ROOMS ====================
print("🏠 Создаю комнаты...")
cur.execute("DELETE FROM rooms")
rooms_data = []
room_names = ["Гостиная", "Спальня", "Кухня", "Ванная", "Кабинет", "Коридор"]
for home_id in home_ids:
    for room_name in room_names:
        rooms_data.append((home_id, room_name))
execute_values(cur, "INSERT INTO rooms (home_id, name) VALUES %s", rooms_data)
conn.commit()
print(f"✅ Создано {len(rooms_data)} комнат")

# ==================== DEVICES ====================
print("🔌 Создаю устройства...")
cur.execute("DELETE FROM devices")
devices_data = []
device_types = ["light", "thermostat", "camera"]
device_names = {
    "light": ["Основной свет", "Настольная лампа", "Подсветка", "Люстра"],
    "thermostat": ["Термостат 1", "Термостат 2"],
    "camera": ["Камера входа", "Камера гостиной", "Камера улицы"],
}
for home_id in home_ids:
    for dev_type in device_types:
        for name in device_names[dev_type]:
            devices_data.append((home_id, dev_type, name, random.choice(["on", "off", "22°C", "idle"])))
execute_values(cur, 
    "INSERT INTO devices (home_id, type, name, status) VALUES %s", 
    devices_data)
conn.commit()
cur.execute("SELECT id FROM devices ORDER BY id")
device_ids = [row[0] for row in cur.fetchall()]
print(f"✅ Создано {len(device_ids)} устройств")

# ==================== SENSORS ====================
print("📊 Создаю датчики...")
cur.execute("DELETE FROM sensors")
sensors_data = []
sensor_types = ["motion", "temp", "door"]
for device_id in device_ids[:len(device_ids)//2]:  # На половине устройств
    for sensor_type in sensor_types:
        value = None
        if sensor_type == "temp":
            value = f"{random.randint(15, 30)}°C"
        elif sensor_type == "motion":
            value = random.choice(["detected", "clear"])
        elif sensor_type == "door":
            value = random.choice(["open", "closed"])
        sensors_data.append((device_id, sensor_type, value))
execute_values(cur, "INSERT INTO sensors (device_id, type, value) VALUES %s", sensors_data)
conn.commit()
print(f"✅ Создано {len(sensors_data)} датчиков")

# ==================== EVENTS ====================
print("📝 Создаю события (1000 записей)...")
cur.execute("DELETE FROM events")
cur.execute("DELETE FROM home_events_summary")
events_data = []
event_types = ["on", "off", "temperature_change", "motion_detected", "door_open", "door_close"]
now = datetime.utcnow()

for i in range(1000):
    device_id = random.choice(device_ids)
    timestamp = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    event_type = random.choice(event_types)
    value = None
    if event_type == "temperature_change":
        value = f"{random.randint(15, 30)}°C"
    events_data.append((device_id, timestamp, event_type, value))

execute_values(cur, 
    "INSERT INTO events (device_id, timestamp, event_type, value) VALUES %s", 
    events_data)
conn.commit()
print(f"✅ Создано {len(events_data)} событий")

# ==================== RULES ====================
print("⚙️  Создаю правила автоматизации...")
cur.execute("DELETE FROM rules")
rules_data = []
conditions = [
    "temperature > 25",
    "motion_detected == true",
    "time == 22:00",
    "door_open == true",
    "humidity > 60",
]
actions = [
    "turn_off light",
    "set_temperature 22",
    "send_notification",
    "activate_alarm",
    "log_event",
]
for home_id in home_ids:
    for _ in range(10):
        rules_data.append((
            home_id,
            random.choice(conditions),
            random.choice(actions),
        ))
execute_values(cur, 
    "INSERT INTO rules (home_id, condition, action) VALUES %s", 
    rules_data)
conn.commit()
print(f"✅ Создано {len(rules_data)} правил")

# ==================== LOGS ====================
print("📋 Создаю логи аудита...")
cur.execute("DELETE FROM logs")
logs_data = []
actions = [
    "Created device",
    "Updated device status",
    "Created rule",
    "Deleted rule",
    "Viewed analytics",
    "Logged in",
    "Changed settings",
]
now = datetime.utcnow()

for i in range(500):
    user_id = random.choice(user_ids)
    timestamp = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    action = random.choice(actions)
    logs_data.append((user_id, action, timestamp))

execute_values(cur, 
    "INSERT INTO logs (user_id, action, timestamp) VALUES %s", 
    logs_data)
conn.commit()
print(f"✅ Создано {len(logs_data)} логов")

# ==================== ИТОГ ====================
cur.close()
conn.close()

print("\n" + "="*50)
print("✨ Заполнение завершено!")
print("="*50)
print(f"✅ Домов: {len(home_ids)}")
print(f"✅ Пользователей: {len(user_ids)}")
print(f"✅ Комнат: {len(rooms_data)}")
print(f"✅ Устройств: {len(device_ids)}")
print(f"✅ Датчиков: {len(sensors_data)}")
print(f"✅ Событий: {len(events_data)}")
print(f"✅ Правил: {len(rules_data)}")
print(f"✅ Логов: {len(logs_data)}")
print("="*50)
