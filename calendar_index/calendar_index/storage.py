import psycopg2

from calendar_index.event import Event

db_name = 'example'
db_user = 'postgres'
db_password = 'example'
db_host = 'cloud-shell'
db_port = '5432'

class Storage:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

    def add_event(self, event: Event):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO data_index (data) VALUES (%s)",
            (event.model_dump_json(),)
        )
        self.connection.commit()

    def remove_event(self, event_id: str):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM data_index WHERE id = %s", (event_id,))
        self.connection.commit()
