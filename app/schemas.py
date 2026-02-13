from pydantic import BaseModel
from datetime import datetime


class PageBase(BaseModel):
    slug: str
    title: str
    content: str


class PageCreate(PageBase):
    pass


class PageResponse(PageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
