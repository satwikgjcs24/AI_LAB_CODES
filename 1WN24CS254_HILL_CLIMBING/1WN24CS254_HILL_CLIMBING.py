
import random

def heuristic(state):
    conflicts = 0
    n = len(state)

    for i in range(n):
        for j in range(i + 1, n):
            if abs(state[i] - state[j]) == abs(i - j):
                conflicts += 1

    return conflicts


def hill_climbing(n):
    state = list(range(n))
    random.shuffle(state)

    while True:
        current_h = heuristic(state)

        if current_h == 0:
            return state

        best_state = state[:]
        best_h = current_h

        for col in range(n):
            for row in range(n):
                if row != state[col]:
                    neighbor = state[:]
                    neighbor[col] = row
                    h = heuristic(neighbor)

                    if h < best_h:
                        best_h = h
                        best_state = neighbor

        if best_h >= current_h:
            return None

        state = best_state


def print_board(state):
    n = len(state)

    for row in range(n):
        for col in range(n):
            if state[col] == row:
                print("Q", end=" ")
            else:
                print(".", end=" ")
        print()


n = int(input("Enter the number of queens: "))

if n < 1:
    print("Enter a positive number.")
else:
    solution = None

    # Random restart to escape local minima
    for _ in range(1000):
        solution = hill_climbing(n)
        if solution is not None:
            break

    if solution is None:
        print("Solution not found. Try again.")
    else:
        print("\nSolution:", solution)
        print("Number of conflicts:", heuristic(solution))
        print("\nChessboard:")
        print_board(solution)
