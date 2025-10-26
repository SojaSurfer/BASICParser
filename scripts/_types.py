from typing import Mapping, TypedDict

from .basics import BASICToken



class TagInfo(TypedDict):
    tag: str
    values: list[str | int | None]


type OptionalTokens = list[BASICToken] | None

type TagsetType = Mapping[str, dict[str, TagInfo]]