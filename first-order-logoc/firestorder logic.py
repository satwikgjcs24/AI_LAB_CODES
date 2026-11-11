"""
Knowledge-Based Agent using First-Order Logic (Forward Chaining)

Parts
  1. Term representation + parser   "Missile(x) & Owns(A,x) => Sells(Robert,x,A)"
  2. Unification                    (with occurs check)
  3. Forward chaining               (FOL-FC-ASK from the lab slides)
  4. KnowledgeBaseAgent             tell() facts/rules, ask() queries

Conventions
  variable          : starts with a lowercase letter   x, p, q
  constant/predicate: starts with an uppercase letter  Robert, Missile, T1
  rule              : P1 & P2 & ... => Q     (definite clause)
  fact              : an atomic sentence such as American(Robert)

Run:  python fol_kb_agent.py
"""

import itertools
import re


# ----------------------------------------------------------------------
# 1. Terms and parsing
#    constant/variable -> str ;  compound -> tuple ('Pred', arg1, arg2, ...)
# ----------------------------------------------------------------------
def is_variable(t):
    return isinstance(t, str) and t[0].islower()


def parse_term(text):
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
            pos += 1                                   # skip ')'
            return (name, *args)
        return name

    return term()


def to_str(t):
    if isinstance(t, tuple):
        return f"{t[0]}({', '.join(to_str(a) for a in t[1:])})"
    return t


def parse_sentence(text):
    """Return ('fact', atom)  or  ('rule', [premises], conclusion)."""
    if "=>" in text:
        left, right = text.split("=>")
        premises = [parse_term(p.strip()) for p in left.split("&")]
        return ("rule", premises, parse_term(right.strip()))
    return ("fact", parse_term(text.strip()))


# ----------------------------------------------------------------------
# 2. Substitution and unification
#    theta is a dict {variable: term}
# ----------------------------------------------------------------------
def subst(term, theta):
    """SUBST(theta, term): apply a substitution fully."""
    if is_variable(term):
        return subst(theta[term], theta) if term in theta else term
    if isinstance(term, tuple):
        return (term[0],) + tuple(subst(a, theta) for a in term[1:])
    return term


def occurs(var, term, theta):
    term = subst(term, theta)
    if term == var:
        return True
    if isinstance(term, tuple):
        return any(occurs(var, a, theta) for a in term[1:])
    return False


def unify(x, y, theta):
    """Return an extended substitution that makes x and y equal, or None."""
    if theta is None:
        return None
    if x == y:
        return theta
    if is_variable(x):
        return unify_var(x, y, theta)
    if is_variable(y):
        return unify_var(y, x, theta)
    if isinstance(x, tuple) and isinstance(y, tuple):
        if x[0] != y[0] or len(x) != len(y):           # predicate / arity check
            return None
        for a, b in zip(x[1:], y[1:]):                 # argument by argument
            theta = unify(a, b, theta)
            if theta is None:
                return None
        return theta
    return None                                        # two different constants


def unify_var(var, x, theta):
    if var in theta:
        return unify(theta[var], x, theta)
    if is_variable(x) and x in theta:
        return unify(var, theta[x], theta)
    if occurs(var, x, theta):                          # occurs check
        return None
    return {**theta, var: x}


# ----------------------------------------------------------------------
# 3. Forward chaining helpers
# ----------------------------------------------------------------------
_counter = itertools.count(1)


def rename(term, mapping):
    if is_variable(term):
        return mapping[term]
    if isinstance(term, tuple):
        return (term[0],) + tuple(rename(a, mapping) for a in term[1:])
    return term


def variables_in(term, found=None):
    found = [] if found is None else found
    if is_variable(term):
        if term not in found:
            found.append(term)
    elif isinstance(term, tuple):
        for a in term[1:]:
            variables_in(a, found)
    return found


def standardize_variables(premises, conclusion):
    """Give the rule brand-new variable names so rules never clash."""
    n = next(_counter)
    names = []
    for t in premises + [conclusion]:
        variables_in(t, names)
    mapping = {v: f"{v}_{n}" for v in names}
    return [rename(p, mapping) for p in premises], rename(conclusion, mapping)


def match_premises(premises, facts, theta):
    """Yield every theta that makes ALL premises match known facts."""
    if not premises:
        yield theta
        return
    first, rest = premises[0], premises[1:]
    for fact in facts:
        t = unify(first, fact, theta)
        if t is not None:
            yield from match_premises(rest, facts, t)


# ----------------------------------------------------------------------
# 4. The knowledge-based agent
# ----------------------------------------------------------------------
class KnowledgeBaseAgent:
    def __init__(self, name="Agent", verbose=True):
        self.name = name
        self.facts = []            # ground atomic sentences
        self.rules = []            # (premises, conclusion)
        self.verbose = verbose

    # TELL: add knowledge
    def tell(self, sentence):
        parsed = parse_sentence(sentence)
        if parsed[0] == "fact":
            if parsed[1] not in self.facts:
                self.facts.append(parsed[1])
        else:
            self.rules.append((parsed[1], parsed[2]))

    # ASK: FOL-FC-ASK (forward chaining). Returns a substitution dict or False.
    def ask(self, query_text):
        query = parse_term(query_text)
        qvars = variables_in(query)
        kb = list(self.facts)

        def answer(phi):
            return {v: to_str(subst(v, phi)) for v in qvars}

        # query already a known fact?
        for f in kb:
            phi = unify(query, f, {})
            if phi is not None:
                self._log(f"Query already in KB: {to_str(f)}")
                return answer(phi)

        round_no = 0
        while True:                                    # repeat until new is empty
            round_no += 1
            new = []
            self._log(f"\n--- Round {round_no} ---")
            for premises, conclusion in self.rules:
                ps, q = standardize_variables(premises, conclusion)
                for theta in match_premises(ps, kb, {}):
                    q1 = subst(q, theta)
                    if q1 not in kb and q1 not in new:
                        new.append(q1)
                        self._log(f"  inferred {to_str(q1)}"
                                  f"   (rule: {' & '.join(to_str(p) for p in premises)}"
                                  f" => {to_str(conclusion)})")
                        phi = unify(q1, query, {})
                        if phi is not None:
                            self._log(f"  matches the query {to_str(query)}")
                            self.facts = kb + new
                            return answer(phi)
            if not new:                                # nothing new can be learned
                self._log("  no new facts, stopping")
                return False
            kb.extend(new)                             # add new to KB

    def _log(self, msg):
        if self.verbose:
            print(msg)


# ----------------------------------------------------------------------
# Demos
# ----------------------------------------------------------------------
def crime_demo():
    print("=" * 60)
    print("DEMO 1: Robert is a criminal (from the lab slides)")
    print("=" * 60)
    agent = KnowledgeBaseAgent("CrimeAgent")

    # Rules
    agent.tell("American(p) & Weapon(q) & Sells(p,q,r) & Hostile(r) => Criminal(p)")
    agent.tell("Missile(x) & Owns(A,x) => Sells(Robert,x,A)")
    agent.tell("Missile(x) => Weapon(x)")
    agent.tell("Enemy(x,America) => Hostile(x)")

    # Facts  (Exists x Owns(A,x) & Missile(x)  ->  new constant T1)
    agent.tell("American(Robert)")
    agent.tell("Owns(A,T1)")
    agent.tell("Missile(T1)")
    agent.tell("Enemy(A,America)")

    result = agent.ask("Criminal(Robert)")
    print("\nQuery  : Criminal(Robert)")
    print("Result :", "PROVED" if result is not False else "NOT PROVED", result)

    print("\nExtra query with a variable: Sells(Robert, m, A) -> what was sold?")
    agent2_result = agent.ask("Sells(Robert, m, A)")
    print("Answer :", agent2_result)


def socrates_demo():
    print("\n" + "=" * 60)
    print("DEMO 2: Who is mortal?")
    print("=" * 60)
    agent = KnowledgeBaseAgent("LogicAgent", verbose=False)
    agent.tell("Human(x) => Mortal(x)")
    agent.tell("Greek(x) & Philosopher(x) => Human(x)")
    agent.tell("Greek(Socrates)")
    agent.tell("Philosopher(Socrates)")

    print("Ask Mortal(z)        ->", agent.ask("Mortal(z)"))
    print("Ask Mortal(Socrates) ->", agent.ask("Mortal(Socrates)"))
    print("Ask Mortal(Plato)    ->", agent.ask("Mortal(Plato)"))


def unsolvable_demo():
    print("\n" + "=" * 60)
    print("DEMO 3: Goal that cannot be proven")
    print("=" * 60)
    agent = KnowledgeBaseAgent("CrimeAgent")
    agent.tell("American(p) & Weapon(q) & Sells(p,q,r) & Hostile(r) => Criminal(p)")
    agent.tell("American(Robert)")                      # no weapon, no sale, no hostile nation
    result = agent.ask("Criminal(Robert)")
    print("\nResult :", "PROVED" if result is not False else "NOT PROVED", result)


if __name__ == "__main__":
    crime_demo()
    socrates_demo()
    unsolvable_demo()