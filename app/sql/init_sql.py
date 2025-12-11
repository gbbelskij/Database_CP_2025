INIT_SQL = """
CREATE TABLE IF NOT EXISTS homes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(16) NOT NULL CHECK (role IN ('admin', 'user')),
    home_id INTEGER REFERENCES homes(id)
);

CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    home_id INTEGER NOT NULL REFERENCES homes(id),
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    home_id INTEGER NOT NULL REFERENCES homes(id),
    type VARCHAR(32) NOT NULL CHECK (type IN ('light', 'thermostat', 'camera')),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS sensors (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id),
    type VARCHAR(32) NOT NULL CHECK (type IN ('motion', 'temp', 'door')),
    value VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(64) NOT NULL,
    value VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    home_id INTEGER NOT NULL REFERENCES homes(id),
    condition TEXT NOT NULL,
    action TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS home_events_summary (
    home_id INT PRIMARY KEY REFERENCES homes(id),
    events_total INT NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_users_home_id ON users(home_id);

-- Дома
CREATE INDEX IF NOT EXISTS idx_homes_user_id ON homes(id);

-- Комнаты
CREATE INDEX IF NOT EXISTS idx_rooms_home_id ON rooms(home_id);

-- Устройства
CREATE INDEX IF NOT EXISTS idx_devices_home_id ON devices(home_id);
CREATE INDEX IF NOT EXISTS idx_devices_type    ON devices(type);

-- Датчики
CREATE INDEX IF NOT EXISTS idx_sensors_device_id ON sensors(device_id);
CREATE INDEX IF NOT EXISTS idx_sensors_type      ON sensors(type);

-- События
CREATE INDEX IF NOT EXISTS idx_events_device_id  ON events(device_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp  ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_device_time
    ON events(device_id, timestamp);

-- Правила
CREATE INDEX IF NOT EXISTS idx_rules_home_id ON rules(home_id);

-- Логи
CREATE INDEX IF NOT EXISTS idx_logs_user_id     ON logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp   ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_user_time
    ON logs(user_id, timestamp);

-- 1. Скалярная функция: количество событий по устройству за период
CREATE OR REPLACE FUNCTION get_events_count_for_device(
    p_device_id INT,
    p_from TIMESTAMP,
    p_to   TIMESTAMP
)
RETURNS INT AS $$
    SELECT COUNT(*)
    FROM events
    WHERE device_id = p_device_id
    AND timestamp BETWEEN p_from AND p_to;
$$ LANGUAGE sql STABLE;


-- 2. Табличная функция: сводка по событиям устройства
CREATE OR REPLACE FUNCTION get_device_events_stats(
    p_device_id INT
)
RETURNS TABLE (
    event_type TEXT,
    events_count INT
) AS $$
    SELECT event_type, COUNT(*)::INT AS events_count
    FROM events
    WHERE device_id = p_device_id
    GROUP BY event_type
    ORDER BY events_count DESC;
$$ LANGUAGE sql STABLE;

-- 1. Сводка устройств по домам
CREATE OR REPLACE VIEW view_home_devices_summary AS
SELECT
    h.id   AS home_id,
    h.name AS home_name,
    COUNT(d.id)              AS devices_total,
    SUM(CASE WHEN d.type = 'light'       THEN 1 ELSE 0 END) AS lights_count,
    SUM(CASE WHEN d.type = 'thermostat' THEN 1 ELSE 0 END) AS thermostats_count,
    SUM(CASE WHEN d.type = 'camera'     THEN 1 ELSE 0 END) AS cameras_count
FROM homes h
LEFT JOIN devices d ON d.home_id = h.id
GROUP BY h.id, h.name;

-- 2. Активность пользователей (кол-во действий)
CREATE OR REPLACE VIEW view_user_activity AS
SELECT
    u.id    AS user_id,
    u.email AS user_email,
    COUNT(l.id) AS actions_count,
    MIN(l.timestamp) AS first_action_at,
    MAX(l.timestamp) AS last_action_at
FROM users u
LEFT JOIN logs l ON l.user_id = u.id
GROUP BY u.id, u.email;

-- 3. Последние события по устройствам
CREATE OR REPLACE VIEW view_last_device_events AS
SELECT DISTINCT ON (e.device_id)
    e.device_id,
    d.name      AS device_name,
    d.type      AS device_type,
    e.timestamp,
    e.event_type,
    e.value
FROM events e
JOIN devices d ON d.id = e.device_id
ORDER BY e.device_id, e.timestamp DESC;

CREATE OR REPLACE FUNCTION trg_update_home_events_summary()
RETURNS TRIGGER AS $$
DECLARE
    v_home_id INT;
BEGIN
    -- находим дом, к которому относится устройство
    SELECT home_id INTO v_home_id FROM devices WHERE id = NEW.device_id;

    IF v_home_id IS NULL THEN
        RETURN NEW;
    END IF;

    INSERT INTO home_events_summary (home_id, events_total)
    VALUES (v_home_id, 1)
    ON CONFLICT (home_id) DO UPDATE
        SET events_total = home_events_summary.events_total + 1;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- триггер срабатывает при вставке новой записи в events
DROP TRIGGER IF EXISTS trg_events_insert_summary ON events;

CREATE TRIGGER trg_events_insert_summary
AFTER INSERT ON events
FOR EACH ROW
EXECUTE FUNCTION trg_update_home_events_summary();

"""
