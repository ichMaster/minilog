"""Integration test for biology_evolution.ml example."""

import subprocess
from pathlib import Path

from minilog.engine import solve
from minilog.evolution import ProductionRule, run_generations
from minilog.kb import KnowledgeBase
from minilog.parser import Fact, parse
from minilog.terms import Atom, Compound, Var
from minilog.tracer import Tracer

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_biology_evolution_output_matches_expected() -> None:
    """minilog run examples/biology_evolution.ml output matches expected."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "biology_evolution.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "biology_evolution.expected.txt").read_text(encoding="utf-8")
    assert result.stdout == expected


def test_evolution_creates_new_species() -> None:
    """After evolution, at least one new species exists not in initial KB."""
    source = (EXAMPLES_DIR / "biology_evolution.ml").read_text(encoding="utf-8")
    program = parse(source)

    kb = KnowledgeBase()
    for fact in program.facts:
        kb.add_fact(fact)
    for rule in program.rules:
        kb.add_rule(rule)

    initial_facts = set(repr(f.head) for f in kb.all_facts())

    # Production rules: speciation — if є(?x, птах) then add є(нео_?x, птах)
    rules = [
        ProductionRule(
            name="speciation",
            condition=Compound("є", (Atom("горобець"), Atom("птах"))),
            add=[Compound("є", (Atom("нео_горобець"), Atom("птах")))],
            remove=[],
        ),
    ]
    history = run_generations(kb, rules, 10)

    # Verify new species was added
    current_facts = set(repr(f.head) for f in kb.all_facts())
    new_facts = current_facts - initial_facts
    assert len(new_facts) > 0, "Evolution should have created new facts"
    assert "є(нео_горобець, птах)" in new_facts


def test_rules_apply_to_evolved_species() -> None:
    """Original taxonomy rules still work on newly evolved species."""
    source = (EXAMPLES_DIR / "biology_evolution.ml").read_text(encoding="utf-8")
    program = parse(source)

    kb = KnowledgeBase()
    for fact in program.facts:
        kb.add_fact(fact)
    for rule in program.rules:
        kb.add_rule(rule)

    # Add a new species via evolution
    rules = [
        ProductionRule(
            name="speciation",
            condition=Compound("є", (Atom("горобець"), Atom("птах"))),
            add=[Compound("є", (Atom("нео_горобець"), Atom("птах")))],
            remove=[],
        ),
    ]
    run_generations(kb, rules, 10)

    # Query: успадковує(нео_горобець, крила) should succeed
    # because нео_горобець є птах, and птах має крила
    goal = Compound("успадковує", (Atom("нео_горобець"), Atom("крила")))
    results = list(solve(goal, kb))
    assert len(results) > 0, "New species should inherit крила via unchanged rules"


def test_evolved_species_proof_tree() -> None:
    """Proof tree for evolved species uses unchanged base rules."""
    source = (EXAMPLES_DIR / "biology_evolution.ml").read_text(encoding="utf-8")
    program = parse(source)

    kb = KnowledgeBase()
    for fact in program.facts:
        kb.add_fact(fact)
    for rule in program.rules:
        kb.add_rule(rule)

    # Evolve
    rules = [
        ProductionRule(
            name="speciation",
            condition=Compound("є", (Atom("горобець"), Atom("птах"))),
            add=[Compound("є", (Atom("нео_горобець"), Atom("птах")))],
            remove=[],
        ),
    ]
    run_generations(kb, rules, 10)

    # Trace query: успадковує(нео_горобець, крила)
    tracer = Tracer()
    goal = Compound("успадковує", (Atom("нео_горобець"), Atom("крила")))
    results = list(tracer.trace_solve(goal, kb))
    assert len(results) > 0
    _, proof = results[0]
    # The proof should use the rule-based derivation
    tree_str = proof.format_tree()
    assert "rule" in tree_str
    assert "└─" in tree_str or "├─" in tree_str
