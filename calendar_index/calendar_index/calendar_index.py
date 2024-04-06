from prefect import flow
from prefect.artifacts import create_table_artifact

from calendar_index.storage import Storage
from calendar_index.find_dates import text_contain_dates
from calendar_index.utils import get_page_text, split_text
from calendar_index.anthropic_scraper import extract_all_events


@flow
def get_page_events(url: str):
    storage = Storage()

    page_data = get_page_text(url)
    docs = split_text(page_data)
    emph_docs = [t for t in docs if text_contain_dates(t.page_content)]

    all_data = []
    for text in emph_docs:
        data = extract_all_events(text.page_content)
        storage.add_event(data)
        all_data.append(data)

    create_table_artifact(
        key="page_data",
        table=all_data,
        description= "# Results of the page",
    )
