import enum
from typing import List, NamedTuple


class ChangeType(enum.Enum):
    CREATE = 1
    MODIFY = 2
    DELETE = 3


class ElementType(enum.Enum):
    NODE = 1
    WAY = 2
    RELATION = 3


ElementID = int


class ElementIdentifier(NamedTuple):
    """An identifier for an OSM element.

    According to the OSM wiki, the ID of an element is unique only within its
    element type.
    To identify an element we need both the element type and the ID.
    """

    id: ElementID
    etype: ElementType


class ChangeInfo(NamedTuple):
    """A tuple containing information about a change.
    The tuple contains a ChangeType and an ElementIdentifier.
    """

    change_type: ChangeType
    element_identifier: ElementIdentifier


OSCInfo = List[ChangeInfo]

Coordinates = list[tuple[float, float]]
IntCoords = list[tuple[int, int]]
FileName = str
