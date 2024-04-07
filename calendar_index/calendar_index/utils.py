import re
import json
import trafilatura
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_page_text(url: str):
    doc = trafilatura.fetch_url(url)
    data = trafilatura.extract(doc)
    return data


def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.create_documents([text])


def extract_data(data: str):
    pattern = r"```python\n(.*?)\n```"
    matches = re.findall(pattern, data, re.IGNORECASE | re.DOTALL)

    if not matches:
        return []
    return json.loads(matches[0])
