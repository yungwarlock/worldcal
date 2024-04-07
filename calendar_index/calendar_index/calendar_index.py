from prefect import flow
from prefect.artifacts import create_table_artifact

from storage import Storage
from find_dates import text_contain_dates
from utils import get_page_text, split_text
from gemini_scraper import extract_all_events

default = "https://www.bbc.com/news/world-middle-east-14649284"

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



if __name__ == "__main__":
    get_page_events.serve(name="get_page_events")
