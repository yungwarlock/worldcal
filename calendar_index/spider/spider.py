from prefect import flow
from prefect.artifacts import create_table_artifact

from storage import Storage
from extract_urls import extract_all_urls


@flow
def spider(url):
    storage = Storage.from_environment_variables()

    all_res = extract_all_urls(url)

    storage.save_urls(all_res)

    create_table_artifact(
        key="all links",
        table=all_res,
        description=f"""
All links from the page

Page: {url}
links count: {len(all_res)}
""",
    )
    return all_res


if __name__ == "__main__":
    spider.serve(name="extract_all_urls")
