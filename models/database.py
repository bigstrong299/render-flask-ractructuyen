# models/database.py
# import os
# import psycopg2

# def get_connection():
#     return psycopg2.connect(
#         host=os.getenv("DB_HOST"),
#         database=os.getenv("DB_NAME"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         port=os.getenv("DB_PORT", 5432)
#     )
import os
import psycopg2
import urllib.parse as urlparse

def get_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url is None:
        raise Exception("DATABASE_URL is not set")

    # Parse URL từ DATABASE_URL
    url = urlparse.urlparse(db_url)
    return psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

