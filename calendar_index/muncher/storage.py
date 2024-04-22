import os
from typing import List, TypedDict

import psycopg2

from event import Event


DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "")
DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


class URLItem(TypedDict):
    id: int
    url: str


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

    def get_unscheduled_urls(self, limit=20) -> List[URLItem]:
        cursor = self.connection.cursor()

        query = f"""
SELECT id, url FROM {self.spider_table}
WHERE status = 'not_scheduled'
AND category != ALL(ARRAY['None', 'unknown'])
ORDER by id
LIMIT %s
        """
        cursor.execute(query, (limit,))
        return [
            {
                "id": x[0],
                "url": x[1],
            }
            for x in cursor.fetchall()
        ]

    def set_url_scheduled(self, url_id: int):
        cursor = self.connection.cursor()

        query = f"""
UPDATE {self.spider_table}
SET status = 'scheduled'
WHERE id = %s
        """
        cursor.execute(query, (url_id,))
        self.connection.commit()

    def set_url_completed(self, url_id: int):
        cursor = self.connection.cursor()

        query = f"""
UPDATE {self.spider_table}
SET status = 'completed'
WHERE id = %s
        """
        cursor.execute(query, (url_id,))
        self.connection.commit()

    def set_url_failed(self, url_id: int):
        cursor = self.connection.cursor()

        query = f"""
UPDATE {self.spider_table}
SET status = 'failed'
WHERE id = %s
        """
        cursor.execute(query, (url_id,))
        self.connection.commit()

    def set_url_unscheduled(self, url_id: int):
        cursor = self.connection.cursor()

        query = f"""
UPDATE {self.spider_table}
SET status = 'not_scheduled'
WHERE id = %s
        """
        cursor.execute(query, (url_id,))
        self.connection.commit()

    def batch_set_url_completed(self, url_ids: List[int]):
        cursor = self.connection.cursor()

        query = f"""
UPDATE {self.spider_table}
SET status = 'completed'
WHERE id = %s
        """
        cursor.executemany(query, [(x,) for x in url_ids])
        self.connection.commit()

    def add_event(self, event: Event):
        cursor = self.connection.cursor()

        query = f"""
INSERT INTO {self.table} (title, summary, context, day, month, year, url)
VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                event.url_id,
            ),
        )
        self.connection.commit()

    def add_bulk_event(self, events: List[Event]):
        cursor = self.connection.cursor()

        query = f"""
INSERT INTO {self.table}
(title, summary, context, day, month, year, url_id)
VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                    event.url_id,
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
