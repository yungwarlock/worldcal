import re
import os
import json
from typing import Optional, Sequence

import anthropic
import trafilatura
from pydantic import BaseModel
from tavily import TavilyClient


class Result(BaseModel):
    title: str
    url: str
    content: str
    score: float
    raw_content: Optional[str]


class Query(BaseModel):
    query: str
    follow_up_questions: Optional[str]
    answer: Optional[str]
    images: Optional[str]
    results: Sequence[Result]
    response_time: float


class Critiquer:
    max_tokens = 600
    temperature = 0.1
    model = "claude-3-sonnet-20240229"
    stop_sequences = ["</search>", "</browser>", "</response>"]

    @classmethod
    def from_env(cls):
        return cls(
            anthropic.Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            ),
            tavily=TavilyClient(
                api_key=os.environ.get("TAVILY_API_KEY", ""),
            ),
        )

    def __init__(self, client: anthropic.Anthropic, tavily: TavilyClient):
        self.client = client
        self._tavily = tavily
        self._messages = []

    def critique(self, event: str) -> dict | None:
        self._messages.append(
            {
                "role": "user",
                "content": event,
            },
        )

        res = self.client.messages.create(
            model=self.model,
            messages=self._messages,
            max_tokens=self.max_tokens,
            system=self.system_message,
            temperature=self.temperature,
        )

        self._messages.append(
            {
                "role": "assistant",
                "content": res.content,
            },
        )

        if res.stop_reason == "stop_sequence" and any(
            seq in res.stop_sequence for seq in self.stop_sequences
        ):
            stop_sequence = res.stop_sequence
            text = res.content[0].text + stop_sequence

            if "</search>" in stop_sequence:
                query = re.search(r"<search>(.*?)</search>", text).group(1)
                self._messages.append(
                    {
                        "role": "assistant",
                        "content": self.handle_search(query),
                    },
                )
            elif "</browser>" in stop_sequence:
                url = re.search(r"<browser>(.*?)</browser>", text).group(1)
                self._messages.append(
                    {
                        "role": "assistant",
                        "content": self.handle_browser(url),
                    },
                )
            elif "</response>" in stop_sequence:
                text = re.search(r"<response>(.*?)</response>", text).group(1)
                json_match = re.search(r"\{(?:[^{}]|)*\}", text).group()
                json_data = json.loads(json_match)
                return json_data
        else:
            return None
            raise ValueError(f"Unexpected stop reason: {res.stop_reason}")

    def handle_search(self, query: str):
        res = Query(**self._tavily.search(query))
        return [
            {
                "title": result.title,
                "url": result.url,
            }
            for result in res.results
        ]

    def handle_browser(self, url: str):
        doc = trafilatura.fetch_url(url)
        content = trafilatura.extract(doc)
        return content

    system_message = """
You are a helpful assistant.
Your task is to find out the true date that a given event occurred.
You will be given: the event title, summary and the assumed date. Your response should be in JSON format. It should have the following fields:
- title: the definitive title
- summary: the definitive and brief summary
- day
- month
- year

You have access to the following tools:
- Search: Gives you access to a search engine. It will return a list of urls relevant to your query. Do not worry about the scores
- Browser: Use it to get the full page of a url you get from the search engine.
- Calculator: For doing complex mathematical operations
- Ask for help: For requesting feedback from a human expert

You have the following tasks:
- Create a plan for how you will solve this task.
- Act on each one step by step

RESPONSES:
When giving any of this responses stop and expect the user to reply to them.

Calls to the tools should be given in the format:
<TOOL_NAME>REQUEST</TOOL_NAME>
Stop at this point and expect a response from the tool. It will be within <tool-response></tool-response>

When reflecting on anything, enclose the message within <self-reflect></self-reflect>. Make each self reflect as brief as possible

When giving back a response it should be enclosed in <response></response>
    """
