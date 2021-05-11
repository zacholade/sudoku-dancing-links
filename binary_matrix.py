from __future__ import annotations

import numpy as np

from storage_object import ColumnObject, DataObject


class BinaryMatrix:
    def __init__(self, head: ColumnObject):
        self._head = head

    @property
    def head(self) -> ColumnObject:
        return self._head

    @classmethod
    def construct_from_np_array(cls, grid: np.array) -> BinaryMatrix:
        """
        Constructs the matrix and returns the root column.
        """
        # Create the root column
        head = ColumnObject('head')
        columns = []
        # We need 324 columns in the binary matrix to satisfy all the
        # constraints Sudoku imposes. Cell, row, column and grid constraints.
        # 324 = (9x9) + (9x9) + (9x9) + (9x9).
        # for loop makes columns from left to right with h on the far left.
        for identifier in range(324):
            column = ColumnObject(identifier)
            # The last column should wrap back to the root (as per circular
            # doubly linked list). So we can set right to head.
            column.right = head
            # Likewise with the last column
            column.left = head.left
            head.left.right = column  # head.left.right is the previously made column.
            # Lastly make it loop to the left also.
            head.left = column
            columns.append(column)

        # Now we need to loop over every grid position in the np array and
        # determine if it provides a clue. What we do is determined by whether this
        # clue is present or not. Explained below.
        for x, y in ((x, y) for x in range(9) for y in range(9)):
            if grid[x][y] != 0:
                # We have been given a clue so must hold this value! No need to
                # create 9 rows for each possible solution like we do below as the
                # solution is already provided.
                sub_row = grid[x][y] - 1
                DataObject.with_constraints(x, y, sub_row, columns)
            else:
                # We don't know what is in this cell so we need to create
                # 9 new rows for each of the possible solutions for this cell.
                for sub_row in range(9):
                    DataObject.with_constraints(x, y, sub_row, columns)

        return cls(head)

    def get_smallest_column(self) -> ColumnObject:
        """
        Donald Knuth argues that to minimise the branching factor, we should
        choose the column with the fewest number of 1's occurring in it.
        """
        min_col = None
        min_value = 325  # Max number of columns + 1.
        for col in self.head:
            size = col.size
            if size < min_value:
                if size <= 1:
                    return col
                min_value = size
                min_col = col
        return min_col
