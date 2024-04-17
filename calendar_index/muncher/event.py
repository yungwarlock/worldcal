from typing import Dict, Any

from pydantic import BaseModel


class Event(BaseModel):
    year: int
    month: int
    day: int
    title: str
    summary: str
    url_id: int
    context: Dict[str, Any] = {}
