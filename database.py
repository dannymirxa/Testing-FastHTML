from sqlalchemy.orm import declarative_base

Base = declarative_base()

import psycopg2

DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/MediaApp"

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="MediaApp",
        user="myuser",
        password="mypassword"
    )
    return conn