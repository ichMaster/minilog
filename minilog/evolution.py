"""Evolution engine — production rules that mutate the knowledge base over generations."""

from dataclasses import dataclass, field
from typing import Any

from minilog.engine import solve, solve_body
from minilog.kb import KnowledgeBase
from minilog.parser import Comparison, Fact, Negation
from minilog.terms import Compound
from minilog.unify import Substitution


@dataclass
class ProductionRule:
    """A production rule: if the condition holds, add these facts and remove those."""
    name: str
    condition: Compound
    add: list[Compound]
    remove: list[Compound]
    guard: Any = None  # Optional Comparison or Negation
    body: list | None = None  # Full condition body for conjunctive conditions


def _evaluate_guard(guard, subst: Substitution) -> bool:
    """Evaluate a guard (Comparison or Negation) under a substitution."""
    from minilog.evaluator import check_comparison

    if isinstance(guard, Comparison):
        result = check_comparison(guard.left, guard.op, guard.right, subst)
        return result is not None

    if isinstance(guard, Negation):
        # Negation-as-failure: guard succeeds if inner goal has no solutions
        try:
            next(solve(guard.inner, KnowledgeBase()))
            return False
        except StopIteration:
            return True

    return True


def run_generations(
    kb: KnowledgeBase,
    rules: list[ProductionRule],
    n: int,
    detect_fixpoint: bool = True,
    max_cap: int = 10000,
) -> list[dict]:
    """Run n generations with two-phase collect/apply semantics."""
    effective_n = min(n, max_cap)
    history: list[dict] = []

    for gen in range(effective_n):
        # Phase 1: collect all planned changes over current KB (no writes)
        planned_adds: list[Fact] = []
        planned_removes: list[Fact] = []

        for rule in rules:
            # Use body if available (conjunctive conditions), otherwise single condition
            if rule.body and len(rule.body) > 1:
                for subst in solve_body(rule.body, kb, Substitution.empty(), 0, 100):
                    if rule.guard is not None and not _evaluate_guard(rule.guard, subst):
                        continue
                    for add_term in rule.add:
                        planned_adds.append(Fact(head=subst.apply(add_term)))
                    for remove_term in rule.remove:
                        planned_removes.append(Fact(head=subst.apply(remove_term)))
            else:
                for subst in solve(rule.condition, kb):
                    if rule.guard is not None and not _evaluate_guard(rule.guard, subst):
                        continue
                    for add_term in rule.add:
                        planned_adds.append(Fact(head=subst.apply(add_term)))
                    for remove_term in rule.remove:
                        planned_removes.append(Fact(head=subst.apply(remove_term)))

        # Phase 2: apply changes atomically, deduplicated
        added: list[Fact] = []
        seen_adds: set[str] = set()
        for fact in planned_adds:
            key = repr(fact.head)
            if key in seen_adds:
                continue
            seen_adds.add(key)
            if kb.add_fact_if_new(fact):
                added.append(fact)

        removed: list[Fact] = []
        seen_removes: set[str] = set()
        for fact in planned_removes:
            key = repr(fact.head)
            if key in seen_removes:
                continue
            seen_removes.add(key)
            if kb.remove_fact(fact):
                removed.append(fact)

        history.append({"generation": gen, "added": added, "removed": removed})

        # Phase 3: fixpoint detection
        if detect_fixpoint and not added and not removed:
            break

    return history
