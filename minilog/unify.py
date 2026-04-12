"""Substitution and Robinson's unification algorithm for minilog."""

from dataclasses import dataclass

from minilog.terms import Atom, Compound, Num, Str, Term, Var


@dataclass(frozen=True)
class Substitution:
    """Immutable mapping from variables to terms."""
    bindings: tuple[tuple[Var, Term], ...]

    @classmethod
    def empty(cls) -> "Substitution":
        return cls(())

    def extend(self, var: Var, term: Term) -> "Substitution":
        return Substitution(self.bindings + ((var, term),))

    def lookup(self, var: Var) -> Term | None:
        for v, t in self.bindings:
            if v == var:
                return t
        return None

    def apply(self, term: Term) -> Term:
        """Recursively resolve all variables in term against this substitution."""
        term = walk(term, self)
        if isinstance(term, Compound):
            return Compound(
                functor=term.functor,
                args=tuple(self.apply(a) for a in term.args),
            )
        return term

    def __repr__(self) -> str:
        if not self.bindings:
            return "Substitution({})"
        pairs = ", ".join(f"{v!r} = {t!r}" for v, t in self.bindings)
        return f"Substitution({{{pairs}}})"


def walk(term: Term, subst: Substitution) -> Term:
    """Dereference a variable chain until we hit a non-var or an unbound var."""
    while isinstance(term, Var):
        value = subst.lookup(term)
        if value is None:
            return term
        term = value
    return term


def unify(t1: Term, t2: Term, subst: Substitution) -> Substitution | None:
    """Attempt to unify t1 and t2. Return an extended substitution, or None on failure."""
    t1 = walk(t1, subst)
    t2 = walk(t2, subst)

    if t1 == t2:
        return subst

    if isinstance(t1, Var):
        return subst.extend(t1, t2)

    if isinstance(t2, Var):
        return subst.extend(t2, t1)

    if isinstance(t1, Compound) and isinstance(t2, Compound):
        if t1.functor != t2.functor or t1.arity != t2.arity:
            return None
        for a1, a2 in zip(t1.args, t2.args):
            subst = unify(a1, a2, subst)
            if subst is None:
                return None
        return subst

    # Atom, Num, Str — must match exactly, already handled by equality check
    return None
