import re
import requests
from typing import List
from multiprocessing.pool import ThreadPool

import numpy as np
from prefect import task
from bs4 import BeautifulSoup

from models import URL
from storage import JSONLManager, BloomFilter


@task
def extract_all_urls(url, json_writer: JSONLManager, max_depth=2):
    bloom_filter = BloomFilter()
    origin_url = url

    def process_url(url: str):
        res = set()
        try:
            doc = requests.get(url)
            soup = BeautifulSoup(doc.text, "html.parser")

            for link in soup.find_all("a"):
                if not link.get("href", None):
                    continue
                is_not_in_store = bloom_filter.lookup(link["href"]) is False
                is_valid_url = re.fullmatch(r"^\/wiki\/.*", link["href"])
                is_not_wiki_page = re.fullmatch(r"^\/wiki\/.*:.*", link["href"])
                # has_base_path = link["href"].find(url) == 0
                # is_not_banned_url = check_is_banned_url(link["href"]) is False
                if is_not_in_store and is_valid_url and not is_not_wiki_page:
                    bloom_filter.add(link["href"])
                    res.add(f"https://en.wikipedia.org{link['href']}")
        except Exception:
            return res

        data: List[URL] = []
        for link in res:
            data.append(
                {
                    "url": link,
                    "hash": str(abs(hash(link))),
                    "previous_node_hash": "origin"
                    if url == origin_url
                    else str(abs(hash(url))),
                }
            )
        return data

    prev = set([url])
    json_writer.write(
        {
            "url": url,
            "hash": str(abs(hash(url))),
            "previous_node_hash": "origin",
        },
    )
    while max_depth > 0:
        with ThreadPool() as pool:
            results = pool.map(process_url, prev)

            new_prev = np.concatenate(([], *results), axis=None) # type: ignore
            prev = np.array([x["url"] for x in new_prev])

            all_store = np.concatenate(([], *results), axis=None) # type: ignore
            json_writer.write_many(all_store)
        max_depth -= 1
