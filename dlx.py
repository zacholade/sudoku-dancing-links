from __future__ import annotations
from typing import List
import numpy as np

from storage_object import ColumnObject, DataObject, Direction, StorageObject
from matrix import Matrix


class DLX:
    """
    Implements the Dancing Links algorithm.
    We will be breaking down the sudoku problem into 4 constraints
    and illustrate them in a cover problem using Donald Knuth's
    """
    def __init__(self, grid: np.array) -> None:
        self.head = Matrix.construct_from_np_array(grid)
        self._solution = []  # type: List[StorageObject]

    def get_solution(self) -> np.array:
        if self._solution:
            solution_rows = [row.identifier for row in self._solution]
            solution_rows.sort()
            solution_grid = [row % 9 + 1 for row in solution_rows]
            solved_sudoku = np.array(solution_grid).reshape(9, 9)
            return solved_sudoku
        # There was no solution. Return array of -1's
        return np.full((9, 9), -1)

    def solve(self) -> List[StorageObject]:
        # First time we call search, call it with an empty list.
        self._search([])
        return self.get_solution()

    def _search(self, solution: List[StorageObject]) -> None:
        if self.head.right == self.head:
            # No more columns present. Solution found!
            # Make a copy or else garbage collection deletes solution...
            self._solution = solution.copy()
            return

        # Choose the column with the least number of data objects.
        column = self._choose_column_object()
        column.cover()

        for r in column.iter(Direction.DOWN):
            # Once covering the column, append all data objects in that
            # column to the solutions.
            solution.append(r)
            for j in r:
                j.column.cover()

            # Recurse until solution is found (no more columns) or
            # until we hit a dead end.
            self._search(solution)
            # We hit a dead end with that column, backtracking started.
            r = solution.pop()

            column = r.column
            for j in r.iter(Direction.LEFT):
                # backtracking involves uncovering all columns that we covered.
                j.column.uncover()

        column.uncover()
        return

    def _choose_column_object(self) -> ColumnObject:
        """
        Donald Knuth argues that to minimise the branching factor, we should
        choose the column with the fewest number of 1's occurring in it.
        """
        min_col = None
        min_value = np.inf
        for col in self.head:
            size = col.size
            if size < min_value:
                if size == 0:
                    return col
                min_value = size
                min_col = col
        return min_col


def sudoku_solver(sudoku: np.array) -> np.array:
    """
    Solves a Sudoku puzzle and returns its unique solution.

    Input
        sudoku : 9x9 numpy array
            Empty cells are designated by 0.

    Output
        9x9 numpy array of integers
            It contains the solution, if there is one. If there is no solution, all array entries should be -1.
    """
    dlx = DLX(sudoku)
    dlx.solve()
    solution = dlx.get_solution()
    return solution


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
            your_solution = sudoku_solver(sudoku)
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

        print(f"{count}/{len(sudokus)} {difficulty} sudokus correct")
        if count < len(sudokus):
            break
        print(f"It took {total_time}s to complete all 60 sudoku's.")
