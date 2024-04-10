import psycopg2

from prefect import task

from event import Event

db_name = "example"
db_user = "postgres"
db_password = "example"
db_host = "cloud-shell"
db_port = "5432"


class Storage:
    def __init__(self):
        self.connection = psycopg2.connect(
            user=db_user,
            host=db_host,
            port=db_port,
            dbname=db_name,
            password=db_password,
        )

    @task
    def add_event(self, event: Event):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO data_index (data) VALUES (%s)", (event.model_dump_json(),)
        )
        self.connection.commit()

    @task
    def remove_event(self, event_id: str):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM data_index WHERE id = %s", (event_id,))
        self.connection.commit()
