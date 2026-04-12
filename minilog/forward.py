"""Forward chaining (saturation) for minilog."""

from minilog.engine import solve_body
from minilog.kb import KnowledgeBase
from minilog.parser import Fact
from minilog.terms import is_ground
from minilog.unify import Substitution


def saturate(kb: KnowledgeBase, max_iterations: int = 100) -> int:
    """Apply all rules, adding new facts until a fixpoint. Return the count of added facts."""
    total_added = 0
    for _ in range(max_iterations):
        new_facts: list[Fact] = []
        for (functor, arity), rules in list(kb._rules.items()):
            for rule in rules:
                for subst in solve_body(rule.body, kb, Substitution.empty(), 0, 100):
                    instantiated = subst.apply(rule.head)
                    if is_ground(instantiated):
                        new_fact = Fact(head=instantiated)
                        if new_fact not in kb._facts[(functor, arity)]:
                            new_facts.append(new_fact)
        if not new_facts:
            break  # fixpoint reached
        for fact in new_facts:
            kb.add_fact(fact)
        total_added += len(new_facts)
    return total_added
