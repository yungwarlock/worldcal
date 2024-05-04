import os
import sentry_sdk
from datetime import timedelta, datetime

from prefect import flow, get_run_logger
from prefect.client.schemas.schedules import IntervalSchedule

from extract_events import extract_events
from database import extract_batch, save_batch_to_database, set_url_as_failed


sentry_sdk.init(
    dsn="https://c1cfcfa5e77aa8e116f77c2b9fed6c00@o4506628622123008.ingest.us.sentry.io/4507197938794496",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

DEBUG = os.environ.get("DEBUG", "") is True
JOB_INTERVAL = int(os.environ.get("JOB_INTERVAL", 50))


@flow
def wikipedia_muncher():
    logger = get_run_logger()

    # Get the urls
    batch = extract_batch()

    # Extract events
    for url in batch:
        logger.info("Extracting events from %s", url)
        try:
            events_batches = extract_events(url)
            for event_batch in events_batches:
                save_batch_to_database(event_batch)
        except Exception:
            set_url_as_failed(url)


if __name__ == "__main__":
    if DEBUG:
        wikipedia_muncher()
    else:
        wikipedia_muncher.serve(
            name="wikipedi_muncher",
            schedule=IntervalSchedule(
                timezone="America/Chicago",
                interval=timedelta(minutes=JOB_INTERVAL),
                anchor_date=datetime(2024, 3, 1, 0, 0),
            ),
        )  # type: ignore
