"""Unit tests for minilog.kb."""

from minilog.kb import KnowledgeBase
from minilog.parser import Fact, Rule
from minilog.terms import Atom, Compound, Var


def _fact(functor: str, *args: str) -> Fact:
    return Fact(head=Compound(functor, tuple(Atom(a) for a in args)))


def _rule(functor: str, body_functor: str) -> Rule:
    return Rule(
        head=Compound(functor, (Var("x"), Var("y"))),
        body=[Compound(body_functor, (Var("x"), Var("y")))],
    )


def test_add_and_lookup():
    """Facts and rules are retrievable by functor/arity."""
    kb = KnowledgeBase()
    f = _fact("батько", "авраам", "ісак")
    r = _rule("предок", "батько")
    kb.add_fact(f)
    kb.add_rule(r)

    facts, rules = kb.lookup("батько", 2)
    assert len(facts) == 1
    assert facts[0] == f

    facts2, rules2 = kb.lookup("предок", 2)
    assert len(rules2) == 1
    assert rules2[0] == r


def test_multiple_predicates():
    """Multiple facts for different predicates are stored separately."""
    kb = KnowledgeBase()
    f1 = _fact("батько", "авраам", "ісак")
    f2 = _fact("мати", "сара", "ісак")
    kb.add_fact(f1)
    kb.add_fact(f2)

    facts1, _ = kb.lookup("батько", 2)
    facts2, _ = kb.lookup("мати", 2)
    assert len(facts1) == 1
    assert len(facts2) == 1


def test_lookup_unknown_predicate():
    """Looking up an unknown predicate returns empty lists, not an error."""
    kb = KnowledgeBase()
    facts, rules = kb.lookup("nonexistent", 1)
    assert facts == []
    assert rules == []


def test_remove_fact():
    """remove_fact removes a fact and returns True; returns False if not found."""
    kb = KnowledgeBase()
    f = _fact("батько", "авраам", "ісак")
    kb.add_fact(f)
    assert kb.remove_fact(f) is True
    assert kb.remove_fact(f) is False

    facts, _ = kb.lookup("батько", 2)
    assert facts == []


def test_all_facts():
    """all_facts yields every fact across all predicates."""
    kb = KnowledgeBase()
    f1 = _fact("батько", "авраам", "ісак")
    f2 = _fact("мати", "сара", "ісак")
    kb.add_fact(f1)
    kb.add_fact(f2)

    all_f = list(kb.all_facts())
    assert len(all_f) == 2
    assert f1 in all_f
    assert f2 in all_f


def test_stats():
    """stats reports correct counts."""
    kb = KnowledgeBase()
    kb.add_fact(_fact("батько", "авраам", "ісак"))
    kb.add_fact(_fact("батько", "ісак", "яків"))
    kb.add_rule(_rule("предок", "батько"))

    s = kb.stats()
    assert s["facts"] == 2
    assert s["rules"] == 1
    assert s["predicates"] == 2  # батько/2 and предок/2
