# Formats: ('pred', name, args...), ('not', A), ('and'/'or'/'imp'/'iff', A, B),
#          ('forall'/'exists', var, A)

def remove_imp(f):
    op = f[0]
    if op == 'pred':
        return f
    if op in ('forall', 'exists'):
        return (op, f[1], remove_imp(f[2]))
    args = [remove_imp(a) for a in f[1:]]
    if op == 'imp':
        a, b = args
        return ('or', ('not', a), b)
    if op == 'iff':
        a, b = args
        return ('and', ('or', ('not', a), b), ('or', ('not', b), a))
    return (op, *args)

def nnf(f, neg=False):
    op = f[0]
    if op == 'pred':
        return ('not', f) if neg else f
    if op == 'not':
        return nnf(f[1], not neg)
    if op in ('and', 'or'):
        if neg:
            op = 'or' if op == 'and' else 'and'
        return (op, nnf(f[1], neg), nnf(f[2], neg))
    if neg:
        op = 'exists' if op == 'forall' else 'forall'
    return (op, f[1], nnf(f[2], neg))

def standardize(f, env, count):
    op = f[0]
    if op == 'pred':
        return ('pred', f[1], *[env.get(a, a) for a in f[2:]])
    if op in ('forall', 'exists'):
        v = f[1]
        n = count.get(v, 0)
        count[v] = n + 1
        new = v if n == 0 else f"{v}{n}"
        return (op, new, standardize(f[2], {**env, v: new}, count))
    return (op, *[standardize(a, env, count) for a in f[1:]])

def skolemize(f, universals, env, count):
    op = f[0]
    if op == 'pred':
        return ('pred', f[1], *[env.get(a, a) for a in f[2:]])
    if op == 'forall':                      # drop ∀, remember variable
        return skolemize(f[2], universals + [f[1]], env, count)
    if op == 'exists':                      # replace with Skolem term
        count[0] += 1
        if universals:
            term = f"F{count[0]}({','.join(universals)})"
        else:
            term = f"C{count[0]}"
        return skolemize(f[2], universals, {**env, f[1]: term}, count)
    return (op, *[skolemize(a, universals, env, count) for a in f[1:]])

def distribute(f):
    if f[0] not in ('and', 'or'):
        return f
    a, b = distribute(f[1]), distribute(f[2])
    if f[0] == 'or':
        if a[0] == 'and':
            return ('and', distribute(('or', a[1], b)), distribute(('or', a[2], b)))
        if b[0] == 'and':
            return ('and', distribute(('or', a, b[1])), distribute(('or', a, b[2])))
    return (f[0], a, b)

def show(f):
    op = f[0]
    if op == 'pred':
        return f"{f[1]}({','.join(f[2:])})"
    if op == 'not':
        return "¬" + show(f[1])
    if op in ('forall', 'exists'):
        q = "∀" if op == 'forall' else "∃"
        return f"{q}{f[1]} {show(f[2])}"
    sym = {'and': '∧', 'or': '∨', 'imp': '→', 'iff': '↔'}[op]
    return f"({show(f[1])} {sym} {show(f[2])})"

# Example
formula = ('forall', 'x',
            ('imp',
              ('forall', 'y',
                ('imp', ('pred', 'Animal', 'y'), ('pred', 'Loves', 'x', 'y'))),
              ('exists', 'y', ('pred', 'Loves', 'y', 'x'))))

print("Input:", show(formula))
f = remove_imp(formula);        print("1. Remove →  :", show(f))
f = nnf(f);                     print("2. Move ¬    :", show(f))
f = standardize(f, {}, {});     print("3. Rename    :", show(f))
f = skolemize(f, [], {}, [0]);  print("4-5. Skolem  :", show(f))
f = distribute(f);              print("6. CNF       :", show(f))