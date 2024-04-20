from datetime import timedelta, datetime

from prefect import flow
from prefect.client.schemas.schedules import IntervalSchedule

from storage import Storage
from extract_labels import batch_get_url_category


@flow
def label():
    storage = Storage.from_environment_variables()

    urls = storage.get_urls_without_category()
    new_urls = batch_get_url_category(urls)
    storage.batch_update_categories(new_urls)


if __name__ == "__main__":
    label.serve(
        name="labeller",
        schedule=IntervalSchedule(
            timezone="America/Chicago",
            interval=timedelta(minutes=10),
            anchor_date=datetime(2024, 3, 1, 0, 0),
        ),
    ) # type: ignore
