import datetime

from pydantic import BaseModel


class URL(BaseModel):
    hash: str
    url: str
    title: str
    previous_node_hash: str
    date_added: datetime.datetime
