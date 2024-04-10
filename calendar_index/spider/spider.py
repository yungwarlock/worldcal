from prefect import flow
from prefect.artifacts import create_table_artifact

from extract_urls import extract_all_urls, batch_array


@flow
def spider(url):
    all_res = extract_all_urls(url)
    batch_links = batch_array(list(all_res), batch_size=10)

    create_table_artifact(
        key="all links",
        table=batch_links,
        description=f"""
All links from the page

Page: {url}
links count: {len(all_res)}
links: {batch_links}
""",
    )
    return batch_links


if __name__ == "__main__":
    spider.serve(name="get_page_events")
