from typing import Callable
import numpy

def solution_found_callback():
    print("SOLUTION FOUND OMG!")


class ABCStorageObject:
    """
    Represents an abstract base class for any storage object in the
    Dancing Links algorithm.
    """
    def __init__(self, c_id: str):
        self.c_id = c_id

    @property
    def c_id(self) -> str:
        return self._c_id

    @c_id.setter
    def c_id(self, c_id: str):
        self._c_id = c_id


class ColumnObject(ABCStorageObject):
    """
    Represents a column in the binary matrix used in DL.
    """
    def __init__(self, c_id: str):
        super().__init__(c_id)

        self.s = 0  # The column size.

        # Columns to the left and right of this one.
        # We do this initialisation in the DL class.
        self.l = self
        self.r = self


class DataObject(ABCStorageObject):
    """
    Represents a given data object for use in the Dancing Links algorithm.
    Donald Knuth refers to any cell in the binary matrix with a value of 1
    as "Data Objects".
    """
    def __init__(self, c: ColumnObject, c_id: str):
        super().__init__(c_id)
        self.c = c

        # Increment the column size by 1 each time we make a new
        # data object for that column
        self.c.s += 1

        # Link to the other cells containing a 1 in 4 orthogonal positions:
        # up, down, left, and right.
        # Any link that has no corresponding 1 instead will link to itself.
        # We therefore initialise these values as just that and will link
        # them later on.
        self.u = self
        self.d = self
        self.l = self
        self.r = self


class DL:
    """Implements the Dancing Links algorithm"""
    def __init__(self, h: ColumnObject, callback: Callable):
        """
        :param h: The root column object
        :param callback: A callback to call with the solution when found.
        """
        self.h = h
        self._callback = callback

    @classmethod
    def from_np_array(cls, grid: numpy.array, callback):
        columns = []
        # Create the root column
        h = ColumnObject('h')
        # We need 324 columns in the binary matrix to satisfy all the
        # constraints sodoku imposes. Cell, row, column and grid constraints.
        # 324 = (9x9) + (9x9) + (9x9) + (9x9).
        # These columns will be made from left to right with h on the far left.
        for c_id in range(324):
            c = ColumnObject(str(c_id))
            # The last column should wrap back to the root (as per circular
            # doubly linked list). So we can set R to h.
            c.R = h
            # Likewise with the last column
            c.L = h.L
            h.L.R = c  # h.L.R is the previously made column.
            # Lastly make it loop to the left also.
            h.L = c

            columns.append(c)

        # Define our constraints


        return cls(h, callback)

    def search(self, s):
        # TODO add typing hint for s
        if self.h.r == self.h:
            self._callback()
            return
