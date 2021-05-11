from __future__ import annotations

from abc import abstractmethod
from typing import Union, List, Tuple

from constraint import CellConstraint, RowConstraint, ColumnConstraint, BoxConstraint


class Direction:
    """
    Can be passed as a direction to the StorageObject.iter() function to
    specify which way to iterate across the circular doubly linked list.
    """
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


class StorageObject:
    """
    Represents an abstract base class for any storage object in the
    Dancing Links algorithm.
    """
    __slots__ = ("column", "identifier", "up", "down", "left", "right")

    def __init__(self,
                 column: ColumnObject,
                 identifier: Union[str, int],
                 up: StorageObject = None,
                 down: StorageObject = None,
                 left: StorageObject = None,
                 right: StorageObject = None) -> None:
        self.identifier = identifier
        self.column = column

        # Link to the other cells containing a 1 in 4 orthogonal positions:
        # up, down, left, and right. Any link that has no corresponding 1
        # instead will link to itself. We therefore initialise these values
        # as just that and will link them later on.
        self.up = up if up else self
        self.down = down if down else self
        self.left = left if left else self
        self.right = right if right else self

    def iter(self, direction: str = Direction.RIGHT) -> StorageObject:
        """
        This more advanced iter function adds support for iterating in any direction.
        'right', 'left', 'up', 'down' are all valid kwargs for direction.
        Note: It is intended that is this called from the head node or a
        column object, because the node that you start on is not yielded.
        """
        current = self
        while (current := getattr(current, direction)) is not self:
            yield current

    def __iter__(self) -> StorageObject:
        """
        Python generators are notably faster than iterators.
        This is because generators implement the __next__ slot directly,
        rather than iterators which have to lookup the __next__ method from
        the class's __dict__. From my own tests, this is a speedup of
        roughly 60-70%. For this purpose, I will not actually be using
        the next() or __next__ functions defined below, and will be calling
        '.right' attribute directly to avoid this lookup.
        Note: It is intended that is this called from the head node, because
        the node that you start on is not yielded.
        """
        current = self
        while (current := current.right) is not self:
            yield current

    def __next__(self) -> StorageObject:
        return self.right

    def next(self) -> StorageObject:
        return self.__next__()

    @abstractmethod
    def cover(self):
        ...

    @abstractmethod
    def uncover(self):
        ...


class ColumnObject(StorageObject):
    """
    Represents a column in the binary matrix used in DLX.
    """
    __slots__ = "size"

    def __init__(self, identifier: Union[str, int]):
        super().__init__(self, identifier)
        # The column size is initialised with 0. We increment this
        # inside of DataObject class __init__ upon creation.
        self.size = 0

    def cover(self):
        """
        Removes the column from the linked list. It initially covers the
        column object node at the top of the matrix, followed by removing
        all rows which have a 1 present in this column. Rows can contain
        more than one 1 as we are satisfying 4 constraints, so it must also
        cover these columns.
        """
        self.right.left = self.left
        self.left.right = self.right
        for row in self.iter(Direction.DOWN):
            for data_object in row:
                data_object.cover()

    def uncover(self):
        """
        Does the exact opposite of cover (see above).
        """
        for row in self.iter(Direction.UP):
            for data_object in row.iter(Direction.LEFT):
                data_object.uncover()
        self.right.left = self.left.right = self


class DataObject(StorageObject):
    """
    Represents a given data object for use in the Dancing Links algorithm.
    Donald Knuth refers to any cell in the binary matrix with a value of 1
    as "Data Objects".
    """
    def __init__(self, column: ColumnObject, identifier: Union[str, int]):
        super().__init__(column, identifier, down=column, up=column.up)
        # New data object in column. Essentially the same as uncovering which
        # increments the column's size and links it to adjacent nodes.
        self.uncover()

    @classmethod
    def with_constraints(cls,
                         x: int,
                         y: int,
                         sub_row: int,
                         columns: list[ColumnObject]) -> Tuple[DataObject, DataObject, DataObject, DataObject]:
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

    def cover(self):
        self.down.up = self.up
        self.up.down = self.down
        self.column.size -= 1

    def uncover(self):
        self.column.size += 1
        self.down.up = self.up.down = self
