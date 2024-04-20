import tempfile

from prefect import flow

from storage import JSONLManager, Storage
from extract_urls import extract_all_urls


@flow
def wikipedia_spider(url: str):
    storage = Storage.from_environment_variables()
    with tempfile.NamedTemporaryFile(dir="/tmp", mode="w+") as temp_fd:
        print("tempfile_name:", temp_fd.name)
        json_manager = JSONLManager(temp_fd)  # type: ignore
        extract_all_urls(url, json_manager)

        json_manager.respool()
        storage.add_urls_from_jsonl(json_manager)


if __name__ == "__main__":
    wikipedia_spider.serve(
            name="wikipedia_spider",
        )  # type: ignore
