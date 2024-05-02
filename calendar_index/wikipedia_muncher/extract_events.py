import re
import os
import json
from typing import List, Dict

import openai
import trafilatura
from prefect import task, get_run_logger
from prefect.tasks import exponential_backoff
from langchain_text_splitters import RecursiveCharacterTextSplitter

from database import Event


@task(
    name="Extract events from text with Llama-3",
    task_run_name="extract-events-from-text-llama3",
    retries=10,
    retry_delay_seconds=exponential_backoff(backoff_factor=10),
)
def _extract_events(text: str) -> List[Dict[str, str]]:
    logger = get_run_logger()

    client = openai.Client(
        base_url="https://api.together.xyz/v1",
        api_key=os.environ.get("TOGETHER_API_KEY"),
    )

    system_message = """\
You are a helpful assistant.
Your task is to extract all events in it contained in the following text.

Output only in JSON. It will be a list of events. Each item should have the following fields:
- year: The year of the event. If not specified, it should be 0
- month: The month in numeric format between 0 and 11. If not specified, it should be 0
- day: The day. If not specified, it should be 0
- title: A short remark of the event
- summary: A 200-words summary of the event
If the text does not contain any notable event. Output an empty array
    """

    response = client.chat.completions.create(
        model="meta-llama/Llama-3-70b-chat-hf",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": text},
        ],
        temperature=0.6,
        max_tokens=4096,
    )
    logger.debug("Response: %s", response.choices[0].message.content)

    patterns = (
        (r"\[.*\]", 0),
        (r"```(.*)```", 1),
        (r"```json(.*)```", 1),
    )

    data = None
    res = response.choices[0].message.content

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



@task
def text_contain_dates(text):
    matches = []
    # Define the regex pattern to match dates in the formats "MM/DD/YYYY" and "YYYY-MM-DD"
    pattern = r"\b(?:\d{1,2}\/\d{1,2}\/\d{4}|\d{4}-\d{2}-\d{2})\b"
    m = re.findall(pattern, text, re.IGNORECASE)
    matches.extend(m)

    # Define the regex pattern to match dates in the format "Month Day, Year"
    pattern = r"(?i)(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}"
    m = re.findall(pattern, text, re.IGNORECASE)
    matches.extend(m)

    # Define the regex pattern to match dates in the format "Month Day"
    pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b"
    matches = re.findall(pattern, text, re.IGNORECASE)

    # Define the regex pattern to match dates in the formats "Month, Year" and "Year"
    pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)?\s*,?\s*\d{4}\b"
    m = re.findall(pattern, text, re.IGNORECASE)
    matches.extend(m)

    return matches



@task
def extract_events(url: str) -> List[Event]:
    logger = get_run_logger()
    all_events: List[Event] = []

    page = trafilatura.fetch_url(url)
    doc = trafilatura.extract(page)
    if not doc:
        logger.error("No document found")
        return all_events

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )


    docs = text_splitter.create_documents([doc])

    for text in docs:
        if not text_contain_dates(text.page_content):
            logger.debug("No dates found in text")
            all_events.extend([])
            continue

        extracted_events = _extract_events(text.page_content)
        if not extracted_events:
            logger.debug("No events found in text")
            all_events.extend([])
        else:
            all_events.extend([
                {
                    "year": event["year"],
                    "month": event["month"],
                    "day": event["day"],
                    "title": event["title"],
                    "summary": event["summary"],
                    "url": url,
                    "context": {},
                }
                for event in extracted_events
            ]) # type: ignore
    
    return all_events
