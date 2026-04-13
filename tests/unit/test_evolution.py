"""Tests for the evolution engine (production rules)."""

from minilog.evolution import ProductionRule, run_generations
from minilog.kb import KnowledgeBase
from minilog.parser import Fact
from minilog.terms import Atom, Compound, Var


def _kb_with_facts(facts: list[Fact]) -> KnowledgeBase:
    kb = KnowledgeBase()
    for f in facts:
        kb.add_fact(f)
    return kb


class TestEvolution:
    """Tests for the run_generations function."""

    def test_add_only_rule(self) -> None:
        """A rule that only adds facts."""
        # If батько(?x, ?y) then add предок(?x, ?y)
        kb = _kb_with_facts([
            Fact(head=Compound("батько", (Atom("авраам"), Atom("ісак")))),
        ])
        rule = ProductionRule(
            name="promote",
            condition=Compound("батько", (Var("x"), Var("y"))),
            add=[Compound("предок", (Var("x"), Var("y")))],
            remove=[],
        )
        history = run_generations(kb, [rule], 1)
        assert len(history) == 1
        assert len(history[0]["added"]) == 1
        assert history[0]["added"][0].head == Compound("предок", (Atom("авраам"), Atom("ісак")))
        assert history[0]["removed"] == []

    def test_remove_only_rule(self) -> None:
        """A rule that only removes facts."""
        # If застарілий(?x) then remove активний(?x)
        kb = _kb_with_facts([
            Fact(head=Compound("застарілий", (Atom("а"),))),
            Fact(head=Compound("активний", (Atom("а"),))),
        ])
        rule = ProductionRule(
            name="deactivate",
            condition=Compound("застарілий", (Var("x"),)),
            add=[],
            remove=[Compound("активний", (Var("x"),))],
        )
        history = run_generations(kb, [rule], 1)
        assert len(history[0]["removed"]) == 1
        assert history[0]["removed"][0].head == Compound("активний", (Atom("а"),))
        assert history[0]["added"] == []
        # Verify it's actually gone from KB
        facts, _ = kb.lookup("активний", 1)
        assert len(facts) == 0

    def test_mixed_rule(self) -> None:
        """A rule that both adds and removes facts."""
        # If стан(?x, молодий) then add стан(?x, дорослий), remove стан(?x, молодий)
        kb = _kb_with_facts([
            Fact(head=Compound("стан", (Atom("а"), Atom("молодий")))),
        ])
        rule = ProductionRule(
            name="age",
            condition=Compound("стан", (Var("x"), Atom("молодий"))),
            add=[Compound("стан", (Var("x"), Atom("дорослий")))],
            remove=[Compound("стан", (Var("x"), Atom("молодий")))],
        )
        history = run_generations(kb, [rule], 1)
        assert len(history[0]["added"]) == 1
        assert len(history[0]["removed"]) == 1
        # молодий gone, дорослий present
        facts, _ = kb.lookup("стан", 2)
        heads = [f.head for f in facts]
        assert Compound("стан", (Atom("а"), Atom("дорослий"))) in heads
        assert Compound("стан", (Atom("а"), Atom("молодий"))) not in heads

    def test_termination_after_n_generations(self) -> None:
        """Running N generations produces exactly N history entries."""
        kb = _kb_with_facts([
            Fact(head=Compound("батько", (Atom("а"), Atom("б")))),
        ])
        rule = ProductionRule(
            name="noop",
            condition=Compound("батько", (Var("x"), Var("y"))),
            add=[Compound("предок", (Var("x"), Var("y")))],
            remove=[],
        )
        history = run_generations(kb, [rule], 3, detect_fixpoint=False)
        assert len(history) == 3

    def test_cumulative_state_over_3_generations(self) -> None:
        """Running a mutation rule 3 times — fixpoint stops early."""
        kb = _kb_with_facts([
            Fact(head=Compound("існує", (Atom("а"),))),
            Fact(head=Compound("існує", (Atom("б"),))),
        ])
        rule = ProductionRule(
            name="mark",
            condition=Compound("існує", (Var("x"),)),
            add=[Compound("позначено", (Var("x"),))],
            remove=[],
        )
        history = run_generations(kb, [rule], 3)
        # First generation adds позначено(а) and позначено(б)
        assert len(history[0]["added"]) == 2
        # Second: no new facts → fixpoint, stops early
        assert len(history) == 2
        assert len(history[1]["added"]) == 0
        # KB should have 4 facts total
        all_facts = list(kb.all_facts())
        assert len(all_facts) == 4
