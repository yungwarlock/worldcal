import os
import sys
import logging

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, before_log

from event import Event
from utils import extract_data

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


@retry(stop=stop_after_attempt(10), before=before_log(logger, logging.DEBUG))
def extract_all_events(text: str):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-1.0-pro-latest")
    chat = model.start_chat(history=[])

    text = f"""
    {system_content}

    {text}
    """
    logging.debug("TEXT: %s", text)

    response = chat.send_message([system_content, text])
    data = extract_data(response.text)

    return Event(**data)
