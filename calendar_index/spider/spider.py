import tempfile

from prefect import flow

from storage import JSONLManager, Storage
from extract_urls import extract_all_urls


@flow
def spider(url):
    storage = Storage.from_environment_variables()

    temp_fd = tempfile.NamedTemporaryFile(dir="/tmp", delete=False, mode="w+")
    # print("tempfile_name:", temp_fd.name)
    json_manager = JSONLManager(temp_fd)  # type: ignore
    extract_all_urls(url, json_manager)
    json_manager.respool()
    storage.save_urls(json_manager)


if __name__ == "__main__":
    spider("https://arise.tv")
