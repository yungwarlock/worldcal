from datetime import timedelta, datetime

from prefect import flow, get_run_logger
from prefect.client.schemas.schedules import IntervalSchedule

from extract_events import extract_events
from database import extract_batch, save_batch_to_database, set_url_as_failed

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
    wikipedia_muncher.serve(
        name="wikipedi_muncher",
        schedule=IntervalSchedule(
            timezone="America/Chicago",
            interval=timedelta(minutes=10),
            anchor_date=datetime(2024, 3, 1, 0, 0),
        ),
    )  # type: ignore
