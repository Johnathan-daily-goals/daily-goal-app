# backend/db.py
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()


class Database:
    def __init__(self):
        self.connection = None
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", 5432)
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

    def connect(self):
        if not self.connection:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor,
            )
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
