import os
import json

from prefect import task
import google.generativeai as genai
from tenacity import retry, wait_fixed

from event import Event
from utils import extract_data


system_content = """
Extract all events in it contained in the following text.
Output in JSON. It will be a list of events. Each item should have the following fields:
- year: The year of the event. If not specified, it should be 0
- month: The month in numeric format between 0 and 11. If not specified, it should be 0
- day: The day. If not specified, it should be 0
- title: A short remark of the event
- summary: A 200-words summary of the event
"""


def before_log(*args, **kwargs):
    print("retrying...")


@task
@retry(
    before_sleep=before_log,  # type: ignore
    wait=wait_fixed(120),  # wait 2 minutes between retries
    # stop=stop_after_attempt(20) + wait_exponential(multiplier=1, min=5, max=80),
)
def extract_all_events(prompt: str, url_id: int):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("models/gemini-pro")

    text = f"{system_content}/n{prompt}"

    response = model.generate_content(text)
    print("saftey:", response.prompt_feedback)
    if response.prompt_feedback or not response.parts:
        return []
    data = extract_data(response.text)
    print("data:", data)
    if not data:
        return []
    print("data:", data[0])
    data = json.loads(data[0])

    events = [
        Event(
            context={},
            title=item.get("title", ""),
            day=int(item.get("day", "0")),
            year=int(item.get("year", "0")),
            summary=item.get("summary", ""),
            month=int(item.get("month", "0")),
            url_id=url_id,
        )
        for item in data
    ]

    return events
