from pydantic import BaseModel


class Event(BaseModel):
    year: int
    month: int
    day: int
    title: str
    summary: str
