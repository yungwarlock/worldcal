import re
import requests
from multiprocessing.pool import ThreadPool

import numpy as np
from prefect import task
from bs4 import BeautifulSoup

from utils import check_is_banned_url
from storage import JSONLManager, BloomFilter


@task
def extract_all_urls(url, json_writer: JSONLManager, max_depth=2):
    bloom_filter = BloomFilter()

    def process_url(url: str):
        res = set()
        doc = requests.get(url)
        soup = BeautifulSoup(doc.text, "html.parser")

        for link in soup.find_all("a"):
            if not link.get("href", None):
                continue
            is_not_in_store = bloom_filter.lookup(link["href"]) is False
            is_valid_url = re.fullmatch(
                r"\bhttps?://[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*", link["href"]
            )
            # has_base_path = link["href"].find(url) == 0
            is_not_banned_url = check_is_banned_url(link["href"]) is False
            if is_not_in_store and is_valid_url and is_not_banned_url:
                bloom_filter.add(link["href"])
                res.add(link["href"])

        data = []
        for link in res:
            data.append({
                "url": link,
                "title": "",
                "hash": abs(hash(link)),
                "previous_node_hash": abs(hash(url)),
            })
        return data

    prev = set([url])
    while max_depth > 0:
        with ThreadPool() as pool:
            results = pool.map(process_url, prev)
            all_store = np.concatenate(([], *results), axis=None)
            prev_x = np.concatenate(([], *results), axis=None)
            prev = np.array([x["url"] for x in prev_x])
            json_writer.write_many(all_store)
        max_depth -= 1



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
