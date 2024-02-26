class GeometryTypeMismatchError(Exception):
    def __init__(self, geom_type_1: str, geom_type_2: str):
        self._gtype1 = geom_type_1
        self._gtype2 = geom_type_2
        super().__init__()

    def __str__(self):
        return f"Geometry type mismatch: {self._gtype1} != {self._gtype2}"


class UnexpectedEditCommandTypeError(Exception):
    _op: str

    def __init__(self, op: str):
        self._op = op
        super().__init__(op)

    def __str__(self):
        return f"Unexpected command type '{self._op}'. Expected 'insert' or 'delete'"
