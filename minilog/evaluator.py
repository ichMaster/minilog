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
                     subst: Substitution) -> Substitution | None:
    """Evaluate a comparison and return an (optionally extended) substitution.

    Returns the substitution (possibly extended with a binding) on success,
    or None on failure.

    For `=`: if one side is an unbound variable and the other evaluates to a
    number, bind the variable to the result (is/2 semantics). If both sides
    are ground, check numeric or term equality.

    For `≠`: check inequality (no binding).
    For ordering operators (≥, ≤, >, <): both sides must evaluate to numbers.
    """
    if op == "=":
        return _check_eq_binding(left, right, subst)

    if op == "≠":
        # Try numeric evaluation first; fall back to term inequality
        try:
            lval = evaluate(left, subst).value
            rval = evaluate(right, subst).value
            return subst if lval != rval else None
        except EvaluatorError:
            lval_t = subst.apply(left)
            rval_t = subst.apply(right)
            return subst if lval_t != rval_t else None

    lval = evaluate(left, subst).value
    rval = evaluate(right, subst).value

    result = False
    if op == "≥":
        result = lval >= rval
    elif op == "≤":
        result = lval <= rval
    elif op == ">":
        result = lval > rval
    elif op == "<":
        result = lval < rval
    else:
        raise EvaluatorError(f"unknown comparison operator: {op!r}")

    return subst if result else None


def _check_eq_binding(left: Term, right: Term,
                      subst: Substitution) -> Substitution | None:
    """Handle = with is/2-style binding for unbound variables."""
    from minilog.terms import Var as VarType

    left_walked = walk(left, subst)
    right_walked = walk(right, subst)

    left_is_var = isinstance(left_walked, VarType)
    right_is_var = isinstance(right_walked, VarType)

    # Both unbound — cannot evaluate, try term equality
    if left_is_var and right_is_var:
        # Bind left to right (unification)
        return subst.extend(left_walked, right_walked)

    # Left is unbound variable, right is evaluable → bind left to result
    if left_is_var:
        try:
            result = evaluate(right, subst)
            return subst.extend(left_walked, result)
        except EvaluatorError:
            # Right isn't numeric — try term binding
            right_resolved = subst.apply(right)
            return subst.extend(left_walked, right_resolved)

    # Right is unbound variable, left is evaluable → bind right to result
    if right_is_var:
        try:
            result = evaluate(left, subst)
            return subst.extend(right_walked, result)
        except EvaluatorError:
            left_resolved = subst.apply(left)
            return subst.extend(right_walked, left_resolved)

    # Both sides ground — check equality
    try:
        lval = evaluate(left, subst).value
        rval = evaluate(right, subst).value
        return subst if lval == rval else None
    except EvaluatorError:
        lval_t = subst.apply(left)
        rval_t = subst.apply(right)
        return subst if lval_t == rval_t else None
