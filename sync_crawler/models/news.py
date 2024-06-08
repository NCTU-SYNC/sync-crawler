from collections.abc import Sequence
from datetime import datetime

import pydantic


class News(pydantic.BaseModel):
    title: str
    content: Sequence[str]
    content_hash: str
    category: str
    modified_date: datetime
    media: str
    tags: Sequence[str]
    url: str
    url_hash: str

    model_config = pydantic.ConfigDict(extra="forbid")

    @property
    def text(self) -> str:
        return " ".join(self.content)
