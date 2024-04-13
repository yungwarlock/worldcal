import os

import psycopg2
import numpy as np
from prefect import task

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

    def add_url(self, event: URL):
        cursor = self.connection.cursor()

        query = f"""
        INSERT INTO {self.table} (hash, url, title, previous_node_hash, date_added)
        VALUES (%s, %s, %s, %s, %s);
        """

        cursor.execute(
            query,
            (
                event.hash,
                event.url,
                event.title,
                event.previous_node_hash,
                event.date_added,
            ),
        )

        self.connection.commit()
        cursor.close()

    def save_urls(self, urls: np.array):
        batch_size = 10
        batches = np.array_split(urls, len(urls) // batch_size)

        for batch in batches:
            cursor = self.connection.cursor()

            query = f"""
            INSERT INTO {self.table} (hash, url, title, previous_node_hash, date_added)
            VALUES (%s, %s, %s, %s, %s);
            """

            cursor.executemany(
                query,
                [
                    (
                        event["hash"],
                        event["url"],
                        event["title"],
                        event["previous_node_hash"],
                        event["date_added"],
                    )
                    for event in batch
                ],
            )

            self.connection.commit()
            cursor.close()

    @task
    def check_url_exists(self, url: str) -> bool:
        cursor = self.connection.cursor()

        query = f"""
        SELECT EXISTS(SELECT 1 FROM {self.table} WHERE url = %s)
        """

        cursor.execute(query, (url,))
        result = cursor.fetchone()[0]
        cursor.close()

        return result
