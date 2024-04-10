import re
import requests
from multiprocessing.pool import ThreadPool

import numpy as np
from prefect import task
from bs4 import BeautifulSoup


@task
def extract_all_urls(url, max_depth=2):
    all_store = np.array([])

    def process_url(url):
        res = set()
        doc = requests.get(url)
        soup = BeautifulSoup(doc.text, "html.parser")
        for link in soup.find_all("a"):
            if not link.get("href", None):
                continue
            is_not_in_store = link["href"] not in all_store
            is_valid_url = re.fullmatch(
                r"\bhttps?://[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*", link["href"]
            )
            has_base_path = link["href"].find(url) == 0
            if is_not_in_store and is_valid_url and has_base_path:
                res.add(link["href"])
        return list(res)

    prev = np.array([url])
    while max_depth > 0:
        with ThreadPool() as pool:
            results = pool.map(process_url, prev)
            all_store = np.concatenate((all_store, *results), axis=None)
            prev = np.concatenate(([], *results), axis=None)
        max_depth -= 1

    return all_store


@task
def extract_all_urls2(url):
    # This function is a simplified version of the get_all_links function from the extract_urls.py file
    # It uses a simple loop to extract all the URLs from the given URL
    all_urls = set()
    urls_to_process = [url]
    while urls_to_process:
        current_url = urls_to_process.pop()
        if current_url in all_urls:
            continue
        doc = requests.get(current_url)
        soup = BeautifulSoup(doc.text, "html.parser")
        for link in soup.find_all("a"):
            if not link.get("href", None):
                continue
            is_valid_url = re.fullmatch(
                r"\bhttps?://[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*", link["href"]
            )
            has_base_path = link["href"].find(url) == 0
            if is_valid_url and has_base_path:
                all_urls.add(link["href"])
                urls_to_process.append(link["href"])
    return list(all_urls)


@task
def batch_array(arr, batch_size=4):
    items = []
    for i in range(0, len(arr), batch_size):
        items.append(arr[i : i + batch_size])
    return items
