from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreationEvent(_message.Message):
    __slots__ = ("id", "timestamp", "version", "point", "linestring", "polygon", "properties")
    ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    POINT_FIELD_NUMBER: _ClassVar[int]
    LINESTRING_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: int
    timestamp: _timestamp_pb2.Timestamp
    version: int
    point: Point
    linestring: LineString
    polygon: Polygon
    properties: Properties
    def __init__(self, id: _Optional[int] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., version: _Optional[int] = ..., point: _Optional[_Union[Point, _Mapping]] = ..., linestring: _Optional[_Union[LineString, _Mapping]] = ..., polygon: _Optional[_Union[Polygon, _Mapping]] = ..., properties: _Optional[_Union[Properties, _Mapping]] = ...) -> None: ...

class Properties(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: _containers.RepeatedScalarFieldContainer[str]
    value: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, key: _Optional[_Iterable[str]] = ..., value: _Optional[_Iterable[str]] = ...) -> None: ...

class ModificationEvent(_message.Message):
    __slots__ = ("id", "timestamp", "version", "point_patch", "linestring_patch", "polygon_patch", "prop_patch")
    ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    POINT_PATCH_FIELD_NUMBER: _ClassVar[int]
    LINESTRING_PATCH_FIELD_NUMBER: _ClassVar[int]
    POLYGON_PATCH_FIELD_NUMBER: _ClassVar[int]
    PROP_PATCH_FIELD_NUMBER: _ClassVar[int]
    id: int
    timestamp: _timestamp_pb2.Timestamp
    version: int
    point_patch: Point
    linestring_patch: LineStringPatch
    polygon_patch: LineStringPatch
    prop_patch: PropPatch
    def __init__(self, id: _Optional[int] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., version: _Optional[int] = ..., point_patch: _Optional[_Union[Point, _Mapping]] = ..., linestring_patch: _Optional[_Union[LineStringPatch, _Mapping]] = ..., polygon_patch: _Optional[_Union[LineStringPatch, _Mapping]] = ..., prop_patch: _Optional[_Union[PropPatch, _Mapping]] = ...) -> None: ...

class DeletionEvent(_message.Message):
    __slots__ = ("id", "timestamp", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    timestamp: _timestamp_pb2.Timestamp
    version: int
    def __init__(self, id: _Optional[int] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., version: _Optional[int] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ("lon", "lat")
    LON_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    lon: int
    lat: int
    def __init__(self, lon: _Optional[int] = ..., lat: _Optional[int] = ...) -> None: ...

class LineString(_message.Message):
    __slots__ = ("lat", "lon")
    LAT_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    lat: _containers.RepeatedScalarFieldContainer[int]
    lon: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, lat: _Optional[_Iterable[int]] = ..., lon: _Optional[_Iterable[int]] = ...) -> None: ...

class Polygon(_message.Message):
    __slots__ = ("lat", "lon")
    LAT_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    lat: _containers.RepeatedScalarFieldContainer[int]
    lon: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, lat: _Optional[_Iterable[int]] = ..., lon: _Optional[_Iterable[int]] = ...) -> None: ...

class LineStringPatch(_message.Message):
    __slots__ = ("index", "command", "vector")
    class Command(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        INSERT: _ClassVar[LineStringPatch.Command]
        DELETE: _ClassVar[LineStringPatch.Command]
        CHANGE: _ClassVar[LineStringPatch.Command]
    INSERT: LineStringPatch.Command
    DELETE: LineStringPatch.Command
    CHANGE: LineStringPatch.Command
    INDEX_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    index: _containers.RepeatedScalarFieldContainer[int]
    command: _containers.RepeatedScalarFieldContainer[LineStringPatch.Command]
    vector: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, index: _Optional[_Iterable[int]] = ..., command: _Optional[_Iterable[_Union[LineStringPatch.Command, str]]] = ..., vector: _Optional[_Iterable[_Union[Point, _Mapping]]] = ...) -> None: ...

class PropPatch(_message.Message):
    __slots__ = ("prop_delete", "prop_add", "prop_update")
    PROP_DELETE_FIELD_NUMBER: _ClassVar[int]
    PROP_ADD_FIELD_NUMBER: _ClassVar[int]
    PROP_UPDATE_FIELD_NUMBER: _ClassVar[int]
    prop_delete: PropDelete
    prop_add: PropAdd
    prop_update: PropUpdate
    def __init__(self, prop_delete: _Optional[_Union[PropDelete, _Mapping]] = ..., prop_add: _Optional[_Union[PropAdd, _Mapping]] = ..., prop_update: _Optional[_Union[PropUpdate, _Mapping]] = ...) -> None: ...

class PropDelete(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, key: _Optional[_Iterable[str]] = ...) -> None: ...

class PropAdd(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: _containers.RepeatedScalarFieldContainer[str]
    value: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, key: _Optional[_Iterable[str]] = ..., value: _Optional[_Iterable[str]] = ...) -> None: ...

class PropUpdate(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: _containers.RepeatedScalarFieldContainer[str]
    value: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, key: _Optional[_Iterable[str]] = ..., value: _Optional[_Iterable[str]] = ...) -> None: ...
