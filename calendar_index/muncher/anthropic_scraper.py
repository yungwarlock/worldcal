import json

import anthropic
from prefect import task
from tenacity import retry, stop_after_attempt, before_log, wait_exponential

from event import Event


system_content = """
You are a helpful assistant.
Your task is to extract all events in it contained in the following text.

Output only in JSON. It will be a list of events. Each item should have the following fields:
- year: The year of the event
- month: The month
- day: The day
- remark: A short remark of the event
- summary: A 200-words summary of the event
If the text does not contain any notable event. Output an empty array
"""

def before_log():
    print("retrying...")

@task
@retry(stop=stop_after_attempt(20) + wait_exponential(multiplier=1, min=5, max=80), before_sleep=before_log)
def extract_all_events(text: str):
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        system=system_content,
        messages=[{"role": "user", "content": [{"type": "text", "text": text}]}],
    )

    data = json.loads(message.content[0].text)
    return Event(**data)
