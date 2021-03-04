from abc import abstractmethod


class Constraint:
    @property
    @abstractmethod
    def _offset(self) -> int:
        """
        Offset to the constraint. Sudoku can be broken into
        4 constraints. Each of these constraints will need 81
        columns. 81x4 = 324 columns in total. Offset will therefore
        be a multiple of 81.
        """
        ...

    @staticmethod
    @abstractmethod
    def column_num(x: int, y: int, sub_row: int) -> int:
        ...


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
