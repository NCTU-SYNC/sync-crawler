from collections.abc import Sequence
from datetime import datetime
from typing import Any, ClassVar

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

    excluded_metadata_keys: ClassVar = ["modified_date"]

    @property
    def text(self) -> str:
        return " ".join(self.content)

    @property
    def metadata(self) -> dict[str, Any]:
        return self.model_dump(
            mode="json",  # use json mode to convert `modified_date` to string
            include={"title", "category", "modified_date"},
        )
