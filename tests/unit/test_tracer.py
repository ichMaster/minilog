"""Tests for tracer and proof trees."""

from minilog.kb import KnowledgeBase
from minilog.parser import Fact, Rule
from minilog.terms import Atom, Compound, Var
from minilog.tracer import ProofNode, Tracer
from minilog.unify import Substitution


def _kb_with(facts: list[Fact], rules: list[Rule]) -> KnowledgeBase:
    kb = KnowledgeBase()
    for f in facts:
        kb.add_fact(f)
    for r in rules:
        kb.add_rule(r)
    return kb


class TestTracer:
    """Tests for the Tracer class."""

    def test_proof_node_for_fact(self) -> None:
        """A simple fact query produces a 'fact' proof node."""
        kb = _kb_with(
            facts=[Fact(head=Compound("батько", (Atom("авраам"), Atom("ісак"))))],
            rules=[],
        )
        tracer = Tracer()
        results = list(tracer.trace_solve(
            Compound("батько", (Atom("авраам"), Atom("ісак"))), kb,
        ))
        assert len(results) == 1
        subst, node = results[0]
        assert node.kind == "fact"
        assert node.goal == Compound("батько", (Atom("авраам"), Atom("ісак")))
        assert node.children == []

    def test_proof_node_for_rule(self) -> None:
        """A rule application produces a 'rule' proof node with children."""
        kb = _kb_with(
            facts=[Fact(head=Compound("батько", (Atom("авраам"), Atom("ісак"))))],
            rules=[
                Rule(
                    head=Compound("предок", (Var("x"), Var("y"))),
                    body=[Compound("батько", (Var("x"), Var("y")))],
                ),
            ],
        )
        tracer = Tracer()
        results = list(tracer.trace_solve(
            Compound("предок", (Atom("авраам"), Atom("ісак"))), kb,
        ))
        assert len(results) == 1
        subst, node = results[0]
        assert node.kind == "rule"
        assert node.rule is not None
        assert len(node.children) == 1
        assert node.children[0].kind == "fact"

    def test_nested_proof_tree(self) -> None:
        """A 3-level recursive derivation produces a nested proof tree."""
        # батько(а, б), батько(б, в)
        # предок(?x, ?y) :- батько(?x, ?y)
        # предок(?x, ?z) :- батько(?x, ?y), предок(?y, ?z)
        # Query: предок(а, в) → rule → батько(а, б) + предок(б, в) → rule → батько(б, в)
        kb = _kb_with(
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
        tracer = Tracer()
        goal = Compound("предок", (Atom("а"), Atom("в")))
        results = list(tracer.trace_solve(goal, kb))
        # Should have at least one result via the transitive rule
        # Find the one with nested children (rule → rule)
        deep_results = [r for r in results if r[1].kind == "rule" and any(
            c.kind == "rule" for c in r[1].children
        )]
        assert len(deep_results) >= 1
        _, node = deep_results[0]
        # node is rule, one child is fact (батько), another is rule (предок)
        assert node.kind == "rule"
        rule_children = [c for c in node.children if c.kind == "rule"]
        assert len(rule_children) >= 1

    def test_to_dict_round_trip(self) -> None:
        """to_dict produces valid JSON-serializable output."""
        kb = _kb_with(
            facts=[Fact(head=Compound("батько", (Atom("авраам"), Atom("ісак"))))],
            rules=[
                Rule(
                    head=Compound("предок", (Var("x"), Var("y"))),
                    body=[Compound("батько", (Var("x"), Var("y")))],
                ),
            ],
        )
        tracer = Tracer()
        results = list(tracer.trace_solve(
            Compound("предок", (Atom("авраам"), Atom("ісак"))), kb,
        ))
        _, node = results[0]
        d = node.to_dict()
        assert d["kind"] == "rule"
        assert d["status"] == "proved"
        assert isinstance(d["goal"], str)
        assert isinstance(d["children"], list)
        assert len(d["children"]) == 1
        assert d["children"][0]["kind"] == "fact"

    def test_format_tree_box_drawing(self) -> None:
        """format_tree uses Unicode box-drawing characters."""
        kb = _kb_with(
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
        tracer = Tracer()
        goal = Compound("предок", (Atom("а"), Atom("в")))
        results = list(tracer.trace_solve(goal, kb))
        deep_results = [r for r in results if r[1].kind == "rule" and any(
            c.kind == "rule" for c in r[1].children
        )]
        assert len(deep_results) >= 1
        _, node = deep_results[0]
        tree_str = node.format_tree()
        # Should contain box-drawing characters
        assert "├─" in tree_str or "└─" in tree_str
        # Should have multiple lines
        assert tree_str.count("\n") >= 2
