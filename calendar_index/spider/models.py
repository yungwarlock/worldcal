import datetime
from typing import TypedDict

class URL(TypedDict):
    hash: str
    url: str
    title: str
    previous_node_hash: str
    date_added: datetime.datetime
