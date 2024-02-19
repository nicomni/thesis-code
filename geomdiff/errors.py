from shapely.geometry.base import BaseGeometry


class GeometryTypeMismatchError(Exception):

    def __init__(self, geom1: BaseGeometry, geom2: BaseGeometry):
        self._geom1 = geom1
        self._geom2 = geom2
        super().__init__()


    def __str__(self):
        return f"Geometry type mismatch: {self._geom1.geom_type} != {self._geom2.geom_type}"


class UnexpectedEditCommandTypeError(Exception):
    _op: str

    def __init__(self, op: str):
        self._op = op
        super().__init__(op)

    def __str__(self):
        return f"Unexpected command type '{self._op}'. Expected 'insert' or 'delete'"
