"""
Unification in First-Order Logic  (follows Unify(Psi1, Psi2) from the lab slides)

Conventions
  variable : starts with a lowercase letter   x, y, z
  constant : starts with an uppercase letter  Riya, Apple, John
  compound : Name(arg1, arg2, ...)            Eats(x, Apple), Mother(y)

Substitution {t/v} means "replace variable v by term t".
Stored as a list of (term, variable) pairs.

Run:  python unification.py
"""

import re

FAILURE = "FAILURE"
NIL = []                                   # empty substitution (nothing to change)


# ---------------- helpers ----------------
def is_variable(t):
    return isinstance(t, str) and t[0].islower()


def occurs(var, term):
    """Occurs check: does var appear inside term?"""
    if term == var:
        return True
    if isinstance(term, tuple):
        return any(occurs(var, a) for a in term[1:])
    return False


def substitute(term, var, value):
    """Replace every occurrence of var in term by value."""
    if term == var:
        return value
    if isinstance(term, tuple):
        return (term[0],) + tuple(substitute(a, var, value) for a in term[1:])
    return term


def apply_subst(term, subst):
    for value, var in subst:
        term = substitute(term, var, value)
    return term


# ---------------- the algorithm ----------------
def unify(psi1, psi2):
    """Return a substitution (list of (term, variable)), NIL, or FAILURE."""

    # Step 1: if either one is a variable or a constant
    if not isinstance(psi1, tuple) or not isinstance(psi2, tuple):
        if psi1 == psi2:                                   # a) identical
            return NIL
        if is_variable(psi1):                              # b) psi1 is a variable
            return FAILURE if occurs(psi1, psi2) else [(psi2, psi1)]   # {psi2/psi1}
        if is_variable(psi2):                              # c) psi2 is a variable
            return FAILURE if occurs(psi2, psi1) else [(psi1, psi2)]   # {psi1/psi2}
        return FAILURE                                     # d) two different constants

    # Step 2: predicate / function symbols must be the same
    if psi1[0] != psi2[0]:
        return FAILURE

    # Step 3: number of arguments must be the same
    if len(psi1) != len(psi2):
        return FAILURE

    # Step 4: SUBST = NIL
    args1, args2 = list(psi1[1:]), list(psi2[1:])
    subst = []

    # Step 5: unify the arguments one by one
    for i in range(len(args1)):
        s = unify(args1[i], args2[i])                      # a) recursive call
        if s == FAILURE:                                   # b) failure
            return FAILURE
        if s:                                              # c) s is not NIL
            for j in range(i + 1, len(args1)):             #    apply s to the rest
                args1[j] = apply_subst(args1[j], s)
                args2[j] = apply_subst(args2[j], s)
            subst = s + [(apply_subst(v, s), x) for v, x in subst]     # APPEND(S, SUBST)

    # Step 6
    return subst


# ---------------- parsing and printing ----------------
def parse(text):
    """'Eats(x, Apple)'  ->  ('Eats', 'x', 'Apple')"""
    tokens = re.findall(r"[A-Za-z_]\w*|[(),]", text)
    pos = 0

    def term():
        nonlocal pos
        name = tokens[pos]
        pos += 1
        if pos < len(tokens) and tokens[pos] == "(":
            pos += 1
            args = [term()]
            while tokens[pos] == ",":
                pos += 1
                args.append(term())
            pos += 1                                       # skip ')'
            return (name, *args)
        return name

    return term()


def to_str(t):
    if isinstance(t, tuple):
        return f"{t[0]}({', '.join(to_str(a) for a in t[1:])})"
    return t


def show(subst):
    if subst == FAILURE:
        return "FAILURE"
    if not subst:
        return "{} (NIL)"
    return "{" + ", ".join(f"{to_str(v)}/{x}" for v, x in subst) + "}"


def unify_strings(a, b):
    t1, t2 = parse(a), parse(b)
    s = unify(t1, t2)
    print(f"Unify({a},  {b})")
    print("  substitution :", show(s))
    if s != FAILURE:
        print("  unified form :", to_str(apply_subst(t1, s)))
    print()


if __name__ == "__main__":
    unify_strings("Eats(x, Apple)", "Eats(Riya, y)")            # slide example
    unify_strings("Knows(John, x)", "Knows(y, Mother(y))")      # nested term
    unify_strings("P(x, h(y))", "P(A, f(z))")                   # h and f differ
    unify_strings("Knows(John, x)", "Knows(x, Elisabeth)")      # x clash
    unify_strings("p(f(A), g(y))", "p(x, x)")                   # f and g differ
    unify_strings("P(x)", "P(f(x))")                            # occurs check
    unify_strings("P(x, y)", "P(A)")                            # arity differs

    # Try your own expressions here:
    # unify_strings("Loves(x, Mary)", "Loves(John, y)")