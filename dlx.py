from __future__ import annotations

from typing import List

import numpy as np

from binary_matrix import BinaryMatrix
from storage_object import ColumnObject, Direction, StorageObject


class DLX:
    """
    Implements the Dancing Links algorithm.
    We will be breaking down the sudoku problem into 4 constraints
    and illustrate them in a cover problem using Donald Knuth's
    """
    def __init__(self, grid: np.array):
        self.head = BinaryMatrix.construct_from_np_array(grid)
        self._solution: List[StorageObject] = []

    def solve(self) -> np.ndarray[int]:
        # First time we call search, call it with an empty list.
        self._search([])
        return self._format_solution()

    def _format_solution(self) -> np.ndarray[int]:
        """
        We know that the solution list contains 81 data objects.
        One for each cell in the sudoku puzzle, whereby each data object will contain
        an integer identifier as per the DLX algorithm. The solution list is first sorted
        by this integer identifier in descending order. Due to the domain of a 9x9 sudoku
        puzzle being 9, I was then able to take the modulus of 9 for each row once
        zero-based indices were corrected for (by adding one).
        """
        return np.array([d % 9 + 1 for d in
                        sorted([r.identifier for r in self._solution])]
                        ).reshape(9, 9) if self._solution else np.full((9, 9), -1)

    def _search(self, solution: List[StorageObject]) -> None:
        if self.head.right == self.head:
            # No more columns present. Solution found!
            self._solution = solution
            return

        # Choose the column with the least number of data objects.
        column = self._choose_column_object()
        column.cover()

        for row in column.iter(Direction.DOWN):
            # Once covering the column, append all data objects in that
            # column to the solutions.
            solution.append(row)
            for data_object in row:
                data_object.column.cover()

            # Recurse until solution is found (no more columns) or
            # until we hit a dead end.
            self._search(solution)

            if self.head.right == self.head:
                # This is an optimisation I found that speeds up the algorithm by ~22%
                # If we add an additional check here for if the solution has been found
                # we don't waste time backtracking as we exit out of the recursion!
                return

            # We hit a dead end with that column, backtracking started.
            row = solution.pop()
            column = row.column

            for data_object in row.iter(Direction.LEFT):
                # backtracking involves uncovering the columns that we covered.
                data_object.column.uncover()

        column.uncover()

    def _choose_column_object(self) -> ColumnObject:
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


if __name__ == "__main__":
    import time
    difficulties = ['very_easy', 'easy', 'medium', 'hard']
    total_time = 0
    for difficulty in difficulties:
        print(f"Testing {difficulty} sudokus")

        sudokus = np.load(f"data/{difficulty}_puzzle.npy")
        solutions = np.load(f"data/{difficulty}_solution.npy")
        count = 0
        for i in range(len(sudokus)):
            sudoku = sudokus[i].copy()
            print(f"This is {difficulty} sudoku number", i)
            print(sudoku)

            start_time = time.process_time()
            your_solution = DLX(sudoku).solve()
            end_time = time.process_time()
            total_time += (end_time - start_time)

            print(f"This is your solution for {difficulty} sudoku number", i)
            print(your_solution)

            print("Is your solution correct?")
            if np.array_equal(your_solution, solutions[i]):
                print("Yes! Correct solution.")
                count += 1
            else:
                print("No, the correct solution is:")
                print(solutions[i])

            print("This sudoku took", end_time - start_time, "seconds to solve.\n")

        print(f"{count}/{len(sudokus)} {difficulty} sudokus correct\n")
        if count < len(sudokus):
            break
        print(f"It took {total_time}s to complete all 60 sudoku's.")
