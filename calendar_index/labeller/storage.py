import os
from typing import List

import psycopg2

from models import URL

DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "")
DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


class Storage:
    table = "spider_index"

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

    def get_urls_without_category(self, limit=15) -> list[URL]:
        cursor = self.connection.cursor()
        query = f"""
SELECT id, url
FROM {self.table}
WHERE category IS 'unknown'
LIMIT %s
"""

        cursor.execute(query, (limit,))
        return [
            {
                "id": id_,
                "url": url,
                "category": "unknown",
            }
            for id_, url in cursor.fetchall()
        ]

    def batch_update_categories(self, urls: List[URL]):
        cursor = self.connection.cursor()
        query = f"""
UPDATE {self.table}
SET category = %s
WHERE id = %s
"""
        cursor.executemany(
            query,
            [
                (
                    url["category"],
                    url["id"],
                )
                for url in urls
            ],
        )
        self.connection.commit()
