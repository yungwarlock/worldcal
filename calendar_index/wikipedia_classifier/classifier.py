import os
import re
import json
from typing import List, TypedDict, Dict, Sequence

import openai
import trafilatura
from bs4 import BeautifulSoup
from prefect import task, get_run_logger
from prefect.tasks import exponential_backoff


class Item(TypedDict):
    url: str
    category: str


@task(
    name="Batch categorize text with Llama-3",
    task_run_name="batch-categorize-text-llama3",
    retries=10,
    retry_delay_seconds=exponential_backoff(backoff_factor=10),
)
def batch_categorize_text_llama3(prompt: str) -> List[Item]:
    logger = get_run_logger()

    system_message = """
You are a helpful assistant.

You are given a batch of summaries of text in the format:
{URL} - {SUMMARY}

Your task is to categorize the each of given summaries as one of the categories:

- Political
- Financial
- Economical
- Business
- Innovation
- None

Output as JSON list with the properties:
- url
- category
    """

    client = openai.OpenAI(
        base_url="https://api.together.xyz/v1",
        api_key=os.environ.get("TOGETHER_API_KEY"),
    )

    logger.debug("TEXT: %s" % prompt)

    response = client.chat.completions.create(
        model="meta-llama/Llama-3-70b-chat-hf",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=4096,
    )

    logger.debug("response: %s" % response.choices[0].message.content)

    res = response.choices[0].message.content

    patterns = (
        (r"\[.*\]", 0),
        (r"```(.*)```", 1),
        (r"```json(.*)```", 1),
    )

    data = None

    for pattern in patterns:
        search_result = re.search(pattern[0], res, re.S | re.I)  # type: ignore
        if search_result:
            data = search_result.group(pattern[1])
            logger.debug("data: %s" % data)
            break

    if not data:
        logger.error("No data found")
        return []

    return json.loads(data)


@task(
    name="Batch get URL category",
    task_run_name="batch-get-url-category",
    retries=10,
)
def batch_get_url_category(urls: Sequence[str]):
    logger = get_run_logger()

    items = []
    res_items: Dict[str, str] = {}
    for url in urls:
        try:
            res = trafilatura.fetch_url(url)
            if not res:
                logger.error(f"Failed to fetch {url}")
                items.append(f"{url} - None")
                res_items[url] = "None"
                continue

            soup = BeautifulSoup(res, "lxml")  # type: ignore

            title = soup.find(id="firstHeading")
            if not title:
                logger.error(f"Title not found for {url}")
                title = ""
            else:
                title = title.string  # type: ignore

            doc = str(soup.find_all("p")[1])
            if soup.find_all("p")[1].string == "":
                doc = str(soup.find_all("p")[0])

            max_chars = 150

            # Remove special characters using regex
            clean_text = re.sub(r"[^\w\s]", "", doc)  # type: ignore
            summary = clean_text[:max_chars]

            items.append(f"{url} - {summary}")
            res_items[url] = url

        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            items.append(f"{url} - None")
            res_items[url] = "None"
            continue

    if not items:
        return []

    categories = batch_categorize_text_llama3("\n".join(items))
    for category in categories:
        res_items[category["url"]] = category["category"]

    return res_items
