from datetime import timedelta, datetime

import sentry_sdk
from prefect import flow
from prefect.client.schemas.schedules import IntervalSchedule

from classifier import batch_get_url_category
from database import extract_batch, save_batch_to_database


sentry_sdk.init(
    dsn="https://e44ec5833daf8098d78bcb657dec51a6@o4506628622123008.ingest.us.sentry.io/4507198027988992",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


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
