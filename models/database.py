
import os
import psycopg2
import urllib.parse as urlparse

def get_connection():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise Exception("DATABASE_URL không được thiết lập trong biến môi trường.")

    url = urlparse.urlparse(db_url)

    return psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )


