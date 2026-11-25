import math

def alphabeta(node, alpha, beta, is_max):
    # Leaf node: return its value
    if isinstance(node, int):
        print("Visited leaf:", node)
        return node

    if is_max:
        best = -math.inf
        for child in node:
            best = max(best, alphabeta(child, alpha, beta, False))
            alpha = max(alpha, best)
            if alpha >= beta:
                print(f"Pruned (alpha={alpha}, beta={beta})")
                break
        return best
    else:
        best = math.inf
        for child in node:
            best = min(best, alphabeta(child, alpha, beta, True))
            beta = min(beta, best)
            if alpha >= beta:
                print(f"Pruned (alpha={alpha}, beta={beta})")
                break
        return best

tree = [[[3, 5], [6, 9]], [[1, 2], [0, -1]]]

result = alphabeta(tree, -math.inf, math.inf, True)
print("Optimal value:", result)