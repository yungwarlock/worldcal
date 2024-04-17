import tempfile

from prefect import flow
from datetime import timedelta, datetime
from prefect.client.schemas.schedules import IntervalSchedule

from storage import JSONLManager, Storage
from extract_urls import extract_all_urls


@flow
def spider(url: str):
    storage = Storage.from_environment_variables()
    with tempfile.NamedTemporaryFile(dir="/tmp", mode="w+") as temp_fd:
        # print("tempfile_name:", temp_fd.name)
        json_manager = JSONLManager(temp_fd)  # type: ignore
        extract_all_urls(url, json_manager)

        json_manager.respool()
        storage.add_urls_from_jsonl(json_manager)


if __name__ == "__main__":
    spider.serve(
        name="spider",
        schedule=IntervalSchedule(
            timezone="America/Chicago",
            interval=timedelta(minutes=10),
            anchor_date=datetime(2024, 3, 1, 0, 0),
        ),
    )  # type: ignore
