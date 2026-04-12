"""Unit tests for minilog.parser."""

import pytest

from minilog.parser import (
    Comparison, Fact, Negation, Program, Query, Rule, parse,
)
from minilog.terms import Atom, Compound, Num, Str, Var
from minilog.errors import ParseError


def test_single_fact():
    """Parse a single ground fact."""
    prog = parse("батько(авраам, ісак).")
    assert len(prog.facts) == 1
    assert len(prog.rules) == 0
    assert len(prog.queries) == 0
    f = prog.facts[0]
    assert f.head.functor == "батько"
    assert f.head.args == (Atom("авраам"), Atom("ісак"))


def test_nullary_fact():
    """Parse a nullary atom-as-fact."""
    prog = parse("сонячно.")
    assert len(prog.facts) == 1
    assert prog.facts[0].head.functor == "сонячно"
    assert prog.facts[0].head.arity == 0


def test_inline_rule():
    """Parse an inline rule: правило head якщо body."""
    prog = parse("правило предок(?х, ?y) якщо батько(?х, ?y).")
    assert len(prog.rules) == 1
    r = prog.rules[0]
    assert r.head.functor == "предок"
    assert r.head.args == (Var("х"), Var("y"))
    assert len(r.body) == 1
    assert isinstance(r.body[0], Compound)
    assert r.body[0].functor == "батько"


def test_block_rule():
    """Parse a block-form rule with INDENT/DEDENT."""
    src = "правило предок(?х, ?y):\n    якщо батько(?х, ?z)\n    і предок(?z, ?y).\n"
    prog = parse(src)
    assert len(prog.rules) == 1
    r = prog.rules[0]
    assert r.head.functor == "предок"
    assert len(r.body) == 2
    assert r.body[0].functor == "батько"
    assert r.body[1].functor == "предок"


def test_query():
    """Parse a standard query."""
    prog = parse("?- предок(авраам, ?хто).")
    assert len(prog.queries) == 1
    q = prog.queries[0]
    assert q.goal.functor == "предок"
    assert q.goal.args == (Atom("авраам"), Var("хто"))
    assert q.trace is False


def test_traced_query():
    """Parse a traced query with слід keyword."""
    prog = parse("?- слід предок(авраам, йосип).")
    assert len(prog.queries) == 1
    q = prog.queries[0]
    assert q.trace is True
    assert q.goal.functor == "предок"


def test_negation_goal():
    """Parse a rule body containing negation."""
    prog = parse("правило safe(?x) якщо node(?x) і не danger(?x).")
    assert len(prog.rules) == 1
    body = prog.rules[0].body
    assert len(body) == 2
    assert isinstance(body[0], Compound)
    assert isinstance(body[1], Negation)
    assert body[1].inner.functor == "danger"


def test_comparison_goal():
    """Parse a rule with a comparison in the body."""
    prog = parse("правило дорослий(?х) якщо вік(?х, ?n) і ?n ≥ 18.")
    assert len(prog.rules) == 1
    body = prog.rules[0].body
    assert len(body) == 2
    assert isinstance(body[1], Comparison)
    assert body[1].left == Var("n")
    assert body[1].op == "≥"
    assert body[1].right == Num(18)


def test_all_comparison_operators():
    """Each comparison operator parses correctly."""
    for op_str, op_sym in [("≥", "≥"), ("≤", "≤"), (">", ">"), ("<", "<"), ("=", "="), ("≠", "≠")]:
        prog = parse(f"правило t(?x) якщо ?x {op_str} 1.")
        cmp = prog.rules[0].body[0]
        assert isinstance(cmp, Comparison)
        assert cmp.op == op_sym


def test_syntax_error_raises_parse_error():
    """Invalid syntax produces a ParseError with position."""
    with pytest.raises(ParseError) as exc_info:
        parse("батько(авраам,)")
    assert exc_info.value.line is not None
    assert exc_info.value.col is not None


def test_syntax_error_missing_dot():
    """Missing dot at end of fact raises ParseError."""
    with pytest.raises(ParseError):
        parse("батько(авраам, ісак)")


def test_full_program():
    """Parse a complete program with facts, rules, and queries."""
    src = (
        "батько(авраам, ісак).\n"
        "батько(ісак, яків).\n"
        "правило предок(?х, ?y) якщо батько(?х, ?y).\n"
        "?- предок(авраам, ?хто).\n"
    )
    prog = parse(src)
    assert len(prog.facts) == 2
    assert len(prog.rules) == 1
    assert len(prog.queries) == 1


def test_nested_compound_terms():
    """Parse nested compound terms as arguments."""
    prog = parse("f(g(a, b), h(c)).")
    assert len(prog.facts) == 1
    head = prog.facts[0].head
    assert head.functor == "f"
    assert head.arity == 2
    assert isinstance(head.args[0], Compound)
    assert head.args[0].functor == "g"
    assert isinstance(head.args[1], Compound)
    assert head.args[1].functor == "h"


def test_string_and_number_terms():
    """Parse facts with string and number arguments."""
    prog = parse('назва("привіт", 42).')
    head = prog.facts[0].head
    assert head.args[0] == Str("привіт")
    assert head.args[1] == Num(42)
