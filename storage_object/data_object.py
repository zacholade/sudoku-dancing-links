from __future__ import annotations

from typing import Union, List, Tuple

from constraint import CellConstraint, RowConstraint, ColumnConstraint, BoxConstraint
from storage_object.column_object import ColumnObject
from storage_object.storage_object import StorageObject


class DataObject(StorageObject):
    """
    Represents a given data object for use in the Dancing Links algorithm.
    Donald Knuth refers to any cell in the binary matrix with a value of 1
    as "Data Objects".
    """
    def __init__(self, column: ColumnObject, identifier: Union[str, int]) -> None:
        super().__init__(column, identifier, down=column, up=column.up)
        # New data object in column. Essentially the same as uncovering which
        # increments the column's size and links it to adjacent nodes.
        self.uncover()

    @classmethod
    def with_constraints(cls,
                         x: int,
                         y: int,
                         sub_row: int,
                         columns: List[ColumnObject]) -> Tuple[DataObject, DataObject, DataObject, DataObject]:
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
