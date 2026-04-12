"""Evolution engine — production rules that mutate the knowledge base over generations."""

from dataclasses import dataclass

from minilog.engine import solve
from minilog.kb import KnowledgeBase
from minilog.parser import Fact
from minilog.terms import Compound


@dataclass
class ProductionRule:
    """A production rule: if the condition holds, add these facts and remove those."""
    name: str
    condition: Compound
    add: list[Compound]
    remove: list[Compound]


def run_generations(
    kb: KnowledgeBase,
    rules: list[ProductionRule],
    n: int,
) -> list[dict]:
    """Run n generations of production rules. Returns a history of changes per generation."""
    history = []
    for gen in range(n):
        added: list[Fact] = []
        removed: list[Fact] = []
        for rule in rules:
            for subst in solve(rule.condition, kb):
                for add_term in rule.add:
                    new_fact = Fact(head=subst.apply(add_term))
                    if new_fact not in list(kb.all_facts()):
                        kb.add_fact(new_fact)
                        added.append(new_fact)
                for remove_term in rule.remove:
                    old_fact = Fact(head=subst.apply(remove_term))
                    if kb.remove_fact(old_fact):
                        removed.append(old_fact)
        history.append({"generation": gen, "added": added, "removed": removed})
    return history
