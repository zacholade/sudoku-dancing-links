import numpy as np
import dlx
import argparse
import sys
import os


if __name__ == "__main__":
    """Example usage:
    py puzzle_saver.py --puzzle
    000000000000000000000000000384000000000000000000000000000000000000000000000000002 
    --filename impossible
    """
    # Goes row by row. Not column by column.

    parser = argparse.ArgumentParser()
    parser.add_argument("--puzzle")
    parser.add_argument("--filename")
    parser.add_argument("--overwrite", default=False, type=bool)
    args = parser.parse_args()

    try:
        puzzle = np.array([int(i) for i in args.puzzle], dtype=int).reshape(9, 9)
    except ValueError:
        print("Could not parse puzzle. Should be 81 numbers long.")
        sys.exit(1)

    print(f"Loaded puzzle: \n{puzzle}")
    solution = dlx.DLX(puzzle).solve()
    print(f"Found solution: \n{solution}")

    if not os.path.exists('data'):
        os.mkdir('data')

    def save(file_path, data_to_save):
        with open(file_path, 'wb') as f:
            np.save(f, data_to_save)

    def write(file_path, data_to_save):
        if args.overwrite:
            save(file_path, [data_to_save])
        else:
            try:
                with open(file_path, 'rb') as f:
                    puzzles = np.load(f)
                    to_save = np.array([data_to_save])
                    data_to_save = np.concatenate((puzzles, to_save))
                    save(file_path, data_to_save)
            except FileNotFoundError:
                save(file_path, [data_to_save])

    puzzle_string = f"data/{args.filename}_puzzle.npy"
    solution_string = f"data/{args.filename}_solution.npy"
    write(puzzle_string, puzzle)
    write(solution_string, solution)
    print("Puzzles saved successfully")
    sys.exit(0)
