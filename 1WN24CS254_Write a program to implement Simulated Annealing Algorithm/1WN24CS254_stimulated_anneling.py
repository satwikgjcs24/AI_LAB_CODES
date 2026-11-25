"""
N-Queens using Simulated Annealing

State  : state[row] = column of the queen in that row (one queen per row)
Energy : number of attacking queen pairs (same column or same diagonal)
Goal   : energy = 0

Run:  python nqueens_sa.py          (default N = 8)
      python nqueens_sa.py 12       (N = 12)
"""

import math
import random
import sys


def energy(state):
    """Count pairs of queens that attack each other."""
    n = len(state)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            same_column = state[i] == state[j]
            same_diagonal = abs(state[i] - state[j]) == abs(i - j)
            if same_column or same_diagonal:
                conflicts += 1
    return conflicts


def neighbor(state):
    """Move the queen of one random row to a different random column."""
    n = len(state)
    new_state = state[:]
    row = random.randrange(n)
    col = random.randrange(n)
    while col == new_state[row]:          # make sure the move changes something
        col = random.randrange(n)
    new_state[row] = col
    return new_state


def simulated_annealing(n, t_start=10.0, t_end=0.001, alpha=0.99, iters=100):
    """Return (state, energy). energy == 0 means a valid solution."""
    current = [random.randrange(n) for _ in range(n)]
    current_e = energy(current)
    t = t_start

    while t > t_end:
        for _ in range(iters):
            if current_e == 0:
                return current, current_e

            candidate = neighbor(current)
            candidate_e = energy(candidate)
            delta = candidate_e - current_e

            # Better move: always accept.
            # Worse move: accept with probability e^(-delta / T).
            if delta < 0 or random.random() < math.exp(-delta / t):
                current, current_e = candidate, candidate_e

        t *= alpha                         # cool down

    return current, current_e


def print_board(state):
    n = len(state)
    for r in range(n):
        print(" ".join("Q" if state[r] == c else "." for c in range(n)))


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    random.seed(1)

    # SA is randomized, so retry a few times if one run ends in a local minimum.
    for attempt in range(1, 11):
        solution, e = simulated_annealing(N)
        if e == 0:
            print(f"Solved N={N} on attempt {attempt}")
            print("State (column per row):", solution)
            print_board(solution)
            break
    else:
        print(f"No perfect solution found; best energy = {e}")