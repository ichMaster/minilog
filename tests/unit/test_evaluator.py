"""Unit tests for minilog.evaluator."""

import pytest

from minilog.evaluator import check_comparison, evaluate
from minilog.errors import EvaluatorError
from minilog.terms import Atom, Compound, Num, Var
from minilog.unify import Substitution


def test_evaluate_num():
    """A Num term evaluates to itself."""
    result = evaluate(Num(42), Substitution.empty())
    assert result == Num(42)


def test_evaluate_var_resolved():
    """A variable bound to a Num evaluates to that Num."""
    s = Substitution.empty().extend(Var("n"), Num(18))
    result = evaluate(Var("n"), s)
    assert result == Num(18)


def test_evaluate_non_numeric_raises():
    """A non-numeric term raises EvaluatorError."""
    with pytest.raises(EvaluatorError):
        evaluate(Atom("hello"), Substitution.empty())


def test_evaluate_unbound_var_raises():
    """An unbound variable raises EvaluatorError."""
    with pytest.raises(EvaluatorError):
        evaluate(Var("x"), Substitution.empty())


def test_comparisons():
    """All comparison operators work correctly."""
    s = Substitution.empty()
    assert check_comparison(Num(5), ">", Num(3), s) is True
    assert check_comparison(Num(3), ">", Num(5), s) is False
    assert check_comparison(Num(5), "<", Num(3), s) is False
    assert check_comparison(Num(3), "<", Num(5), s) is True
    assert check_comparison(Num(5), "≥", Num(5), s) is True
    assert check_comparison(Num(5), "≥", Num(3), s) is True
    assert check_comparison(Num(3), "≤", Num(5), s) is True
    assert check_comparison(Num(5), "≤", Num(5), s) is True
    assert check_comparison(Num(5), "=", Num(5), s) is True
    assert check_comparison(Num(5), "=", Num(3), s) is False
    assert check_comparison(Num(5), "≠", Num(3), s) is True
    assert check_comparison(Num(5), "≠", Num(5), s) is False


def test_comparison_with_variables():
    """Comparisons resolve variables before comparing."""
    s = Substitution.empty().extend(Var("n"), Num(18))
    assert check_comparison(Var("n"), "≥", Num(18), s) is True
    assert check_comparison(Var("n"), ">", Num(17), s) is True


def test_comparison_non_numeric_raises():
    """Comparing a non-numeric term raises EvaluatorError."""
    with pytest.raises(EvaluatorError):
        check_comparison(Atom("hello"), ">", Num(3), Substitution.empty())


def test_float_comparison():
    """Float comparisons work correctly."""
    s = Substitution.empty()
    assert check_comparison(Num(3.14), ">", Num(3), s) is True
    assert check_comparison(Num(2.71), "<", Num(3.14), s) is True


# -- Compound arithmetic tests --

def test_addition():
    """3 + 4 = 7."""
    expr = Compound("+", (Num(3), Num(4)))
    assert evaluate(expr, Substitution.empty()) == Num(7)


def test_nested_expression():
    """3 + 4 * 5 = 23."""
    expr = Compound("+", (Num(3), Compound("*", (Num(4), Num(5)))))
    assert evaluate(expr, Substitution.empty()) == Num(23)


def test_division_float():
    """10 / 4 = 2.5."""
    expr = Compound("/", (Num(10), Num(4)))
    assert evaluate(expr, Substitution.empty()) == Num(2.5)


def test_division_by_zero():
    """Division by zero raises EvaluatorError."""
    expr = Compound("/", (Num(1), Num(0)))
    with pytest.raises(EvaluatorError, match="division by zero"):
        evaluate(expr, Substitution.empty())


def test_unary_minus():
    """-5 evaluates to -5."""
    expr = Compound("-", (Num(5),))
    assert evaluate(expr, Substitution.empty()) == Num(-5)


def test_sqrt():
    """sqrt(16) = 4.0."""
    expr = Compound("sqrt", (Num(16),))
    assert evaluate(expr, Substitution.empty()) == Num(4.0)


def test_sqrt_negative():
    """sqrt(-1) raises EvaluatorError."""
    expr = Compound("sqrt", (Num(-1),))
    with pytest.raises(EvaluatorError, match="sqrt of negative"):
        evaluate(expr, Substitution.empty())


def test_pow_int():
    """pow(2, 10) = 1024 (integer preserved)."""
    expr = Compound("pow", (Num(2), Num(10)))
    result = evaluate(expr, Substitution.empty())
    assert result == Num(1024)
    assert isinstance(result.value, int)


def test_abs():
    """abs(-7) = 7."""
    expr = Compound("abs", (Num(-7),))
    assert evaluate(expr, Substitution.empty()) == Num(7)


def test_unknown_function():
    """Unknown function raises EvaluatorError."""
    expr = Compound("log", (Num(10),))
    with pytest.raises(EvaluatorError, match="unknown arithmetic function"):
        evaluate(expr, Substitution.empty())
