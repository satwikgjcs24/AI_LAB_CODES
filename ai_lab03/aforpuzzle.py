
import heapq

def manhattan(state, goal):
    distance = 0

    for i in range(9):
        if state[i] != 0:
            j = goal.index(state[i])
            r1, c1 = divmod(i, 3)
            r2, c2 = divmod(j, 3)
            distance += abs(r1 - r2) + abs(c1 - c2)

    return distance


def get_neighbors(state):
    neighbors = []
    zero = state.index(0)
    r, c = divmod(zero, 3)

    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc

        if 0 <= nr < 3 and 0 <= nc < 3:
            pos = nr * 3 + nc
            new_state = list(state)
            new_state[zero], new_state[pos] = (
                new_state[pos], new_state[zero]
            )
            neighbors.append(tuple(new_state))

    return neighbors


def a_star(initial, goal):
    pq = [(manhattan(initial, goal), 0, initial)]
    parent = {initial: None}
    cost = {initial: 0}

    while pq:
        f, g, current = heapq.heappop(pq)

        if g != cost[current]:
            continue

        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]

        for neighbor in get_neighbors(current):
            new_g = g + 1

            if new_g < cost.get(neighbor, float("inf")):
                cost[neighbor] = new_g
                parent[neighbor] = current
                h = manhattan(neighbor, goal)
                heapq.heappush(pq, (new_g + h, new_g, neighbor))

    return None


def read_state(message):
    print(message)
    state = []

    for i in range(3):
        while True:
            try:
                row = list(map(int, input(
                    f"Enter row {i + 1} (3 numbers separated by spaces): "
                ).split()))

                if len(row) != 3:
                    print("Please enter exactly 3 numbers.")
                    continue

                state.extend(row)
                break
            except ValueError:
                print("Enter numbers only.")

    if sorted(state) != list(range(9)):
        raise ValueError("Use each number from 0 to 8 exactly once.")

    return tuple(state)


def print_state(state):
    for i in range(0, 9, 3):
        print(*state[i:i + 3])


try:
    initial = read_state("\nEnter INITIAL state (0 represents blank):")
    goal = read_state("\nEnter GOAL state (0 represents blank):")

    path = a_star(initial, goal)

    if path:
        print("\nSolution found!")
        print("Minimum number of moves:", len(path) - 1)

        for step, state in enumerate(path):
            print(f"\nStep {step}:")
            print_state(state)
    else:
        print("No solution exists.")

except ValueError as e:
    print("Invalid input:", e)
