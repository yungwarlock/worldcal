import os

from prefect import task
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from event import Event
from utils import extract_data


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


@task
@retry(stop=stop_after_attempt(20) + wait_exponential(multiplier=1, min=5, max=80))
def extract_all_events(text: str):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-1.0-pro-latest")
    chat = model.start_chat(history=[])

    text = f"""
    {system_content}

    {text}
    """

    response = chat.send_message([system_content, text])
    data = extract_data(response.text)

    return Event(**data)
