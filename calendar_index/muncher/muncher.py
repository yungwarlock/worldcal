from datetime import timedelta, datetime

from prefect import flow
# from prefect.artifacts import create_table_artifact
from prefect.client.schemas.schedules import IntervalSchedule

from storage import Storage
from find_dates import text_contain_dates
from utils import get_page_text, split_text

from gemini_scraper import extract_all_events
# from anthropic_scraper import extract_all_events


@flow
def muncher():
    storage = Storage.from_environment_variables()

    url_items = storage.get_unscheduled_urls()

    for item in url_items:
        storage.set_url_scheduled(item["id"])

        try:
            page_data = get_page_text(item["url"])

            if not page_data:
                continue

            docs = split_text(page_data)
            emph_docs = [t for t in docs if text_contain_dates(t.page_content)]

            for text in emph_docs:
                events = extract_all_events(text.page_content, item["id"])
                storage.add_bulk_event(events)
        except Exception:
            storage.set_url_unscheduled(item["id"])
            continue

    # create_table_artifact(
    #     key=url,
    #     table=all_data,
    #     description=f"""Events found on the page {url}:""",
    # )


if __name__ == "__main__":
    muncher.serve(
        name="get_events",
        schedule=IntervalSchedule(
            timezone="America/Chicago",
            interval=timedelta(minutes=10),
            anchor_date=datetime(2024, 3, 1, 0, 0),
        ),
    )  # type: ignore
