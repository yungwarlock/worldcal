import os
from typing import List

import psycopg2


DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "")
DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


class BaseStorage:
    table = ""

    def __init__(self, username: str, password: str, host: str, db_name: str):
        self.connection = psycopg2.connect(
            host=host,
            user=username,
            dbname=db_name,
            password=password,
        )

    @classmethod
    def from_environment_variables(cls):
        return cls(
            host=DB_HOST,
            db_name=DB_NAME,
            username=DB_USER,
            password=DB_PASSWORD,
        )


class SpiderIndexStorage(BaseStorage):
    table = "spider_index"

    def get_unscheduled_items(self, limit: int = 10) -> List[int]:
        cursor = self.connection.cursor()

        query = """
SELECT id, date_added FROM spider_index
WHERE status = 'not_scheduled'
ORDER BY date_added
LIMIT %s
        """

        cursor.execute(query, (limit,))
        return [x[0] for x in cursor.fetchall()]

    def mark_as_scheduled(self, ids: List[int]):
        cursor = self.connection.cursor()

        query = """
UPDATE spider_index
SET status = 'scheduled'
WHERE id = %s
        """

        cursor.executemany(query, ((x,) for x in ids))
        self.connection.commit()


class CalendarIndexStorage(BaseStorage):
    table = "calendar_index"

    def get_unscheduled_urls(self, limit: int) -> List[str]:
        cursor = self.connection.cursor()

        query = """
SELECT id, date_added FROM calendar_index
WHERE status = 'not_scheduled'
ORDER BY date_added
LIMIT %s
        """

        cursor.execute(query, (limit,))
        return [x[0] for x in cursor.fetchall()]

    def mark_as_scheduled(self, ids: List[int]):
        cursor = self.connection.cursor()

        query = """
UPDATE calendar_index
SET status = 'scheduled'
WHERE id = %s
        """

        cursor.executemany(query, ((x,) for x in ids))
        self.connection.commit()


class MunchingJobStorage(BaseStorage):
    table = "munching_jobs"

    def schedule_job(self, ids: List[int]):
        cursor = self.connection.cursor()

        query = """
INSERT INTO munching_jobs (items)
VALUES (%s)
        """

        cursor.execute(query, ((ids,),))
        self.connection.commit()

    def get_latest_job(self):
        cursor = self.connection.cursor()

        query = """
SELECT id, items FROM munching_jobs
ORDER BY date_added DESC
LIMIT 1
        """

        cursor.execute(query)
        res = cursor.fetchone()
        if not res:
            return None
        return res[0]

    def set_job_as_scheduled(self, job_id: int):
        cursor = self.connection.cursor()

        query = """
UPDATE munching_jobs
SET status = 'scheduled'
WHERE id = %s
        """

        cursor.execute(query, (job_id,))
        self.connection.commit()

    def set_job_as_done(self, job_id: int):
        cursor = self.connection.cursor()

        query = """
UPDATE munching_jobs
SET status = 'completed'
WHERE id = %s
        """

        cursor.execute(query, (job_id,))
        self.connection.commit()
