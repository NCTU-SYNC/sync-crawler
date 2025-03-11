from collections.abc import Sequence
from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class News(BaseModel):
    title: str
    content: Sequence[str]
    content_hash: str
    category: str
    modified_date: datetime
    media: str
    tags: Sequence[str]
    url: str
    url_hash: str
    mongo_id: ObjectId = Field(default_factory=ObjectId)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def text(self) -> str:
        return " ".join(self.content)
