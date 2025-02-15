import psycopg2
from config import DB_CONFIG

def connect_db():
    """Kết nối PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("❌ Lỗi kết nối Database:", e)
        return None
