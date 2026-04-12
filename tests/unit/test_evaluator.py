"""Unit tests for minilog.evaluator."""

import pytest

from minilog.evaluator import check_comparison, evaluate
from minilog.errors import EvaluatorError
from minilog.terms import Atom, Num, Var
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
