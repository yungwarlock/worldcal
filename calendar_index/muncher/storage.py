import os
from typing import List

import psycopg2

from event import Event


DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "")
DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


class Storage:
    table = "calendar_index"
    spider_table = "spider_index"

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

    def get_urls_from_range(self, start: int, end: int):
        cursor = self.connection.cursor()

        query = """
        SELECT url FROM spider_index
        LIMIT 300
        """
        cursor.execute(query, (start, end))
        return [x[0] for x in cursor.fetchall()]

    def add_event(self, event: Event):
        cursor = self.connection.cursor()

        query = """
INSERT INTO calendar_index (title, summary, context, day, month, year)
VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            query,
            (
                event.title,
                event.summary,
                str(event.context),
                event.day,
                event.month,
                event.year,
            ),
        )
        self.connection.commit()

    def add_bulk_event(self, events: List[Event]):
        cursor = self.connection.cursor()

        query = f"""
INSERT INTO {self.table}
(title, summary, context, day, month, year)
VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(
            query,
            [
                (
                    event.title,
                    event.summary,
                    str(event.context),
                    event.day,
                    event.month,
                    event.year,
                )
                for event in events
            ],
        )
        self.connection.commit()

    def remove_event(self, event_id: str):
        cursor = self.connection.cursor()

        query = f"""DELETE FROM {self.table} WHERE id = ?"""
        cursor.execute(query, (event_id,))
        self.connection.commit()
