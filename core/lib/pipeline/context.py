from pydantic import BaseModel


class Context(BaseModel):
    header: str
    steps: list[str]
    footer: str
    score: float
