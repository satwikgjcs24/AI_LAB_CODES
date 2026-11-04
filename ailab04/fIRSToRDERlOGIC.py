"""
Unification in First-Order Logic
Follows the Unify(Psi1, Psi2) algorithm from the lab slides.

Conventions
  variable : starts with a lowercase letter   x, y, z
  constant : starts with an uppercase letter  Riya, Apple, John
  compound : Name(arg1, arg2, ...)            Eats(x, Apple), Mother(y)
A substitution {t/v} means "replace variable v by term t".

Run:  python unification.py
"""

import re

FAILURE = "FAILURE"
NIL = []                                   # empty substitution


# ---------------- term helpers ----------------
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
def unify(t1, t2):
    """Return a substitution (list of (term, variable)), NIL, or FAILURE."""

    # Step 1: if either is a variable or constant
    if not isinstance(t1, tuple) or not isinstance(t2, tuple):
        if t1 == t2:
            return NIL
        if is_variable(t1):
            return FAILURE if occurs(t1, t2) else [(t2, t1)]    # {t2 / t1}
        if is_variable(t2):
            return FAILURE if occurs(t2, t1) else [(t1, t2)]    # {t1 / t2}
        return FAILURE

    # Step 2: predicate / function symbols must be the same
    if t1[0] != t2[0]:
        return FAILURE

    # Step 3: number of arguments must be the same
    if len(t1) != len(t2):
        return FAILURE

    # Step 4: SUBST = NIL
    args1, args2 = list(t1[1:]), list(t2[1:])
    subst = []

    # Step 5: unify argument by argument
    for i in range(len(args1)):
        s = unify(args1[i], args2[i])
        if s == FAILURE:
            return FAILURE
        if s:                                              # s is not NIL
            for j in range(i + 1, len(args1)):             # apply s to the rest
                args1[j] = apply_subst(args1[j], s)
                args2[j] = apply_subst(args2[j], s)
            subst = s + [(apply_subst(v, s), x) for v, x in subst]   # APPEND

    # Step 6
    return subst


# ---------------- parsing and printing ----------------
def parse(text):
    """'Eats(x, Apple)' -> ('Eats', 'x', 'Apple')"""
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