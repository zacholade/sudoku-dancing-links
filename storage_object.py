from __future__ import annotations
from typing import Union, List, Tuple, Iterable

from constraint import CellConstraint, RowConstraint, ColumnConstraint, BoxConstraint
from utility import CircularLinkedListIterator


class StorageObject:
    """
    Represents an abstract base class for any storage object in the
    Dancing Links algorithm.
    """
    __slots__ = ("column", "_identifier", "up", "down", "left", "right")

    def __init__(self,
                 column: ColumnObject,
                 identifier: Union[str, int],
                 up=None,
                 down=None,
                 left=None,
                 right=None) -> None:
        self.identifier = identifier
        self.column = column

        # Link to the other cells containing a 1 in 4 orthogonal positions:
        # up, down, left, and right.
        # Any link that has no corresponding 1 instead will link to itself.
        # We therefore initialise these values as just that and will link
        # them later on.
        self.up = up if up else self
        self.down = down if down else self
        self.left = left if left else self
        self.right = right if right else self

    @property
    def identifier(self) -> Union[str, int]:
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: Union[str, int]):
        self._identifier = identifier


class ColumnObject(StorageObject):
    """
    Represents a column in the binary matrix used in DLX.
    """
    __slots__ = ("size",)

    def __init__(self, identifier: Union[str, int]):
        super().__init__(self, identifier)
        # The column size is initialised with 0. We increment this
        # inside of DataObject class __init__ upon creation.
        self.size = 0

    def __iter__(self) -> CircularLinkedListIterator:
        return CircularLinkedListIterator(self)

    def cover(self) -> None:
        self.right.left = self.left
        self.left.right = self.right
        i = self.down
        while i != self:
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1
                j = j.right
            i = i.down

    def uncover(self) -> None:
        i = self.up
        while i != self:
            j = i.left
            while j != i:
                j.column.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        self.right.left = self.left.right = self


class DataObject(StorageObject):
    """
    Represents a given data object for use in the Dancing Links algorithm.
    Donald Knuth refers to any cell in the binary matrix with a value of 1
    as "Data Objects".
    """
    def __init__(self, column: ColumnObject, identifier: Union[str, int]) -> None:
        super().__init__(column, identifier, down=column, up=column.up)
        # New data object in column. Increase the size.
        self.column.size += 1
        self.column.up.down = self.column.up = self

    @classmethod
    def with_constraints(cls,
                         x: int,
                         y: int,
                         sub_row: int,
                         columns: List[ColumnObject]) -> \
            Tuple[DataObject, DataObject, DataObject, DataObject]:
        """
        A class method which creates four data objects for the given position
        in the 9x9 sudoku grid. Each data object satisfies a different constraint.
        Afterwards we link the columns/rows together to form a circular doubly
        linked list.
        """
        row_num = 81 * x + 9 * y + sub_row
        cel = cls(columns[CellConstraint.column_num(x, y, sub_row)], row_num)
        row = cls(columns[RowConstraint.column_num(x, y, sub_row)], row_num)
        col = cls(columns[ColumnConstraint.column_num(x, y, sub_row)], row_num)
        box = cls(columns[BoxConstraint.column_num(x, y, sub_row)], row_num)

        # Link the rows together as they are part of one big matrix.
        # Order that these 4 constraints take place in this matrix does not
        # matter. For legibility sake, they will retain the order defined above.
        # Cell constraint on the far left .. to box constraint on the far right.
        cel.right = col.left = row
        row.right = box.left = col
        col.right = cel.left = box
        box.right = row.left = cel
        return cel, row, col, box
