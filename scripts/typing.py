from typing import Mapping, TypedDict



class _TagInfo(TypedDict):
    tag: str
    values: list[str | int | None]


type TagsetType = Mapping[str, dict[str, _TagInfo]]
