from __future__ import annotations


class CircularLinkedListIterator:
    def __init__(self, head) -> None:
        self.head = head
        self.current = head.right

    def __next__(self):
        if self.current != self.head:
            obj = self.current
            self.current = self.current.right
            return obj
        raise StopIteration

    def next(self):
        return self.__next__()
