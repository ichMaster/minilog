"""Knowledge base for minilog: fact and rule storage indexed by (functor, arity)."""

from collections import defaultdict
from typing import Iterator

from minilog.parser import Fact, Rule


class KnowledgeBase:
    """Fact and rule storage, indexed by (functor, arity)."""

    def __init__(self) -> None:
        self._facts: dict[tuple[str, int], list[Fact]] = defaultdict(list)
        self._rules: dict[tuple[str, int], list[Rule]] = defaultdict(list)

    def add_fact(self, fact: Fact) -> None:
        key = (fact.head.functor, fact.head.arity)
        self._facts[key].append(fact)

    def add_rule(self, rule: Rule) -> None:
        key = (rule.head.functor, rule.head.arity)
        self._rules[key].append(rule)

    def lookup(self, functor: str, arity: int) -> tuple[list[Fact], list[Rule]]:
        key = (functor, arity)
        return (list(self._facts[key]), list(self._rules[key]))

    def remove_fact(self, fact: Fact) -> bool:
        """Remove a fact from the KB. Returns True if the fact existed and was removed."""
        key = (fact.head.functor, fact.head.arity)
        facts = self._facts[key]
        if fact in facts:
            facts.remove(fact)
            return True
        return False

    def all_facts(self) -> Iterator[Fact]:
        for facts in self._facts.values():
            yield from facts

    def stats(self) -> dict[str, int]:
        return {
            "facts": sum(len(fs) for fs in self._facts.values()),
            "rules": sum(len(rs) for rs in self._rules.values()),
            "predicates": len(set(self._facts.keys()) | set(self._rules.keys())),
        }
