"""Arithmetic evaluation and comparison operators for minilog."""

from minilog.errors import EvaluatorError
from minilog.terms import Num, Term, Var
from minilog.unify import Substitution, walk


def evaluate(term: Term, subst: Substitution) -> Num:
    """Resolve a term to a numeric value under a substitution.

    Raises EvaluatorError if the resolved term is not a Num.
    """
    resolved = walk(term, subst)
    if isinstance(resolved, Var):
        raise EvaluatorError(f"unbound variable {resolved!r} in arithmetic expression")
    if not isinstance(resolved, Num):
        raise EvaluatorError(
            f"expected numeric value, got {type(resolved).__name__}: {resolved!r}"
        )
    return resolved


def check_comparison(left: Term, op: str, right: Term,
                     subst: Substitution) -> bool:
    """Evaluate a comparison: left op right under the given substitution.

    Supported operators: ≥, ≤, >, <, =, ≠
    """
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
    if op == "=":
        return lval == rval
    if op == "≠":
        return lval != rval

    raise EvaluatorError(f"unknown comparison operator: {op!r}")
