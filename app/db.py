import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import settings
from typing import Optional, List, Dict, Any


class Database:
    def __init__(self):
        self.conn_params = {
            "dbname": settings.DATABASE_NAME,
            "user": settings.DATABASE_USER,
            "password": settings.DATABASE_PASSWORD,
            "host": settings.DATABASE_HOST,
            "port": settings.DATABASE_PORT,
        }

    def get_connection(self):
        """Открыть подключение к БД"""
        return psycopg2.connect(**self.conn_params)

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Выполнить SELECT-запрос, вернуть список словарей"""
        conn = self.get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, params or ())
            result = cur.fetchall()
            cur.close()
            return result
        finally:
            conn.close()

    def execute_single(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Выполнить SELECT-запрос, вернуть одну строку"""
        conn = self.get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, params or ())
            result = cur.fetchone()
            cur.close()
            return result
        finally:
            conn.close()

    def execute_insert(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Выполнить INSERT-запрос (с RETURNING), вернуть вставленную строку"""
        conn = self.get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, params or ())
            result = cur.fetchone()
            conn.commit()
            cur.close()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Выполнить UPDATE/DELETE-запрос, вернуть количество измененных строк"""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            affected = cur.rowcount
            conn.commit()
            cur.close()
            return affected
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_schema(self):
        """Инициализировать схему БД из init.sql"""
        from app.sql import init_sql
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(init_sql.INIT_SQL)
            conn.commit()
            cur.close()
            print("✓ Schema initialized successfully")
        except psycopg2.errors.DuplicateTable:
            conn.rollback()
            print("✓ Schema already exists")
        except Exception as e:
            conn.rollback()
            print(f"✗ Error initializing schema: {e}")
            raise
        finally:
            conn.close()


db = Database()


def get_db() -> Database:
    """Зависимость FastAPI для получения подключения"""
    return db
