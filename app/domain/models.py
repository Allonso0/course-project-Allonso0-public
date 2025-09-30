from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, validator


class EntryKind(str, Enum):
    BOOK = "book"
    ARTICLE = "article"


class EntryStatus(str, Enum):
    PLANNED = "planned"
    READING = "reading"
    COMPLETED = "completed"


class EntryBase(BaseModel):
    title: str
    kind: EntryKind
    link: Optional[str] = None
    status: EntryStatus = EntryStatus.PLANNED

    @validator("title", allow_reuse=True)
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @validator("title")
    def title_length(cls, v):
        if len(v) > 200:
            raise ValueError("Title must be less than 200 characters")
        return v

    @validator("link")
    def validate_link(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError(
                "Link must be a valid URL starting with http:// or https://"
            )
        return v


class EntryCreate(EntryBase):
    pass


class EntryUpdate(BaseModel):
    title: Optional[str] = None
    kind: Optional[EntryKind] = None
    link: Optional[str] = None
    status: Optional[EntryStatus] = None

    @validator("title")
    def title_not_empty_if_provided(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty if provided")
        return v.strip() if v else v

    @validator("link")
    def validate_link_if_provided(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError(
                "Link must be a valid URL starting with http:// or https://"
            )
        return v


class Entry(EntryBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
        use_enum_values = True


class EntryList(BaseModel):
    items: List[Entry]
    total: int
