from pydantic import BaseModel


class VisitorCreate(BaseModel):
    uid: str