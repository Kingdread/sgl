# -*- coding: utf-8 -*-
import scipy.linalg

def null(f):
    return abs(f) < 1e-10

def nullrow(r):
    return all(map(null, r))

def solve(matrix):
    _, s = scipy.linalg.lu(matrix, True)
    return Solution(s)

def count(f, l):
    c = 0
    for i in l:
        if f(i):
            c += 1
    return c

def index(f, l):
    for i, v in enumerate(l):
        if f(v):
            return i
    raise ValueError("No item satisfies {}".format(f))

def first_nonzero(r):
    for i, v in enumerate(r):
        if not null(v):
            return i
    return len(r)

class Solution(object):
    """Holds a solution to a system of equations."""
    def __init__(self, s):
        self._s = s
        self.varcount = s.shape[1] - 1
        # No solution, 0a + 0b + 0c + ... = 1 which can never be true
        self._solvable = not any(
            all(null(coeff) for coeff in row[:-1]) and not null(row[-1])
            for row in s
        )
        unique_equations = sum(1 for row in s if not nullrow(row))
        self.varargs = self.varcount - unique_equations
        self.exact =  self.varargs == 0

    def __bool__(self):
        return self._solvable
    __nonzero__ = __bool__

    def __call__(self, *v):
        if not self._solvable:
            raise ValueError("Has no solution")
        if len(v) != self.varargs:
            raise ValueError("Expected {} values, got {}".format(
                self.varargs, len(v)))
        v = list(v)
        vals = [None] * self.varcount
        # Scan for real solutions
        for i, row in enumerate(self._s):
            # Can't use .count here because we need null()
            # I miss Haskell lambdas :(
            if count(lambda i: not null(i), row[:-1]) == 1:
                # We can find a variable here
                var = index(lambda i: not null(i), row[:-1])
                vals[var] = row[-1] / row[var]
        # Fill in the rest with given values
        for i in reversed(range(len(vals))):
            if not v:
                break
            if vals[i] is None:
                vals[i] = v.pop()

        for i in reversed(range(len(self._s))):
            row = self._s[i]
            if nullrow(row):
                continue
            tbd = first_nonzero(row)
            s = sum(-1 * row[j] * vals[j] for j in range(tbd + 1, len(row) - 1))
            s += row[-1]
            vals[tbd] = s / row[tbd]
        return tuple(vals)
