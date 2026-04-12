"""Tracer and proof-tree construction for minilog."""

from dataclasses import dataclass, field
from typing import Iterator

from minilog.engine import rename_variables, solve_body
from minilog.kb import KnowledgeBase
from minilog.parser import Comparison, Fact, Goal, Negation, Rule
from minilog.terms import Compound, Term, Var
from minilog.unify import Substitution, unify


@dataclass
class ProofNode:
    """A node in a proof tree."""
    goal: Compound
    kind: str  # 'fact' | 'rule' | 'builtin' | 'negation'
    rule: Rule | None = None
    binding: Substitution | None = None
    children: list["ProofNode"] = field(default_factory=list)
    status: str = "proved"  # 'proved' | 'failed'

    def format_tree(self, indent: int = 0, prefix: str = "", is_last: bool = True) -> str:
        """Render the tree using Unicode box-drawing characters."""
        lines: list[str] = []
        if indent == 0:
            lines.append(f"{self.kind}: {self.goal}")
        else:
            connector = "└─ " if is_last else "├─ "
            lines.append(f"{prefix}{connector}{self.kind}: {self.goal}")

        for i, child in enumerate(self.children):
            is_last_child = i == len(self.children) - 1
            if indent == 0:
                child_prefix = ""
            else:
                child_prefix = prefix + ("   " if is_last else "│  ")
            lines.append(child.format_tree(
                indent=indent + 1,
                prefix=child_prefix if indent == 0 else child_prefix,
                is_last=is_last_child,
            ))

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """JSON-serializable form. Needed by Stage 3 and Stage 5."""
        return {
            "goal": repr(self.goal),
            "kind": self.kind,
            "rule": repr(self.rule) if self.rule else None,
            "binding": repr(self.binding) if self.binding else None,
            "children": [c.to_dict() for c in self.children],
            "status": self.status,
        }


class Tracer:
    """Wraps the solve engine to produce proof trees alongside substitutions."""

    def trace_solve(
        self,
        goal: Goal,
        kb: KnowledgeBase,
        subst: Substitution = Substitution.empty(),
        depth: int = 0,
        max_depth: int = 100,
    ) -> Iterator[tuple[Substitution, ProofNode]]:
        """Like solve(), but also builds a ProofNode for each successful derivation."""
        from minilog.errors import SolveError
        from minilog.evaluator import check_comparison

        if depth > max_depth:
            raise SolveError(f"Maximum recursion depth {max_depth} exceeded")

        # Comparison goal
        if isinstance(goal, Comparison):
            if check_comparison(goal.left, goal.op, goal.right, subst):
                node = ProofNode(goal=goal, kind="builtin", binding=subst)
                yield subst, node
            return

        # Negation-as-failure
        if isinstance(goal, Negation):
            try:
                next(self.trace_solve(goal.inner, kb, subst, depth + 1, max_depth))
                return  # inner succeeded → negation fails
            except StopIteration:
                node = ProofNode(goal=goal.inner, kind="negation", binding=subst)
                yield subst, node
            return

        # Standard compound goal
        assert isinstance(goal, Compound)
        facts, rules = kb.lookup(goal.functor, goal.arity)

        # Try facts
        for fact in facts:
            new_subst = unify(goal, fact.head, subst)
            if new_subst is not None:
                node = ProofNode(goal=goal, kind="fact", binding=new_subst)
                yield new_subst, node

        # Try rules
        for rule in rules:
            fresh_rule = rename_variables(rule, suffix=f"_{depth}_{id(rule)}")
            new_subst = unify(goal, fresh_rule.head, subst)
            if new_subst is None:
                continue
            yield from self._trace_body(
                fresh_rule.body, kb, new_subst, depth + 1, max_depth,
                goal, fresh_rule,
            )

    def _trace_body(
        self,
        body: list[Goal],
        kb: KnowledgeBase,
        subst: Substitution,
        depth: int,
        max_depth: int,
        head_goal: Compound,
        rule: Rule,
    ) -> Iterator[tuple[Substitution, ProofNode]]:
        """Solve a rule body while collecting child proof nodes."""
        child_proofs: list[list[ProofNode]] = []
        yield from self._trace_body_rec(
            body, kb, subst, depth, max_depth,
            head_goal, rule, [], child_proofs,
        )

    def _trace_body_rec(
        self,
        body: list[Goal],
        kb: KnowledgeBase,
        subst: Substitution,
        depth: int,
        max_depth: int,
        head_goal: Compound,
        rule: Rule,
        children_so_far: list[ProofNode],
        child_proofs: list[list[ProofNode]],
    ) -> Iterator[tuple[Substitution, ProofNode]]:
        """Recursively solve body goals, accumulating child proof nodes."""
        if not body:
            node = ProofNode(
                goal=head_goal,
                kind="rule",
                rule=rule,
                binding=subst,
                children=list(children_so_far),
            )
            yield subst, node
            return

        first, *rest = body
        for new_subst, child_node in self.trace_solve(first, kb, subst, depth, max_depth):
            yield from self._trace_body_rec(
                rest, kb, new_subst, depth, max_depth,
                head_goal, rule, children_so_far + [child_node], child_proofs,
            )
