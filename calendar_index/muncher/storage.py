import os

import psycopg2
from prefect import task

from event import Event


DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "")
DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


class Storage:
    table = "calendar_index"

    def __init__(self, username: str, password: str, host: str, db_name: str):
        self.connection = psycopg2.connect(
            host=host,
            user=username,
            dbname=db_name,
            password=password,
        )

    @staticmethod
    def from_environment_variables():
        return Storage(
            host=DB_HOST,
            db_name=DB_NAME,
            username=DB_USER,
            password=DB_PASSWORD,
        )

    @task
    def add_event(self, event: Event):
        cursor = self.connection.cursor()

        query = f"""
INSERT INTO {self.table}
(title, summary, day, month, year)
VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            event.title,
            event.summary,
            event.day,
            event.month,
            event.year,
        ))
        self.connection.commit()

    @task
    def remove_event(self, event_id: str):
        cursor = self.connection.cursor()

        query = f"""DELETE FROM {self.table} WHERE id = ?"""
        cursor.execute(query, (event_id,))
        self.connection.commit()
