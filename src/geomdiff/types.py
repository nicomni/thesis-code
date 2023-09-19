from typing import Literal, Sequence, TypeGuard

Point = tuple[float, float]
InsertCommand = tuple[int, Literal["insert"], Point]  # (0, 'insert', (1,1))
DeleteCommand = tuple[int, Literal["delete"]]  # (2, 'delete')
ChangeCommand = tuple[int, Literal["change"], Point]  # (1, 'change', (3,3))
EditCommand = InsertCommand | DeleteCommand
PatchCommand = EditCommand | ChangeCommand
EditScript = Sequence[EditCommand]
Patch = Sequence[PatchCommand]
PointSequence = Sequence[Point]


def is_insert_command(cmd) -> TypeGuard[InsertCommand]:
    if isinstance(cmd, tuple) and len(cmd) == 3:
        op = cmd[1]
        return op == "insert"
    return False


def is_delete_command(cmd) -> TypeGuard[DeleteCommand]:
    if isinstance(cmd, tuple) and len(cmd) == 2:
        op = cmd[1]
        return op == "delete"
    return False


def is_change_command(cmd: PatchCommand) -> TypeGuard[ChangeCommand]:
    op = cmd[1]
    if op == "change":
        return True
    return False


def is_point_type(val: object) -> TypeGuard[Point]:
    return (
        isinstance(val, tuple)
        and len(val) == 2
        and all(isinstance(x, float) for x in val)
    )


def is_point_sequence(seq: list) -> TypeGuard[PointSequence]:
    return all(is_point_type(x) for x in seq)


def is_valid_edit_command(cmd) -> TypeGuard[EditCommand]:
    if isinstance(cmd, tuple) and 2 <= len(cmd) <= 3:
        return is_insert_command(cmd) or is_delete_command(cmd)
    return False


class UnexpectedEditCommandTypeError(Exception):
    _op: str

    def __init__(self, op: str):
        self._op = op
        super().__init__(op)

    def __str__(self):
        return f"Unexpected command type '{self._op}'. Expected 'insert' or 'delete'"
