from typing import Union

from storage_object.storage_object import StorageObject, Direction


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
