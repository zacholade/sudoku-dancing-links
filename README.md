# Dancing Links (DLX) - Solving Sudoku
A Pythonic implementation of the DLX algorithm to 9x9 Sudoku puzzles.

By wrapping the while loops outlined in Donald Knuth's DLX algorithm inside a Python `__iter__()` function, iteration in all directions over a circular doubly linked list can be achieved as follows:

```py
for node in storage_object.iter(direction: Direction):
    ...
```

This abstraction considerably improves legibility of the algorithm, particularly in the [search function](https://github.com/zacholade/sudoku-dancing-links/blob/master/dlx.py#L39).

Can solve the 60 test puzzles of varying difficulty found in the [data directory](https://github.com/zacholade/sudoku-dancing-links/tree/master/data), in approximately 0.17 seconds. Requires Python > 3.9 to run.

## Background
One approach to solving a sudoku puzzle involves a standard depth-first search algorithm, which has a time complexity of O(n^2), where n is both the size of the square grid and number of possible numbers a cell can hold. This approach would be highly achievable due to it being covered in the unit material and can be paired with constraint satisfaction. However, after further research, I discovered that it is possible for sudoku of a fixed nxn size to be solved in O(1) time. NP completeness is a concept which applies to any decision-based problem that has a variable input size (Johnson, D. 1985). Should the input size, n not be fixed, the time complexity would be O(n) (NP complete), because it could hold a value up to infinity. In this case, the algorithm would spend O(n) time simply reading the input as it can't expect what size the grid will be beforehand. 

In terms of sudoku, NP-completeness is achievable because any sudoku is reducible to the exact cover problem; an algorithm which is known to be NP complete (Knuth et al., 2000). The exact cover problem is a type of constraint satisfaction problem and can be represented visually using a binary sparse matrix. In this binary sparse matrix, the columns represent constraints and rows represent possible values. A '1' present in any given intersection represents an incidence relation (the constraint is satisfied for that possible value), and a 0 otherwise. Donald Knuth refers to these 1's as *data objects*, and it should be noted that each row will contain only a single *data object* for each constraint range. 

## Dancing Links
One very efficient way of finding all solutions to the exact cover problem is by using Algorithm X. Algorithm X is a recursive, nondeterministic algorithm that utilizes depth-first search to support backtracking. It is referred to as DLX when efficiently implemented using the Dancing Links technique (Knuth et al., 2000). DLX was originally invented by Hiroshi Hitotsumatsu and Kohei Noshita, but later popularised by Donald Knuth and is a technique that can be used to undo the operation of removing a given node from a circular doubly linked list. See the example code below for a basic overview of how this works. In the case of DLX, each column also has a special column node at the top of every column. This column  node contains identifying information for the column, including its size (the number of *data objects*) and are referred to as a *column objects*. Additionally, there is also a head node prepending the first *column object* which can be used to enter the circular doubly linked list.

```python
# Where foo represents a node in a circular doubly linked list and the left
# and right attributes refer to the nodes to the left and right of foo.

# These two lines will remove foo from the doubly linked list.
foo.right.left = foo.left
foo.left.right = foo.right

# These two lines will restore foo's position in the list.
# Even though foo's reference was removed from its neighbour's above,
# we are able to restore its position in the list because foo retained
# which neighbours were to its left and right.
foo.right.left = foo.left.right = foo
```

## Reduction of Sudoku to the Exact Cover Problem
To reduce a 9x9 sudoku to the exact cover problem, it is important to understand how the rules of sudoku can be described in terms of 4 constraints (Laestander, M, 2014):
- **Cell Constraint:** A Cell can contain one integer from 1-9.
- **Row Constraint:** Each row must contain 9 unique integers from 1-9.
- **Column Constraint:** Each column must contain 9 unique integers from 1-9.
- **Box Constraint:** All 9 cells in a 3x3 box must contain 9 unique integers from 1-9.

With the above information, and given that there are 81 cells in a 9x9 sudoku puzzle, we can calculate that there will be a total of 81 x 4 = 324 columns in the binary sparse matrix. This is because all 81 cells will need to satisfy all 4 constraints. We also know there are 9 possible solutions (should there be no clue given) for each cell, so there can be up to 81 x 9 = 729 rows present. Each cell with a clue given will only add one row to the matrix due to it having only one possible value (the clue given). 

## Solving the Matrix (DLX)
Once these fundamentals have been understood, the way DLX can be applied to this cover problem is straightforward. The goal is to find a subset of 81 *data objects* that satisfy all constraints. To do this, we start searching recursively and choosing a *column object* to cover (remove from the linked list) and transfer its' *data objects* into a secondary solution list. The method for choosing this column is discussed below and is done by recursively calling the `search(solution: list[DataObject]) -> None` function, where solution is the solution list so far. Should the algorithm reach a dead end, it uses the principles of depth-first search and backtracks prior to trying a different *column object*. Once there are no more columns to cover, the solution has been found and lies in the solution list, which is then returned.

At this point, I found an optimisation in the algorithm that as far as I could tell, has not been covered in literature for this problem. In the recursive search function, right after we call search recursively, I found that implementing an additional closure statement: `if self.head.right == self.head: return`, speeds up the algorithm by roughly 22%. This is because it prevents the algorithm spending pointless time backtracking while traversing back up the call stack once a solution has already been found. A small but noticeable improvement.

## Choosing a Column to Cover
Within the search function uses the matrix interface to call `matrix.get_smallest_column() -> ColumnObject`, which returns a column object present in the M. The column this returns is then next in line to be covered (removed from the linked list). Donald Knuth proposes that there are two ways to go about implementing this function. It could either return the *column object* containing the least amount of *data objects*, or simply return the first *column object* following the head. Donald Knuth suggests that the former is worth the additional computation in order to minimise the branching factor, so this is the decision I made (Knuth et al., 2000). Through my own tests, the time saved when completing a single puzzle using the former often far exceeded 150 seconds.

Due to the nature of DLX being an unsorted circular doubly linked list, and the fact that columns are constantly changing in size as well as both being covered/uncovered repeatedly, implementing an efficient way to find the column of the smallest size is difficult. The partial selection sort algorithm takes O(n) time (Knuth, D. 1997; Wikipedia, 2021), and iterates over all items while constantly keeping track of the smallest value it has come across. Furthermore, if we know the smallest value that a list can hold, we have the additional choice of breaking out of the loop as soon as we come across it. In my case, this value is 0. However, when applied, I instead found that checking for a value <= 1 immediately after coming across it saved an additional 0.117s when completing the test puzzles. d.f. = 1000. This could be to numerous factors including the number of elements in the linked list and the frequency of 0's and 1's in the list.

## Translating Back to Sudoku
Once the DLX algorithm successfully halted in a solution found state, I was able to translate the obtained solution list back to a 9x9 array of values ranging from 1-9 relatively easily. We know that the solution list contains 81 *data objects*, one for each cell in the sudoku puzzle, whereby each *data object* will contain an integer identifier as per the DLX algorithm. The solution list is first sorted by this integer identifier in descending order. Due to the domain of a 9x9 sudoku puzzle being 9, I was then able to take the modulus of 9 for each row once zero-based indices were corrected for (by adding one). This was done for all 81 values such that the first value corresponded to cell 0 in the sudoku, followed by 1, 2, 3 ... 81-1 (Laestander, M, 2014).

## Implementation: Class Responsibilities
**DLX:** Keeps reference to the head node of the binary matrix and implements a `solve(sudoku: np.array) -> np.array` function; the point of entry for the DLX algorithm. This function calls the recursive `_search(solution: list[StorageObject]) -> list[StorageObject]` function which breaks out of recursion upon finding a solution or otherwise.

**Binary Matrix:** Implements a classmethod called `construct_from_np_array`, which is called by the `DLX` class to initialise the binary matrix (circular doubly linked list) from the 9x9 sudoku array.

**Constraint:** Serves as a constraint on the binary matrix. There are four sub classes for each of the four sudoku constraints discussed above. It allows us to calculate the column a given *data object* should exist in based off what sort of constraint that *data object* refers to.

**StorageObject:** Has two subclasses: **ColumnObject** and **DataObject**. Both subclasses implement a `cover() -> None` and `uncover() -> None` function that covers/uncovers itself from the circular doubly linked list. Holds reference to directly adjacent nodes in the up, down, left, and right positions. The `ColumnObject` class also keeps track of the number of *data objects* in its' column.


## References

Johnson, D.S. (1985) The NP-completeness column: an ongoing guide. *Journal of Algorithms*, 6(3), pp.434–451.

Knuth, D.E. (1997) The Art of Computer Programming, volumes 1, 2 and 3.

Knuth, D.E., Davies, J., Roscoe, B. and Woodcock, J. (2000) Dancing links. *Millenial Perspectives in Computer Science*, pp.187–214.

Laestander, M. (2014) *Solving Sudoku efficiently with Dancing Links*. Stockholm, Sweden: KTH Royal Institute of Technology. Available from: https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf [Accessed 27 March 2021].

Wikipedia (2021) Selection algorithm. Available from: https://en.m.wikipedia.org/wiki/Selection_algorithm [Accessed 28 March 2021].
