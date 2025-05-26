# models/database.py

import psycopg2
from config import DB_CONFIG

def get_connection():
    """
    Trả về một connection tới PostgreSQL theo cấu hình DB_CONFIG.
    """
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
