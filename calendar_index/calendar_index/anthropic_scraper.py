import sys
import json
import logging

import anthropic
from tenacity import retry, stop_after_attempt, before_log

from event import Event


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

logger = logging.getLogger(__name__)


system_content = """
You are helpful assistant.
You will be given a piece of text and your task is to extract any
notable events in it.

Output in JSON. It will be a list of events. Each item should have the following fields:

- Year: The year of the event
- Month: The month
- Day: The day
- Remark: A short remark of the event
- Summary: A 200-words summary of the event
If the text does not contain any notable event. Output an empty array
"""


@retry(stop=stop_after_attempt(20), before=before_log(logger, logging.DEBUG))
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
