import os
import json
from io import TextIOWrapper
from typing import Hashable

import psycopg2
from prefect import task

from models import URL


DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "")
DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


class BloomFilter:
    def __init__(self, size: int = 1500):
        self.size = size
        self.bit_array = [0] * size

    def add(self, item: Hashable):
        h = hash(item) % self.size
        self.bit_array[h] = 1

    def lookup(self, item: Hashable):
        h = hash(item) % self.size
        return self.bit_array[h] == 1


class JSONLManager:
    def __init__(self, fd: TextIOWrapper):
        self._fd = fd
        self.num_lines = 0

    def write(self, data):
        self._fd.write(json.dumps(data) + "\n")
        self.num_lines += 1

    def respool(self):
        self._fd.seek(0)

    def write_many(self, data: dict):
        self._fd.writelines(json.dumps(item) + "\n" for item in data)
        self.num_lines += len(data)

    def read(self):
        return json.loads(self._fd.readline())

    def read_all(self):
        return [json.loads(line) for line in self._fd.readlines()]


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
        INSERT INTO {self.table} (hash, url, title, previous_node_hash)
        VALUES (%s, %s, %s, %s);
        """

        cursor.execute(
            query,
            (
                event.hash,
                event.url,
                event.title,
                event.previous_node_hash,
            ),
        )

        self.connection.commit()
        cursor.close()

    def save_urls(self, json_manager: JSONLManager):
        batch_size = 10

        current_batch = 0
        while True:
            if current_batch >= json_manager.num_lines:
                break

            batch = []
            for _ in range(batch_size):
                try:
                    batch.append(json_manager.read())
                except json.JSONDecodeError:
                    break

            current_batch += batch_size

            cursor = self.connection.cursor()

            query = f"""
            INSERT INTO {self.table} (hash, url, title, previous_node_hash)
            VALUES (%s, %s, %s, %s);
            """

            cursor.executemany(
                query,
                [
                    (
                        event["hash"],
                        event["url"],
                        event["title"],
                        event["previous_node_hash"],
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
