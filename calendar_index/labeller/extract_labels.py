import re
import os
import json
from typing import List, Dict
from urllib.parse import unquote

import nltk
import openai
import wikipedia
from prefect import task
from nltk.tokenize import word_tokenize
from tenacity import retry, stop_after_attempt

from models import URL

nltk.download('punkt')

@task
@retry(stop=stop_after_attempt(10), before_sleep=lambda x: print("Retrying..."))
def batch_categorize_text_together(prompt: str) -> List[dict]:
    system_message = """
You are a helpful assistant.

You are given a batch of summaries of text in the format:
{ID} - {SUMMARY}

Your task is to categorize the each of given summaries as one of the categories:

- Political
- Financial
- Economical
- Business
- Innovation
- None

Output as JSON list with the properties:
- id
- category
    """

    client = openai.OpenAI(
        base_url="https://api.together.xyz/v1",
        api_key=os.environ.get("TOGETHER_API_KEY"),
    )
    # print("TEXT: ", prompt)

    response = client.chat.completions.create(
        model="meta-llama/Llama-3-70b-chat-hf",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=1000,
    )
    # print("response:", response.choices[0].message.content)
    # print(response.usage.json())

    res = response.choices[0].message.content
    data = re.search(r"```(.*)```", res, re.S).group(1) # type: ignore

    return json.loads(data)

@task
def batch_get_url_category(urls: List[URL]) -> List[URL]:
    items = []

    res_items: Dict[str, URL] = {}
    for item in urls:
        try:
            pattern = r"/wiki/(.*)"
            page_id = re.search(pattern, item["url"]).group(1) # type: ignore
            page_id = unquote(page_id)
            page = wikipedia.page(page_id, auto_suggest=False)

            max_chars = 150
            # Remove special characters using regex
            clean_text = re.sub(r'[^\w\s]', '', page.summary)
            summary = word_tokenize(clean_text)[:max_chars]

            items.append(f"{item['id']} - {' '.join(summary) + '...'}")
            res_items[str(item["id"])] = item
        except wikipedia.DisambiguationError:
            continue

    categories = batch_categorize_text_together("\n".join(items))
    for category in categories:
        res_items[str(category["id"])]["category"] = category["category"]

    return res_items.values() # type: ignore
