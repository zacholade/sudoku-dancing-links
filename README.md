# sudoku-dancing-links

When deciding which algorithm to pursue for my sudoku solver, efficiency in the algorithm was my upmost priority. After some search into various algorithms, I discovered various algorithms with varying time complexity. One approach involved a standard depth-first search algorithm, which has a time complexity of O(n^2), where n is both the size of the square grid and number of possible numbers a cell can hold. This approach would be highly achievable due to it being covered in the unit material and can be paired with constraint satisfaction. However, after further research, I discovered that it is possible for sudoku of a fixed nxn size to be solved in O(1) time. NP completeness is a concept which applies to any decision-based problem that has a variable input size. Should the input size, n not be fixed, the time complexity would be O(n) (np complete), because n will tend towards infinity and the algorithm would spend O(n) time simply reading the input. 

O(1) time complexity is achievable due to any sudoku being reducible to the exact cover problem; an algorithm which is known to be NP complete. The exact cover problem is a type of constraint satisfaction problem and can be represented visually using a binary sparce matrix, where a 1 represents an incidence relation. One very efficient way of finding all solutions to the exact cover problem is by using Algorithm X, discovered by Donald Knuth. Algorithm X is a recursive, nondeterministic algorithm that utilizes depth-first search to support backtracking. It is referred to as DLX when efficiently implemented using the Dancing Links (DLX) technique (Knuth et al., 2000), originally invented by Hiroshi Hitotsumatsu and Kohei Noshita, but later popularised by Donald Knuth. DLX is a technique which can be used to undo the operation of removing a given node from a circular doubly linked list. See the example below for a basic overview of how this works.

```python
# Where foo represents a node in a circular doubly linked list and the left
# and right attributes refer to the nodes to the left and right in the list:

# These two lines will remove foo from the doubly linked list.
# Note: Even though foo is removed from the list itself,
# foo will retain its left and right neighbours.
foo.right.left = foo.left
foo.left.right = foo.right

# These two lines will restore foo's position back into the list.
foo.right.left = foo
foo.left.right = foo
```


## References

Knuth, D.E., Davies, J., Roscoe, B. and Woodcock, J. (2000) Dancing links. *Millenial Perspectives in Computer Science*, pp.187–214.

Laestander, M. (2014) *Solving Sudoku efficiently with Dancing Links*. Stockholm, Sweden: KTH Royal Institute of Technology. Available from: https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf [Accessed 27 March 2021].




