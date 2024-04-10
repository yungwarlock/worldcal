from pydantic import BaseModel


class Event(BaseModel):
    year: int
    month: int
    day: int
    remark: str
    summary: str
