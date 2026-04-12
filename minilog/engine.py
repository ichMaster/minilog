"""Backward-chaining engine (SLD resolution) for minilog."""

import itertools
from typing import Iterator

from minilog.errors import SolveError
from minilog.evaluator import check_comparison
from minilog.kb import KnowledgeBase
from minilog.parser import Comparison, Fact, Goal, Negation, Rule
from minilog.terms import Compound, Term, Var
from minilog.unify import Substitution, unify

_rename_counter = itertools.count()


def solve(
    goal: Goal,
    kb: KnowledgeBase,
    subst: Substitution = Substitution.empty(),
    depth: int = 0,
    max_depth: int = 100,
) -> Iterator[Substitution]:
    """Solve a goal against the KB, yielding each successful substitution."""
    if depth > max_depth:
        raise SolveError(f"Maximum recursion depth {max_depth} exceeded")

    # Comparison goal: delegate to evaluator
    if isinstance(goal, Comparison):
        if check_comparison(goal.left, goal.op, goal.right, subst):
            yield subst
        return

    # Negation-as-failure
    if isinstance(goal, Negation):
        try:
            next(solve(goal.inner, kb, subst, depth + 1, max_depth))
            return  # inner goal succeeded → negation fails
        except StopIteration:
            yield subst  # inner goal failed → negation succeeds
        return

    # Standard compound goal
    assert isinstance(goal, Compound)
    facts, rules = kb.lookup(goal.functor, goal.arity)

    # Try facts first
    for fact in facts:
        new_subst = unify(goal, fact.head, subst)
        if new_subst is not None:
            yield new_subst

    # Then try rules
    for rule in rules:
        fresh_rule = rename_variables(rule, suffix=f"_{next(_rename_counter)}")
        new_subst = unify(goal, fresh_rule.head, subst)
        if new_subst is None:
            continue
        yield from solve_body(fresh_rule.body, kb, new_subst, depth + 1, max_depth)


def solve_body(
    body: list[Goal],
    kb: KnowledgeBase,
    subst: Substitution,
    depth: int,
    max_depth: int,
) -> Iterator[Substitution]:
    """Solve a conjunction of goals (the body of a rule)."""
    if not body:
        yield subst
        return
    first, *rest = body
    for new_subst in solve(first, kb, subst, depth, max_depth):
        yield from solve_body(rest, kb, new_subst, depth, max_depth)


def rename_variables(rule: Rule, suffix: str) -> Rule:
    """Produce a copy of the rule with all variables renamed with a unique suffix."""
    return Rule(
        head=_rename_term(rule.head, suffix),
        body=[_rename_goal(g, suffix) for g in rule.body],
    )


def _rename_term(term: Term, suffix: str) -> Term:
    """Recursively rename all variables in a term."""
    if isinstance(term, Var):
        if term.name == "_":
            # Anonymous variables get unique names each time
            return Var(f"_{suffix}")
        return Var(f"{term.name}{suffix}")
    if isinstance(term, Compound):
        return Compound(
            functor=term.functor,
            args=tuple(_rename_term(a, suffix) for a in term.args),
        )
    return term  # Atom, Num, Str are unchanged


def _rename_goal(goal: Goal, suffix: str) -> Goal:
    """Rename variables in a goal."""
    if isinstance(goal, Compound):
        return _rename_term(goal, suffix)
    if isinstance(goal, Negation):
        return Negation(inner=_rename_term(goal.inner, suffix))
    if isinstance(goal, Comparison):
        return Comparison(
            left=_rename_term(goal.left, suffix),
            op=goal.op,
            right=_rename_term(goal.right, suffix),
        )
    return goal
