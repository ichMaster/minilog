"""Arithmetic evaluation and comparison operators for minilog."""

import math

from minilog.errors import EvaluatorError
from minilog.terms import Compound, Num, Term, Var
from minilog.unify import Substitution, walk

# Binary arithmetic operators
_BINARY_OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
}


def evaluate(term: Term, subst: Substitution) -> Num:
    """Recursively evaluate a term to a numeric value under a substitution.

    Handles: Num literals, variables (walked), compound arithmetic (+, -, *, /),
    unary minus, and built-in functions (sqrt, abs, pow).
    """
    resolved = walk(term, subst)

    if isinstance(resolved, Num):
        return resolved

    if isinstance(resolved, Var):
        raise EvaluatorError(f"unbound variable {resolved!r} in arithmetic expression")

    if isinstance(resolved, Compound):
        # Binary arithmetic: +, -, *, /
        if resolved.functor in _BINARY_OPS and resolved.arity == 2:
            lv = evaluate(resolved.args[0], subst).value
            rv = evaluate(resolved.args[1], subst).value
            result = _BINARY_OPS[resolved.functor](lv, rv)
            return Num(value=result)

        if resolved.functor == "/" and resolved.arity == 2:
            lv = evaluate(resolved.args[0], subst).value
            rv = evaluate(resolved.args[1], subst).value
            if rv == 0:
                raise EvaluatorError("division by zero")
            return Num(value=lv / rv)  # always float

        # Unary minus
        if resolved.functor == "-" and resolved.arity == 1:
            v = evaluate(resolved.args[0], subst).value
            return Num(value=-v)

        # Built-in functions
        if resolved.functor == "sqrt" and resolved.arity == 1:
            v = evaluate(resolved.args[0], subst).value
            if v < 0:
                raise EvaluatorError(f"sqrt of negative number: {v}")
            return Num(value=math.sqrt(v))

        if resolved.functor == "abs" and resolved.arity == 1:
            v = evaluate(resolved.args[0], subst).value
            return Num(value=abs(v))

        if resolved.functor == "pow" and resolved.arity == 2:
            bv = evaluate(resolved.args[0], subst).value
            ev = evaluate(resolved.args[1], subst).value
            result = bv ** ev
            # Preserve int type when both operands are int and exponent >= 0
            if isinstance(bv, int) and isinstance(ev, int) and ev >= 0:
                result = int(result)
            return Num(value=result)

        raise EvaluatorError(
            f"unknown arithmetic function {resolved.functor}/{resolved.arity}"
        )

    raise EvaluatorError(
        f"expected numeric value, got {type(resolved).__name__}: {resolved!r}"
    )


def check_comparison(left: Term, op: str, right: Term,
                     subst: Substitution) -> bool:
    """Evaluate a comparison: left op right under the given substitution.

    Supported operators: ≥, ≤, >, <, =, ≠
    Equality (=, ≠) works on any terms. Ordering (≥, ≤, >, <) requires numbers.
    For = and ≠ with arithmetic expressions, both sides are evaluated numerically.
    """
    if op in ("=", "≠"):
        # Try numeric evaluation first; fall back to term equality
        try:
            lval = evaluate(left, subst).value
            rval = evaluate(right, subst).value
            return lval == rval if op == "=" else lval != rval
        except EvaluatorError:
            lval = subst.apply(left)
            rval = subst.apply(right)
            return lval == rval if op == "=" else lval != rval

    lval = evaluate(left, subst).value
    rval = evaluate(right, subst).value

    if op == "≥":
        return lval >= rval
    if op == "≤":
        return lval <= rval
    if op == ">":
        return lval > rval
    if op == "<":
        return lval < rval

    raise EvaluatorError(f"unknown comparison operator: {op!r}")
