import enum
from typing import Literal

Properties = dict[str, str]


@enum.unique
class ChangeType(enum.Enum):
    INSERT = enum.auto()
    UPDATE = enum.auto()
    DELETE = enum.auto()


PropKey = str
PropVal = str

InsertCommand = tuple[Literal[ChangeType.INSERT], PropKey, PropVal]
UpdateCommand = tuple[Literal[ChangeType.UPDATE], PropKey, PropVal]
DeleteCommand = tuple[Literal[ChangeType.DELETE], PropKey]
PatchCommand = InsertCommand | UpdateCommand | DeleteCommand


def diff(props_a: Properties, props_b: Properties):
    for key, val in props_a.items():
        if key in props_b and props_b[key] != val:
            yield (ChangeType.UPDATE, key, props_b[key])
        if key not in props_b:
            yield (ChangeType.DELETE, key)
    only_b_keys = set(props_b.keys()) - set(props_a.keys())
    for key in only_b_keys:
        yield (ChangeType.INSERT, key, props_b[key])
