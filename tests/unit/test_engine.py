"""Unit tests for minilog.engine."""

import pytest

from minilog.engine import rename_variables, solve, solve_body
from minilog.errors import SolveError
from minilog.evaluator import check_comparison
from minilog.kb import KnowledgeBase
from minilog.parser import Comparison, Fact, Negation, Rule
from minilog.terms import Atom, Compound, Num, Var
from minilog.unify import Substitution


def _make_family_kb() -> KnowledgeBase:
    """Build a KB with батько facts and предок rules."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("батько", (Atom("авраам"), Atom("ісак")))))
    kb.add_fact(Fact(Compound("батько", (Atom("ісак"), Atom("яків")))))
    # предок(?x, ?y) :- батько(?x, ?y).
    kb.add_rule(Rule(
        head=Compound("предок", (Var("x"), Var("y"))),
        body=[Compound("батько", (Var("x"), Var("y")))],
    ))
    # предок(?x, ?y) :- батько(?x, ?z), предок(?z, ?y).
    kb.add_rule(Rule(
        head=Compound("предок", (Var("x"), Var("y"))),
        body=[
            Compound("батько", (Var("x"), Var("z"))),
            Compound("предок", (Var("z"), Var("y"))),
        ],
    ))
    return kb


def test_single_fact_solve():
    """Solve a goal that matches a single fact."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("батько", (Atom("авраам"), Atom("ісак")))))

    goal = Compound("батько", (Atom("авраам"), Var("хто")))
    solutions = list(solve(goal, kb))
    assert len(solutions) == 1
    assert solutions[0].apply(Var("хто")) == Atom("ісак")


def test_single_rule_solve():
    """Solve a goal that requires one rule application."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("батько", (Atom("авраам"), Atom("ісак")))))
    kb.add_rule(Rule(
        head=Compound("предок", (Var("x"), Var("y"))),
        body=[Compound("батько", (Var("x"), Var("y")))],
    ))

    goal = Compound("предок", (Atom("авраам"), Var("хто")))
    solutions = list(solve(goal, kb))
    assert len(solutions) == 1
    assert solutions[0].apply(Var("хто")) == Atom("ісак")


def test_recursive_rule():
    """Solve a goal requiring recursive rule application."""
    kb = _make_family_kb()

    goal = Compound("предок", (Atom("авраам"), Var("хто")))
    solutions = list(solve(goal, kb))
    names = {s.apply(Var("хто")) for s in solutions}
    assert names == {Atom("ісак"), Atom("яків")}


def test_multi_solution_backtracking():
    """Multiple facts yield multiple solutions via backtracking."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("color", (Atom("red"),))))
    kb.add_fact(Fact(Compound("color", (Atom("green"),))))
    kb.add_fact(Fact(Compound("color", (Atom("blue"),))))

    goal = Compound("color", (Var("c"),))
    solutions = list(solve(goal, kb))
    assert len(solutions) == 3
    colors = {s.apply(Var("c")) for s in solutions}
    assert colors == {Atom("red"), Atom("green"), Atom("blue")}


def test_negation_success():
    """Negation succeeds when inner goal has no solutions."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("safe", (Atom("a"),))))
    # danger is not defined → не danger(a) should succeed

    goal = Negation(inner=Compound("danger", (Atom("a"),)))
    solutions = list(solve(goal, kb))
    assert len(solutions) == 1


def test_negation_failure():
    """Negation fails when inner goal has solutions."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("danger", (Atom("a"),))))

    goal = Negation(inner=Compound("danger", (Atom("a"),)))
    solutions = list(solve(goal, kb))
    assert len(solutions) == 0


def test_comparison_goal():
    """Comparison goals are handled correctly."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("вік", (Atom("петро"), Num(25)))))
    # дорослий(?x) :- вік(?x, ?n), ?n ≥ 18
    kb.add_rule(Rule(
        head=Compound("дорослий", (Var("x"),)),
        body=[
            Compound("вік", (Var("x"), Var("n"))),
            Comparison(left=Var("n"), op="≥", right=Num(18)),
        ],
    ))

    goal = Compound("дорослий", (Var("хто"),))
    solutions = list(solve(goal, kb))
    assert len(solutions) == 1
    assert solutions[0].apply(Var("хто")) == Atom("петро")


def test_comparison_goal_fails():
    """Comparison goal fails when condition is not met."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("вік", (Atom("дитя"), Num(5)))))
    kb.add_rule(Rule(
        head=Compound("дорослий", (Var("x"),)),
        body=[
            Compound("вік", (Var("x"), Var("n"))),
            Comparison(left=Var("n"), op="≥", right=Num(18)),
        ],
    ))

    goal = Compound("дорослий", (Var("хто"),))
    solutions = list(solve(goal, kb))
    assert len(solutions) == 0


def test_max_depth_trip():
    """Exceeding MAX_DEPTH raises SolveError."""
    kb = KnowledgeBase()
    # Infinite recursion: loop(?x) :- loop(?x).
    kb.add_rule(Rule(
        head=Compound("loop", (Var("x"),)),
        body=[Compound("loop", (Var("x"),))],
    ))

    goal = Compound("loop", (Atom("a"),))
    with pytest.raises(SolveError, match="Maximum recursion depth"):
        list(solve(goal, kb, max_depth=10))


def test_missing_predicate():
    """A goal with no matching facts or rules yields no solutions."""
    kb = KnowledgeBase()
    goal = Compound("nonexistent", (Atom("a"),))
    solutions = list(solve(goal, kb))
    assert solutions == []


def test_body_with_multiple_goals():
    """Solving a body with multiple conjuncts works."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("a", (Atom("x"),))))
    kb.add_fact(Fact(Compound("b", (Atom("x"),))))

    body = [Compound("a", (Var("v"),)), Compound("b", (Var("v"),))]
    solutions = list(solve_body(body, kb, Substitution.empty(), 0, 100))
    assert len(solutions) == 1
    assert solutions[0].apply(Var("v")) == Atom("x")


def test_solve_returns_iterator():
    """solve returns a generator, not a list."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("a", (Atom("x"),))))
    result = solve(Compound("a", (Var("v"),)), kb)
    import types
    assert isinstance(result, types.GeneratorType)


def test_rename_variables():
    """rename_variables produces fresh variable names."""
    rule = Rule(
        head=Compound("f", (Var("x"), Var("y"))),
        body=[Compound("g", (Var("x"), Var("z")))],
    )
    fresh = rename_variables(rule, "_0")
    assert fresh.head.args[0] == Var("x_0")
    assert fresh.head.args[1] == Var("y_0")
    assert fresh.body[0].args[1] == Var("z_0")


def test_nullary_fact():
    """Nullary compounds (atoms-as-facts) can be solved."""
    kb = KnowledgeBase()
    kb.add_fact(Fact(Compound("сонячно", ())))

    solutions = list(solve(Compound("сонячно", ()), kb))
    assert len(solutions) == 1
