from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNSPECIFIED: _ClassVar[Category]
    POLITICAL_ECONOMY: _ClassVar[Category]
    INTERNATIONAL: _ClassVar[Category]
    SOCIETY: _ClassVar[Category]
    TECHNOLOGY: _ClassVar[Category]
    ENVIRONMENT: _ClassVar[Category]
    LIFE: _ClassVar[Category]
    SPORTS: _ClassVar[Category]
UNSPECIFIED: Category
POLITICAL_ECONOMY: Category
INTERNATIONAL: Category
SOCIETY: Category
TECHNOLOGY: Category
ENVIRONMENT: Category
LIFE: Category
SPORTS: Category

class News(_message.Message):
    __slots__ = ["title", "content", "category", "modified_date", "media", "tags", "url", "url_hash", "content_hash"]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_DATE_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    URL_HASH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    title: str
    content: _containers.RepeatedScalarFieldContainer[str]
    category: Category
    modified_date: _timestamp_pb2.Timestamp
    media: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    url: str
    url_hash: str
    content_hash: str
    def __init__(self, title: _Optional[str] = ..., content: _Optional[_Iterable[str]] = ..., category: _Optional[_Union[Category, str]] = ..., modified_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., media: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., url: _Optional[str] = ..., url_hash: _Optional[str] = ..., content_hash: _Optional[str] = ...) -> None: ...
