from __future__ import annotations
from typing import Union, List, Tuple

from constraint import CellConstraint, RowConstraint, ColumnConstraint, BoxConstraint


class Direction:
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


class StorageObject:
    """
    Represents an abstract base class for any storage object in the
    Dancing Links algorithm.
    """
    __slots__ = ("column", "_identifier", "up", "down", "left", "right")

    def __init__(self,
                 column: ColumnObject,
                 identifier: Union[str, int],
                 up: StorageObject=None,
                 down: StorageObject=None,
                 left: StorageObject=None,
                 right: StorageObject=None) -> None:
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

    def iter(self, direction: str=Direction.RIGHT) -> StorageObject:
        """
        This more advanced iter function adds support for iterating in any direction.
        'right', 'left', 'up', 'down' are all valid kwargs for direction.
        Note: It is intended that is this called from the head node or a
        column object, because the node that you start on is not yielded.
        """
        current = getattr(self, direction)
        while current != self:
            yield current
            current = getattr(current, direction)

    def __iter__(self) -> StorageObject:
        """
        Python generators are notably faster than iterators.
        This is because generators implement the __next__ slot directly,
        rather than iterators which have to lookup the __next__ method from
        the __dict__ method. From my own tests, this is a speedup of
        roughly 60-70%. For this purpose, I will not actually be using
        the next() or __next__ functions defined below, and will be calling
        '.right' attribute directly to avoid this lookup.
        Note: It is intended that is this called from the head node, because
        the node that you start on is not yielded.
        """
        current = self.right
        while current != self:
            yield current
            current = current.right

    def __next__(self) -> StorageObject:
        return self.right

    def next(self) -> StorageObject:
        return self.__next__()


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

    def cover(self) -> None:
        """
        Removes the column from the linked list. It initially covers the
        column object node at the top of the matrix, followed by removing
        all rows which have a 1 present in this column. Rows can contain
        more than one 1 as we are satisfying 4 constraints, so it must also
        cover these columns.
        """
        self.right.left = self.left
        self.left.right = self.right
        for i in self.iter(Direction.DOWN):
            for j in i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1

    def uncover(self) -> None:
        """
        Does the exact opposite of cover (see above).
        """
        for i in self.iter(Direction.UP):
            for j in i.iter(Direction.LEFT):
                j.column.size += 1
                j.down.up = j
                j.up.down = j
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
