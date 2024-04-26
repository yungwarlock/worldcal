import re
import os
import json
from csv import DictWriter
from typing import List, Dict, TypedDict

import nltk
import openai
import requests
import trafilatura
import google.generativeai as genai
from nltk.tokenize import word_tokenize
from prefect import task, get_run_logger
from tenacity import retry, wait_exponential, stop_after_attempt


nltk.download("punkt")


class Item(TypedDict):
    url: str
    category: str


@task
@retry(
    stop=stop_after_attempt(10),
    before_sleep=lambda x: print("Retrying..."),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def batch_categorize_text_gemini(prompt: str) -> List[Item]:
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
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("models/gemini-pro")

    logger = get_run_logger()

    text = f"{system_message}\n\n{prompt}"

    logger.debug("prompt: %s" % text)

    response = model.generate_content(text)
    if response.prompt_feedback or not response.parts:
        logger.info("saftey: %s" % response.prompt_feedback)
        return []

    logger.debug("response: %s" % response.text)
    data = re.search(r"```json(.*)```", response.text, re.S | re.I).group(1)  # type: ignore
    logger.debug("data: %s" % data)
    return json.loads(data)


@task
@retry(
    stop=stop_after_attempt(10),
    before_sleep=lambda x: print("Retrying..."),
    wait=wait_exponential(multiplier=1, min=4, max=10),
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

    logger.info("TEXT: %s" % prompt)

    response = client.chat.completions.create(
        model="meta-llama/Llama-3-8b-chat-hf",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=4096,
    )

    logger.info("response: %s" % response.choices[0].message.content)

    res = response.choices[0].message.content

    patterns = (
        (r"\[.*\]", 0),
        (r"```(.*)```", 1),
        (r"```json(.*)```", 1),
    )

    data = None

    for pattern in patterns:
        search_result = re.search(pattern[0], res, re.S | re.I) # type: ignore
        if search_result:
            data = search_result.group(pattern[1])
            logger.info("data: %s" % data)
            break
    
    if not data:
        logger.error("No data found")
        return []

    return json.loads(data)


@task
def batch_get_url_category(urls: List[str], result_writer: DictWriter):
    logger = get_run_logger()

    items = []
    res_items: Dict[str, str] = {}
    for url in urls:
        try:
            res = requests.get(f"https://{url}", timeout=(5, 10))
            data = trafilatura.extract(res.text)
            if not data:
                data = "No data found..."

            max_chars = 150
            # Remove special characters using regex
            clean_text = re.sub(r"[^\w\s]", "", data)
            summary = word_tokenize(clean_text)[:max_chars]

            items.append(f"{url} - {' '.join(summary)}")
            res_items[url] = url
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            continue

    if not items:
        return []

    categories = batch_categorize_text_llama3("\n".join(items))
    for category in categories:
        res_items[category["url"]] = category["category"]

    for domain, category in res_items.items():
        result_writer.writerow({"domain": domain, "category": category})
