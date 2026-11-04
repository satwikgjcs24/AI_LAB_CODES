"""
Truth-Table Enumeration for Propositional Entailment (TT-ENTAILS?)

KB |= alpha  if alpha is true in EVERY model where KB is true.

Sentences are written as Python functions that take a model (dict of
symbol -> True/False) and return True/False.

Run:  python tt_entails.py
"""


def implies(p, q):
    """P => Q  is false only when P is true and Q is false."""
    return (not p) or q


def pl_true(sentence, model):
    """PL-TRUE?: evaluate a sentence in a (complete) model."""
    return sentence(model)


def tt_entails(kb, alpha, symbols):
    """TT-ENTAILS?: returns True if KB |= alpha, else False."""
    return tt_check_all(kb, alpha, list(symbols), {})


def tt_check_all(kb, alpha, symbols, model):
    """TT-CHECK-ALL: recursively enumerate all assignments."""
    if not symbols:                                   # EMPTY?(symbols)
        if pl_true(kb, model):                        # KB true in this model
            return pl_true(alpha, model)              # then alpha must be true
        return True                                   # KB false -> row ignored
    p, rest = symbols[0], symbols[1:]                 # FIRST / REST
    return (tt_check_all(kb, alpha, rest, {**model, p: True}) and
            tt_check_all(kb, alpha, rest, {**model, p: False}))


def print_truth_table(kb, alpha, symbols):
    """Print every row with KB and alpha, marking models where KB is true."""
    n = len(symbols)
    header = " ".join(f"{s:<5}" for s in symbols) + " | KB    alpha"
    print(header)
    print("-" * len(header))
    for i in range(2 ** n):
        values = [bool((i >> (n - 1 - k)) & 1) for k in range(n)]
        model = dict(zip(symbols, values))
        kb_v, a_v = kb(model), alpha(model)
        row = " ".join(f"{str(v):<5}" for v in values)
        mark = "  <-- KB true" if kb_v else ""
        print(f"{row} | {str(kb_v):<5} {str(a_v):<5}{mark}")


if __name__ == "__main__":
    # ------------------------------------------------------------
    # Example 1 (from the slides): alpha = A v B, KB = (A v C) ^ (B v ~C)
    # ------------------------------------------------------------
    syms = ["A", "B", "C"]
    kb1 = lambda m: (m["A"] or m["C"]) and (m["B"] or not m["C"])
    alpha1 = lambda m: m["A"] or m["B"]

    print("Example 1:  KB = (A v C) ^ (B v ~C),  alpha = A v B")
    print_truth_table(kb1, alpha1, syms)
    print("KB entails alpha?", tt_entails(kb1, alpha1, syms))

    # ------------------------------------------------------------
    # Example 2 (observation-book question):
    # KB = (Q => P) ^ (P => ~Q) ^ (Q v R)
    # ------------------------------------------------------------
    syms2 = ["P", "Q", "R"]
    kb2 = lambda m: (implies(m["Q"], m["P"]) and
                     implies(m["P"], not m["Q"]) and
                     (m["Q"] or m["R"]))

    print("\nExample 2:  KB = (Q->P) ^ (P->~Q) ^ (Q v R)")
    print_truth_table(kb2, lambda m: m["R"], syms2)

    queries = {
        "R":      lambda m: m["R"],
        "R -> P": lambda m: implies(m["R"], m["P"]),
        "Q -> R": lambda m: implies(m["Q"], m["R"]),
    }
    for name, q in queries.items():
        print(f"KB entails {name:<7}? {tt_entails(kb2, q, syms2)}")