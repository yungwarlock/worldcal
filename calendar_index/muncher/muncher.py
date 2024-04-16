from prefect import flow
# from prefect.artifacts import create_table_artifact

from storage import Storage
from find_dates import text_contain_dates
from utils import get_page_text, split_text
# from anthropic_scraper import extract_all_events
from gemini_scraper import extract_all_events


@flow
def get_page_events():
    storage = Storage.from_environment_variables()

    urls = storage.get_urls_from_range(0, 50)

    for url in urls:
        page_data = get_page_text(url)

        if not page_data:
            continue

        docs = split_text(page_data)
        emph_docs = [t for t in docs if text_contain_dates(t.page_content)]

        all_data = []
        for text in emph_docs:
            events = extract_all_events(text.page_content)
            storage.add_bulk_event(events)
            [all_data.append(e) for e in events]

    # create_table_artifact(
    #     key=url,
    #     table=all_data,
    #     description=f"""Events found on the page {url}:""",
    # )


if __name__ == "__main__":
    get_page_events.serve(name="get_page_events")
    # get_page_events()
