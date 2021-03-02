from typing import Callable, List, Union, Tuple
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


class StorageObject:
    """
    Represents an abstract base class for any storage object in the
    Dancing Links algorithm.
    """
    def __init__(self,
                 column: "ColumnObject",
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
    def __init__(self, identifier: Union[str, int]):
        super().__init__(self, identifier)
        # The column size is initialised with 0. We increment this
        # inside of DataObject class __init__ upon creation.
        self.size = 0

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
        self.right.left = self
        self.left.right = self


class DataObject(StorageObject):
    """
    Represents a given data object for use in the Dancing Links algorithm.
    Donald Knuth refers to any cell in the binary matrix with a value of 1
    as "Data Objects".
    """
    def __init__(self, column: ColumnObject, identifier: Union[str, int]):
        super().__init__(column, identifier)
        # New data object in column. Increase the size.
        self.column.size += 1

        # Following lines Link each row to the column in a circular linked list fashion.
        # Make the last data object wrap to the column object.
        self.down = self.column
        # Now we can swap the previous last data object with this data object.
        self.up = self.column.up
        self.column.up.down = self.column.up = self

    @classmethod
    def with_constraints(cls,
                         x: int,
                         y: int,
                         sub_row: int,
                         columns: List[ColumnObject]) -> \
            Tuple["DataObject", "DataObject", "DataObject", "DataObject"]:
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


class MatrixUtility:
    @classmethod
    def construct_from_np_array(cls, grid: np.array) -> ColumnObject:
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
            # doubly linked list). So we can set R to h.
            column.right = head
            # Likewise with the last column
            column.left = head.left
            head.left.right = column  # h.L.R is the previously made column.
            # Lastly make it loop to the left also.
            head.left = column
            columns.append(column)

        # Now we need to loop over every grid position in the np array and
        # determine if it provides a clue. What we do is determined by where this
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
        return head


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
        self.head = MatrixUtility.construct_from_np_array(grid)

    def solve(self) -> None:
        # First time we call search, call it with an empty list.
        self._search([])

    def _search(self, solution: List[DataObject]):
        if self.head.right == self.head:
            self._callback(solution)
            return

        column = self._choose_column_object()
        column.cover()
        r = column.down
        while r != column:
            solution.append(r)
            j = r.right
            while j != r:
                j.column.cover()
                j = j.right
            self._search(solution)
            r = solution.pop()
            column = r.column
            j = r.left
            while j != r:
                j.column.uncover()
                j = j.left
            r = r.down
        column.uncover()
        return

    def _choose_column_object(self):
        """
        Donald Knuth argues that to minimise the branching factor, we should
        choose the column with the fewest number of 1's occurring in it.
        """
        size = np.inf
        current = self.head.right
        column = None
        while current != self.head:
            if current.size < size:
                size = current.size
                column = current
            current = current.right
        return column


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
