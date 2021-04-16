from __future__ import annotations

from abc import abstractmethod
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from storage_object import ColumnObject


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
    def cover(self) -> None:
        ...

    @abstractmethod
    def uncover(self) -> None:
        ...
