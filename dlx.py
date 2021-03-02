from typing import Callable, List, Union
import numpy as np
import abc

def solution_found_callback(s: List):
    print("SOLUTION FOUND OMG!")
    rows = []
    for k in s:
        rows.append(k.identifier)
    rows.sort()

    grid = []
    for row in rows:
        grid.append(row % 9 + 1)

    print(np.array(grid).reshape(9,9))
    print('---------------------')



class StorageObject:
    """
    Represents an abstract base class for any storage object in the
    Dancing Links algorithm.
    """
    def __init__(self, c: "ColumnObject", identifier: Union[str, int], u=None, d=None, l=None, r=None):
        self.identifier = identifier
        self.c = c

        # Link to the other cells containing a 1 in 4 orthogonal positions:
        # up, down, left, and right.
        # Any link that has no corresponding 1 instead will link to itself.
        # We therefore initialise these values as just that and will link
        # them later on.
        self.u = u if u else self
        self.d = d if d else self
        self.l = l if l else self
        self.r = r if r else self

    @property
    def identifier(self) -> Union[str, int]:
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: Union[str, int]):
        self._identifier = identifier


class ColumnObject(StorageObject):
    """
    Represents a column in the binary matrix used in DL.
    """
    def __init__(self, identifier: Union[str, int]):
        super().__init__(self, identifier)
        # The column size is initialised with 0. We increment this
        # inside of DataObject class __init__ upon creation.
        self.s = 0

    def cover(self) -> None:
        self.r.l = self.l
        self.l.r = self.r
        i = self.d
        while i != self:
            j = i.r
            while j != i:
                j.d.u = j.u
                j.u.d = j.d
                j.c.s -= 1
                j = j.r
            i = i.d

    def uncover(self) -> None:
        i = self.u
        while i != self:
            j = i.l
            while j != i:
                j.c.s += 1
                j.d.u = j
                j.u.d = j
                j = j.l
            i = i.u
        self.r.l = self
        self.l.r = self

class DataObject(StorageObject):
    """
    Represents a given data object for use in the Dancing Links algorithm.
    Donald Knuth refers to any cell in the binary matrix with a value of 1
    as "Data Objects".
    """
    def __init__(self, c: ColumnObject, identifier: Union[str, int]):
        super().__init__(c, identifier)

    def link_rows(self):
        c = self.c
        c.s += 1
        # make the last data object wrap to the column object.
        self.d = c
        # Now we can swap the previous last data object with this data object.
        self.u = c.u
        c.u.d = c.u = self

    def unlink(self):
        ...

class Constraint:
    @property
    @abc.abstractmethod
    def _offset(self) -> int:
        """
        Offset to the constraint. Sudoku can be broken into
        4 constraints. Each of these constraints will need 81
        columns. 81x4 = 324 columns in total. Offset will therefore
        be a multiple of 81.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def column_num(x: int, y: int, sub_row: int) -> int:
        pass


class CellConstraint(Constraint):
    _offset = 0

    @staticmethod
    def column_num(x: int, y: int, sub_row: int) -> int:
        return CellConstraint._offset + (x * 9) + y


class RowConstraint(Constraint):
    _offset = 81

    @staticmethod
    def column_num(x: int, y: int, sub_row: int) -> int:
        return RowConstraint._offset + (x * 9) + sub_row


class ColumnConstraint(Constraint):
    _offset = 162

    @staticmethod
    def column_num(x: int, y: int, sub_row: int) -> int:
        return ColumnConstraint._offset + (y * 9) + sub_row


class BoxConstraint(Constraint):
    _offset = 243

    @staticmethod
    def column_num(x: int, y: int, sub_row: int) -> int:
        return BoxConstraint._offset + (3 * (x // 3) + y // 3) * 9 + sub_row


class MatrixUtility:
    @classmethod
    def construct_from_np_array(cls, grid: np.array) -> ColumnObject:
        """
        Constructs the matrix and returns the root column.
        """
        # Create the root column
        h = ColumnObject('h')
        columns = []
        # We need 324 columns in the binary matrix to satisfy all the
        # constraints Sudoku imposes. Cell, row, column and grid constraints.
        # 324 = (9x9) + (9x9) + (9x9) + (9x9).
        # for loop makes columns from left to right with h on the far left.
        for identifier in range(324):
            c = ColumnObject(identifier)
            # The last column should wrap back to the root (as per circular
            # doubly linked list). So we can set R to h.
            c.r = h
            # Likewise with the last column
            c.l = h.l
            h.l.r = c  # h.L.R is the previously made column.
            # Lastly make it loop to the left also.
            h.l = c
            columns.append(c)

        cls._build_constraints(grid, columns)
        return h

    @staticmethod
    def _link(x, y, sub_row, columns: List[ColumnObject]):
        # Ensures each row has a unique identifier.
        row_num = 81 * x + 9 * y + sub_row
        # Create the constraints
        cell_constraint = DataObject(
            # Get the column by indexing our columns list with the constraint offset.
            columns[CellConstraint.column_num(x, y, sub_row)],
            # set the id equal to the row num
            row_num
        )
        row_constraint = DataObject(
            columns[RowConstraint.column_num(x, y, sub_row)],
            row_num
        )
        col_constraint = DataObject(
            columns[ColumnConstraint.column_num(x, y, sub_row)],
            row_num
        )
        box_constraint = DataObject(
            columns[BoxConstraint.column_num(x, y, sub_row)],
            row_num
        )

        # Link the rows together as they are part of one big matrix.
        # Order that these 4 constraints take place in this matrix does not
        # matter. For legibility sake, they will retain the order defined above.
        # Cell constraint on the far left .. to box constraint on the far right.
        cell_constraint.r = col_constraint.l = row_constraint
        row_constraint.r = box_constraint.l = col_constraint
        col_constraint.r = cell_constraint.l = box_constraint
        box_constraint.r = row_constraint.l = cell_constraint

        # Link each row to the column
        for d in (cell_constraint, row_constraint, col_constraint, box_constraint):
            d.link_rows()

    @staticmethod
    def _build_constraints(grid: np.array, columns: List[ColumnObject]):
        for x, y in ((x, y) for x in range(9) for y in range(9)):
            if grid[x][y] != 0:
                # We have been given a clue so must hold this value! No need to
                # create 9 rows for each solution like we did above.
                sub_row = grid[x][y] - 1
                MatrixUtility._link(x, y, sub_row, columns)
            else:
                # We don't know what is in this cell so we need to create
                # 9 new rows for each of the possible solutions for this cell.
                for sub_row in range(9):
                    MatrixUtility._link(x, y, sub_row, columns)


class DLX:
    """
    Implements the Dancing Links algorithm.
    We will be breaking down the sudoku problem into 4 constraints
    and illustrate them in a cover problem using Donald Knuth's
    """
    def __init__(self, grid: np.array, callback: Callable) -> None:
        """
        :param h: The root column object
        :param callback: A callback to call with the solution when found.
        """
        self._callback = callback
        self.h = MatrixUtility.construct_from_np_array(grid)

    def solve(self) -> None:
        # First time we call search, call it with an empty list.
        self._search([])

    def _search(self, s: List[DataObject]):
        if self.h.r == self.h:
            self._callback(s)
            return

        c = self._choose_column_object()
        c.cover()
        r = c.d
        while r != c:
            s.append(r)
            j = r.r
            while j != r:
                j.c.cover()
                j = j.r
            self._search(s)
            r = s.pop()
            c = r.c
            j = r.l
            while j != r:
                j.c.uncover()
                j = j.l
            r = r.d
        c.uncover()
        return

    def _choose_column_object(self):
        """
        Donald Knuth argues that to minimise the branching factor, we should
        choose the column with the fewest number of 1's occurring in it.
        """
        s = np.inf
        cur = self.h.r
        col = None
        while cur != self.h:
            if cur.s < s:
                s = cur.s
                col = cur
            cur = cur.r
        return col


if __name__ == "__main__":
    # Load sudokus
    sudokus = np.load("data/very_easy_puzzle.npy")
    print("very_easy_puzzle.npy has been loaded into the variable sudoku")
    print(f"sudoku.shape: {sudokus.shape}, sudoku[0].shape: {sudokus[0].shape}, sudoku.dtype: {sudokus.dtype}")

    # Load solutions for demonstration
    solutions = np.load("data/very_easy_solution.npy")
    print()

    for i, sudoku in enumerate(sudokus):
        # Print the first 9x9 sudoku...
        print("First sudoku:")
        print(sudoku, "\n")

        # ...and its solution
        print("Solution of first sudoku:")
        print(solutions[i])

        dlx = DLX(sudoku, solution_found_callback)
        dlx.solve()