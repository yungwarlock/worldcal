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
            data.append(
                {
                    "url": link,
                    "title": "",
                    "hash": abs(hash(link)),
                    "previous_node_hash": abs(hash(url)),
                }
            )
        return data

    prev = set([url])
    while max_depth > 0:
        with ThreadPool() as pool:
            results = pool.map(process_url, prev)
            all_store = np.concatenate(([], *results), axis=None)
            prev_x = np.concatenate(([], *results), axis=None)
            prev = np.array([x["url"] for x in prev_x])
            json_writer.write_many(list(all_store))
        max_depth -= 1
