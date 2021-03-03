# Dancing Links (DLX) - Solving Sudoku

When deciding which algorithm to pursue for my sudoku solver, efficiency in the algorithm was my upmost priority. After some search into various algorithms, I discovered various algorithms with varying time complexity. One approach involved a standard depth-first search algorithm, which has a time complexity of O(n^2), where n is both the size of the square grid and number of possible numbers a cell can hold. This approach would be highly achievable due to it being covered in the unit material and can be paired with constraint satisfaction. However, after further research, I discovered that it is possible for sudoku of a fixed nxn size to be solved in O(1) time. NP completeness is a concept which applies to any decision-based problem that has a variable input size. Should the input size, n not be fixed, the time complexity would be O(n) (NP complete), because n will tend towards infinity. In this case, the algorithm would spend O(n) time simply reading the input as it can't expect what size the grid will be beforehand. 

In terms of sudoku, NP-completeness is achievable because any sudoku is reducible to the exact cover problem; an algorithm which is known to be NP complete. The exact cover problem is a type of constraint satisfaction problem and can be represented visually using a binary sparce matrix, where a 1 represents an incidence relation. One very efficient way of finding all solutions to the exact cover problem is by using Algorithm X, discovered by Donald Knuth. Algorithm X is a recursive, nondeterministic algorithm that utilizes depth-first search to support backtracking. It is referred to as DLX when efficiently implemented using the Dancing Links (DLX) technique (Knuth et al., 2000), originally invented by Hiroshi Hitotsumatsu and Kohei Noshita, but later popularised by Donald Knuth. DLX is a technique which can be used to undo the operation of removing a given node from a circular doubly linked list. See the example below for a basic overview of how this works.

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
foo.right.left = foo
foo.left.right = foo
```

To reduce a 9x9 sudoku to the exact cover problem, it is important to understand how the rules of sudoku can be described in terms of 4 constraints (Laestander, M, 2014):
- **Cell Constraint:** A Cell can contain one integer from 1-9.
- **Row Constraint:** Each row must contain 9 unique integers from 1-9.
- **Column Constraint:** Each column must contain 9 unique integers from 1-9.
- **Box Constraint:** All 9 cells in a 3x3 box must contain 9 unique integers from 1-9.

When representing the exact cover problem in a sparse matrix, the columns represent constraints and rows represent possible solutions. There are 81 cells in a 9x9 sudoku puzzle:
- **Columns:** therefore, each constraint will occupy 81 columns. There are 4 constraints so there will be a total of 81*4 = 324 columns.
- **Rows:** each cell can have 9 possible solutions (should there be no clue given), so there can be up to 81*9 = 729 rows. Each cell with a clue given will only add one row to the matrix due to it having only one possible value (the clue given). 

Once these fundamentals have been understood, the way DLX can be applied to this cover problem is straightforward. Each column in the matrix, M will track how many.

Within the search function exists a call to a function called `choose_column_object`, which returns a column object present in the M. The column this returns is then next in line to be covered (removed from the linked list like the former example in the code block above). Donald Knuth proposes that there are two ways to go about implementing this function. It could either return the column containing the least amount of 1's, or simply return the first column following the head. Donald Knuth suggests that the former is worth the additional computation in order to minimise the branching factor, so this is the decision I made. To do this, I used a Python generator to loop over and compare the size of all columns by using an equality operator to compare each column's size to the current lowest value. Furthermore, I found with my own tests that if I returned a column with a size of 0 (the smallest number of 1's a column could contain) immediately after coming across one, the DLX algorithm was on average an additional 0.78s quicker when completing a sample of 60 sudokus of varying difficulty. d.f. = 100.

Once the DLX algorithm successfully halted in a solution found state, I was able to translate the solution from the binary matrix, M relatively easily. We know that M contains 81 rows, one for each cell in the sudoku puzzle, whereby each row will contain an integer identifier as per the DLX algorithm. This was firstly sorted in descending order. Due to the domain of a 9x9 sudoku puzzle being 9, I was able to take the modulus of 9 for each row once zero-based indices were corrected for.

## References

Knuth, D.E., Davies, J., Roscoe, B. and Woodcock, J. (2000) Dancing links. *Millenial Perspectives in Computer Science*, pp.187–214.

Laestander, M. (2014) *Solving Sudoku efficiently with Dancing Links*. Stockholm, Sweden: KTH Royal Institute of Technology. Available from: https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf [Accessed 27 March 2021].




