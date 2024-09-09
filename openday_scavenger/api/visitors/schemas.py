from pydantic import BaseModel


class VisitorCreate(BaseModel):
    uid: str


class VisitorUpdate(BaseModel):
    id: int
    uid: str | None = None
    checked_in: str | None = None
    checked_out: str | None = None
    check_out: bool | None = None


class VisitorAuth(BaseModel):
    uid: str | None


class VisitorPoolCreate(BaseModel):
    number_of_entries: int = 100
