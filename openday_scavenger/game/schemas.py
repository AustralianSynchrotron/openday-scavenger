from pydantic import BaseModel, Field


class Answer(BaseModel):
    id: str
    answer: str
