import json

import anthropic
from prefect import task
from tenacity import retry, wait_fixed

from event import Event
from utils import extract_data


system_content = """
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


def before_log():
    print("retrying...")


@task
@retry(
    before_sleep=before_log,  # type: ignore
    wait=wait_fixed(120),  # wait 2 minutes between retries
    # stop=stop_after_attempt(20) + wait_exponential(multiplier=1, min=5, max=80),
)
def extract_all_events(text: str, url_id: int):
    client = anthropic.Anthropic()

    max_tokens = 3000
    temperature = 0.3
    model = "claude-3-haiku-20240307"

    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_content,
        temperature=temperature,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text,
                    },
                ],
            },
        ],
    )

    print(message.content[0].text)

    if not extract_data(message.content[0].text) == []:
        res = extract_data(message.content[0].text)
        res = json.loads(res[0])
    else:
        res = json.loads(message.content[0].text)

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
        for item in res
    ]

    return events
