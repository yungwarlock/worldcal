from typing import TypedDict


class URL(TypedDict):
    hash: str
    url: str
    category: str
    previous_node_hash: str