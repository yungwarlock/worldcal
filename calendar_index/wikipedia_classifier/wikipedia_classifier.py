from datetime import timedelta, datetime

from prefect import flow
from prefect.client.schemas.schedules import IntervalSchedule

from classifier import batch_get_url_category
from database import extract_batch, save_batch_to_database


@flow
def wikipedia_classifier(batch_size: int = 7):
    data = extract_batch(batch_size)
    data = batch_get_url_category(data)  # type: ignore
    save_batch_to_database(data)  # type: ignore


if __name__ == "__main__":
    wikipedia_classifier.serve(
        name="wikipedia_classifier",
        schedule=IntervalSchedule(
            timezone="America/Chicago",
            interval=timedelta(minutes=3),
            anchor_date=datetime(2024, 3, 1, 0, 0),
        ),
    )  # type: ignore
