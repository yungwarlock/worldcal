import os

from prefect import task
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from event import Event
from utils import extract_data


system_content = """
Extract all events in it contained in the following text.
Output in JSON. It will be a list of events. Each item should have the following fields:
- year: The year of the event
- month: The month
- day: The day
- remark: A short remark of the event
- summary: A 200-words summary of the event
"""


def before_log():
    print("retrying...")


@task
@retry(
    stop=stop_after_attempt(20) + wait_exponential(multiplier=1, min=5, max=80),
    before_sleep=before_log,
)
def extract_all_events(prompt: str):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("models/gemini-pro")

    text = f"{system_content}/n{prompt}" ""

    response = model.generate_content(text)
    data = extract_data(response.text)

    return Event(**data)
