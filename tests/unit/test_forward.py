"""Tests for forward chaining (saturation)."""

from minilog.forward import saturate
from minilog.kb import KnowledgeBase
from minilog.parser import Fact, Rule
from minilog.terms import Atom, Compound, Var


def _kb_with_facts_and_rules(
    facts: list[Fact], rules: list[Rule]
) -> KnowledgeBase:
    kb = KnowledgeBase()
    for f in facts:
        kb.add_fact(f)
    for r in rules:
        kb.add_rule(r)
    return kb


class TestSaturate:
    """Tests for the saturate function."""

    def test_simple_saturation(self) -> None:
        """Derive new facts from a rule and existing facts."""
        # Facts: батько(авраам, ісак)
        # Rule: предок(?x, ?y) :- батько(?x, ?y)
        # Expected: saturate derives предок(авраам, ісак)
        kb = _kb_with_facts_and_rules(
            facts=[
                Fact(head=Compound("батько", (Atom("авраам"), Atom("ісак")))),
            ],
            rules=[
                Rule(
                    head=Compound("предок", (Var("x"), Var("y"))),
                    body=[Compound("батько", (Var("x"), Var("y")))],
                ),
            ],
        )
        added = saturate(kb)
        assert added > 0
        # предок(авраам, ісак) should now be a fact
        facts, _ = kb.lookup("предок", 2)
        heads = [f.head for f in facts]
        assert Compound("предок", (Atom("авраам"), Atom("ісак"))) in heads

    def test_fixpoint_detection(self) -> None:
        """Second call to saturate returns 0 (idempotence at fixpoint)."""
        kb = _kb_with_facts_and_rules(
            facts=[
                Fact(head=Compound("батько", (Atom("авраам"), Atom("ісак")))),
            ],
            rules=[
                Rule(
                    head=Compound("предок", (Var("x"), Var("y"))),
                    body=[Compound("батько", (Var("x"), Var("y")))],
                ),
            ],
        )
        first = saturate(kb)
        assert first > 0
        second = saturate(kb)
        assert second == 0

    def test_empty_kb(self) -> None:
        """Saturating an empty KB adds nothing."""
        kb = KnowledgeBase()
        assert saturate(kb) == 0

    def test_no_rules(self) -> None:
        """KB with facts but no rules — nothing to derive."""
        kb = _kb_with_facts_and_rules(
            facts=[
                Fact(head=Compound("батько", (Atom("авраам"), Atom("ісак")))),
            ],
            rules=[],
        )
        assert saturate(kb) == 0

    def test_transitive_saturation(self) -> None:
        """Multi-step derivation across iterations."""
        # батько(а, б), батько(б, в)
        # предок(?x, ?y) :- батько(?x, ?y)
        # предок(?x, ?z) :- батько(?x, ?y), предок(?y, ?z)
        # Should derive: предок(а,б), предок(б,в), then предок(а,в)
        kb = _kb_with_facts_and_rules(
            facts=[
                Fact(head=Compound("батько", (Atom("а"), Atom("б")))),
                Fact(head=Compound("батько", (Atom("б"), Atom("в")))),
            ],
            rules=[
                Rule(
                    head=Compound("предок", (Var("x"), Var("y"))),
                    body=[Compound("батько", (Var("x"), Var("y")))],
                ),
                Rule(
                    head=Compound("предок", (Var("x"), Var("z"))),
                    body=[
                        Compound("батько", (Var("x"), Var("y"))),
                        Compound("предок", (Var("y"), Var("z"))),
                    ],
                ),
            ],
        )
        added = saturate(kb)
        assert added >= 3
        facts, _ = kb.lookup("предок", 2)
        heads = [f.head for f in facts]
        assert Compound("предок", (Atom("а"), Atom("в"))) in heads
