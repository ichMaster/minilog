# minilog Stage 1 — Technical Specification

**Project:** minilog (a mini-Prolog engine with Ukrainian-language syntax)
**Stage:** Stage 1 of a five-stage roadmap
**Location:** `/Users/Vitalii_Bondarenko2/development/minilog/`
**Implementation language:** Python 3.11+
**Runtime dependencies:** stdlib only
**Dev dependencies:** `pytest`, `pytest-cov`
**Status:** ready to hand off to Claude Code for implementation
**Author:** Vitalii Bondarenko
**Date:** April 2026

---

## Table of Contents

1. Purpose and Principles
2. How It Works (end-to-end walkthrough)
3. Architecture
4. Language Grammar
5. Data Models
6. Algorithms
7. CLI and REPL
8. Example Files (9 examples)
9. Testing Strategy
10. Task List for Claude Code (MINILOG-001..MINILOG-017)
11. Task Dependency Graph
12. Stage 1 Completion Criteria
13. What Comes Next

---

## 1. Purpose and Principles

**Goal of Stage 1:** build a working logic-programming engine with Ukrainian-language surface syntax that can execute classical Prolog-style queries against nine teaching examples and produce interpretable proof trees. This is a learning prototype, not a production tool.

**Implementation principles:**

- **Readability beats performance.** Code must be obvious to a person who reopens it in six months.
- **Minimalism.** No optimizations that complicate the code. No memoization, no first-argument indexing, no transition tables. Only what the nine examples actually require.
- **Stdlib only at runtime.** No third-party runtime dependencies. `pytest` is dev-only.
- **Type hints everywhere.** Every public function and method has a full type signature.
- **Pure functions for algorithms.** `unify`, `solve`, `forward_chain` have no side effects except the explicit KB mutation inside the evolution engine.
- **Immutable data structures where possible.** `Term` and its subclasses are frozen dataclasses. `Substitution` is a frozen wrapper around a mapping.
- **Error messages in English, domain vocabulary in Ukrainian.** User-facing `.ml` syntax is Ukrainian; CLI/REPL messages, Python code, docstrings, and parser errors are English.

---

## 2. How It Works

This section walks the full life cycle from a `.ml` file on disk to printed query output. The goal is to give the reader (Claude Code, or you in six months) intuition for how the pieces fit together before diving into module details.

### 2.1. Input

You have a file `examples/family.ml` with this content:

```
батько(авраам, ісак).
батько(ісак, яків).

правило предок(?х, ?y) якщо батько(?х, ?y).
правило предок(?х, ?y):
    якщо батько(?х, ?z)
    і предок(?z, ?y).

?- предок(авраам, ?хто).
```

You run `minilog run examples/family.ml`.

### 2.2. Step 1 — Lexing

The CLI reads the file as UTF-8 text and hands the string to `Lexer`. The lexer scans character by character and emits a stream of tokens:

```
IDENT('батько') LPAREN IDENT('авраам') COMMA IDENT('ісак') RPAREN DOT
IDENT('батько') LPAREN IDENT('ісак') COMMA IDENT('яків') RPAREN DOT
KW_RULE IDENT('предок') LPAREN VAR('х') COMMA VAR('y') RPAREN
  KW_IF IDENT('батько') LPAREN VAR('х') COMMA VAR('y') RPAREN DOT
...
QUERY_START IDENT('предок') LPAREN IDENT('авраам') COMMA VAR('хто') RPAREN DOT
```

Key points:

- The lexer recognizes Ukrainian keywords: `факт`, `правило`, `якщо`, `і`, `не`, `слід`
- Variables are identified by the `?` prefix: `?х`, `?хто`, `?_`
- `% ...` comments are discarded entirely
- Math operators `≥`, `≤`, `>`, `<`, `=`, `≠` are emitted as dedicated tokens
- Both inline-rule form and indented block-rule form are supported (the lexer emits `INDENT`/`DEDENT` tokens for block form)
- Identifiers are Unicode-aware and accept any letter from Unicode category `L*`

### 2.3. Step 2 — Parsing

`Parser` transforms the token list into an AST. For our example:

```python
Program(
    facts=[
        Fact(Compound("батько", (Atom("авраам"), Atom("ісак")))),
        Fact(Compound("батько", (Atom("ісак"), Atom("яків")))),
    ],
    rules=[
        Rule(
            head=Compound("предок", (Var("х"), Var("y"))),
            body=[Compound("батько", (Var("х"), Var("y")))],
        ),
        Rule(
            head=Compound("предок", (Var("х"), Var("y"))),
            body=[
                Compound("батько", (Var("х"), Var("z"))),
                Compound("предок", (Var("z"), Var("y"))),
            ],
        ),
    ],
    queries=[
        Query(goal=Compound("предок", (Atom("авраам"), Var("хто"))), trace=False),
    ],
)
```

The parser enforces syntactic correctness but does **not** perform semantic checks — it will not verify that `батько/2` is defined anywhere. Missing predicates surface later during execution as `predicate X/N not found` errors.

### 2.4. Step 3 — Loading into the Knowledge Base

The interpreter walks the AST and routes each node:

- Facts and rules are inserted into `KnowledgeBase`, keyed by `(functor, arity)`
- Queries are collected into a separate list for execution

After loading, the KB looks (conceptually) like:

```
KB:
  батько/2 → [
    Fact(батько(авраам, ісак)),
    Fact(батько(ісак, яків)),
  ]
  предок/2 → [
    Rule(предок(?х, ?y) :- батько(?х, ?y)),
    Rule(предок(?х, ?y) :- батько(?х, ?z), предок(?z, ?y)),
  ]

Queries:
  [предок(авраам, ?хто)]
```

### 2.5. Step 4 — Executing a query via backward chaining

For each query the CLI calls `engine.solve(goal, kb)`, which returns a **generator of solutions** — a lazy sequence of `Substitution` objects, each of which is a valid binding of the query's variables to ground terms.

For the query `предок(авраам, ?хто)`, the engine:

1. Looks up all facts and rules for predicate `предок/2` in the KB
2. Tries the first rule: `предок(?х, ?y) :- батько(?х, ?y)`
3. Unifies the rule head `предок(?х, ?y)` with the query `предок(авраам, ?хто)`, producing `{?х=авраам, ?y=?хто}`
4. Applies the substitution to the body: `батько(авраам, ?хто)`
5. Recursively solves `батько(авраам, ?хто)` — finds fact `батько(авраам, ісак)`, unifies, produces `{?хто=ісак}`
6. Yields the first solution: `?хто = ісак`
7. Backtracks to try the second rule: `предок(?х, ?y) :- батько(?х, ?z), предок(?z, ?y)`
8. Unifies, solves `батько(авраам, ?z)` → `?z=ісак`, then recursively solves `предок(ісак, ?хто)` → finds `?хто=яків`
9. Yields the second solution: `?хто = яків`
10. No more solutions; the generator is exhausted

### 2.6. Step 5 — Formatting and printing

The CLI collects all solutions from the generator and formats them:

```
?- предок(авраам, ?хто).
?хто = ісак.
?хто = яків.
(2 solutions)
```

If a query is prefixed with `слід` (e.g., `?- слід предок(авраам, йосип).`), the engine is instead invoked through `Tracer`, which constructs a `ProofNode` tree for each successful derivation. The tree is then rendered with Unicode box-drawing characters for the REPL output.

### 2.7. Key Invariants

- **Generators, not lists.** The engine returns `Iterator[Substitution]`, not `List[Substitution]`. This enables lazy evaluation and early termination (e.g., the REPL asking for at most `N` solutions).
- **Fresh variables per rule application.** When a rule is applied, its variables are renamed with a unique suffix so they do not collide with query variables or with earlier applications of the same rule. This is a standard Prolog technique and is essential for correctness under recursion.
- **MAX_DEPTH guard.** Recursion is bounded at depth 100 by default, to prevent silent infinite loops from poorly written rules.
- **Occurs check is disabled by default.** Like most Prolog implementations, for speed. It can be enabled with `--occurs-check`.
- **Negation as failure.** The `не` operator is implemented as classical negation-as-failure: `не G` succeeds iff `G` has no solutions under the current substitution.

---

## 3. Architecture

### 3.1. Top-level module layout

```
minilog/
├── minilog/
│   ├── __init__.py           — public API exports
│   ├── terms.py              — Term, Atom, Var, Compound, Num, Str
│   ├── lexer.py              — Lexer, Token, TokenType
│   ├── parser.py             — Parser, AST nodes (Fact, Rule, Query, Program)
│   ├── unify.py              — unify(), Substitution, walk()
│   ├── kb.py                 — KnowledgeBase (fact/rule storage)
│   ├── engine.py             — backward chaining (solve)
│   ├── forward.py            — forward chaining (saturate)
│   ├── tracer.py             — Tracer, ProofNode, tree formatter
│   ├── evaluator.py          — arithmetic, comparison operators
│   ├── evolution.py          — evolution engine (production rules)
│   ├── repl.py               — interactive shell
│   ├── cli.py                — CLI entry point (minilog run/repl/check)
│   └── errors.py             — error types and formatters
├── examples/
│   ├── family.ml
│   ├── directions.ml
│   ├── dwh_dependencies.ml
│   ├── biology.ml
│   ├── recipes.ml
│   ├── mythology.ml
│   ├── causality.ml
│   ├── terra_tacita.ml
│   └── biology_evolution.ml
├── tests/
│   ├── unit/
│   │   ├── test_terms.py
│   │   ├── test_lexer.py
│   │   ├── test_parser.py
│   │   ├── test_unify.py
│   │   ├── test_kb.py
│   │   ├── test_engine.py
│   │   ├── test_forward.py
│   │   ├── test_tracer.py
│   │   ├── test_evaluator.py
│   │   └── test_evolution.py
│   └── integration/
│       ├── test_family.py
│       ├── test_directions.py
│       ├── test_dwh_dependencies.py
│       ├── test_biology.py
│       ├── test_recipes.py
│       ├── test_mythology.py
│       ├── test_causality.py
│       ├── test_terra_tacita.py
│       └── test_biology_evolution.py
├── docs/
│   └── language-reference.md   — user-facing language docs (in Ukrainian)
├── pyproject.toml
└── README.md
```

### 3.2. Data-flow diagram

```
[.ml file on disk]
      │
      ▼  read UTF-8
[raw text : str]
      │
      ▼  Lexer.tokenize()
[tokens : list[Token]]
      │
      ▼  Parser.parse()
[AST : Program(facts, rules, queries)]
      │
      ├────── facts, rules ─────────▶  [KnowledgeBase]
      │                                       │
      └────── queries ──┐                     │
                        │                     │
                        ▼                     │
                  Engine.solve() ◀────────────┘
                        │
                        ▼
             [Iterator[Substitution]]
                        │
                        ▼  CLI formatter
                 [printed output]
```

Trace queries (`?- слід ...`) additionally pass through `Tracer`, which wraps `solve` and builds a `ProofNode` tree alongside each yielded substitution. Evolution commands (`:evolve N` in the REPL) invoke `evolution.run_generations(kb, n)`, which repeatedly applies production rules until `N` generations have elapsed or a fixpoint is reached.

### 3.3. Module responsibilities

| Module | Responsibility | Public API |
|---|---|---|
| `terms` | Core value types for the language | `Term`, `Atom`, `Var`, `Compound`, `Num`, `Str`, `is_ground()` |
| `lexer` | Text → token stream | `Lexer`, `tokenize(text) -> list[Token]`, `Token`, `TokenType` |
| `parser` | Tokens → AST | `Parser`, `parse(tokens) -> Program`, `Program`, `Fact`, `Rule`, `Query` |
| `unify` | Robinson's algorithm | `unify(t1, t2, subst) -> Substitution \| None`, `Substitution`, `walk()` |
| `kb` | Fact and rule storage | `KnowledgeBase`, `.add_fact()`, `.add_rule()`, `.lookup()`, `.remove_fact()` |
| `engine` | SLD resolution (backward chaining) | `solve(goal, kb, ...) -> Iterator[Substitution]` |
| `forward` | Saturation (forward chaining) | `saturate(kb) -> int` |
| `tracer` | Proof-tree construction and formatting | `Tracer`, `ProofNode`, `format_tree()`, `to_dict()` |
| `evaluator` | Arithmetic and comparisons | `evaluate(term, subst) -> Num`, `check_comparison(...)` |
| `evolution` | Production-rule engine | `ProductionRule`, `run_generations(kb, rules, n)` |
| `repl` | Interactive shell | `REPL`, `.run()` |
| `cli` | Command-line entry point | `main()` |
| `errors` | Error hierarchy | `MinilogError`, `LexError`, `ParseError`, `SolveError`, `EvaluatorError` |

### 3.4. Dependency hierarchy

```
terms.py                 ← no dependencies (foundation)
  ↑
unify.py                 ← depends only on terms
  ↑
kb.py                    ← depends on terms, parser (AST node types)
  ↑
engine.py                ← depends on unify, kb, evaluator
forward.py               ← depends on unify, kb
evaluator.py             ← depends on terms, unify
  ↑
tracer.py                ← wraps engine
evolution.py             ← depends on forward, kb
  ↑
parser.py                ← depends on lexer, terms
lexer.py                 ← depends on errors
  ↑
repl.py                  ← depends on engine, tracer, kb, parser, lexer
cli.py                   ← depends on repl, engine, parser, lexer
```

No cycles. `terms.py` is the foundation. `unify.py` and `kb.py` form the next layer. `engine.py`, `forward.py`, and `evaluator.py` sit on top. `tracer.py`, `evolution.py`, `repl.py`, and `cli.py` are the outermost layer.

---

## 4. Language Grammar

Formal grammar in EBNF. A few productions are described informally where that is clearer.

```
program        = { statement } ;
statement      = fact | rule | query ;

fact           = compound "." ;

rule           = "правило" compound "якщо" body "."
               | "правило" compound ":" NEWLINE INDENT "якщо" body "." DEDENT ;

body           = goal { "і" goal } ;
goal           = compound | negation | comparison ;
negation       = "не" compound ;
comparison     = term comparison_op term ;
comparison_op  = "≥" | "≤" | ">" | "<" | "=" | "≠" ;

query          = "?-" [ "слід" ] compound "." ;

compound       = IDENT "(" [ term { "," term } ] ")"
               | IDENT ;                   (* atom = 0-arity compound *)

term           = atom | variable | number | string | compound ;
atom           = IDENT ;
variable       = "?" IDENT | "?_" ;
number         = INT | FLOAT ;
string         = '"' { character } '"' ;

IDENT          = (UnicodeLetter | "_") { UnicodeLetter | Digit | "_" | "'" } ;
UnicodeLetter  = any character in Unicode category L* (Ukrainian, Latin, etc.) ;

comment        = "%" { character } NEWLINE ;   (* discarded by the lexer *)
```

### Examples matching the grammar

**Plain fact:**
```
батько(авраам, ісак).
```

**Nullary atom-as-fact:**
```
сонячно.
```

**Inline rule:**
```
правило дорослий(?х) якщо вік(?х, ?n) і ?n ≥ 18.
```

**Block rule:**
```
правило предок(?х, ?y):
    якщо батько(?х, ?z)
    і предок(?z, ?y).
```

**Query:**
```
?- предок(авраам, ?хто).
```

**Traced query:**
```
?- слід предок(авраам, йосип).
```

### Deliberate language omissions

- No disjunction (`;`) — expressed via multiple rules with the same head
- No cut (`!`)
- No infix operators other than comparison
- No lists as first-class terms (not needed by Stage 1 examples)
- No built-in predicates beyond comparison and arithmetic

---

## 5. Data Models

### 5.1. Term hierarchy

```python
# terms.py

from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Atom:
    """An atomic symbol: авраам, ісак, red."""
    name: str
    def __repr__(self) -> str:
        return self.name

@dataclass(frozen=True)
class Var:
    """A variable: ?х, ?хто, ?_. Anonymous variable has name='_'."""
    name: str
    def __repr__(self) -> str:
        return f"?{self.name}"

@dataclass(frozen=True)
class Num:
    """A numeric literal: 42, 3.14."""
    value: int | float
    def __repr__(self) -> str:
        return str(self.value)

@dataclass(frozen=True)
class Str:
    """A string literal."""
    value: str
    def __repr__(self) -> str:
        return f'"{self.value}"'

@dataclass(frozen=True)
class Compound:
    """A compound term: батько(авраам, ісак)."""
    functor: str
    args: tuple["Term", ...]    # tuple for hashability

    def __repr__(self) -> str:
        return f"{self.functor}({', '.join(repr(a) for a in self.args)})"

    @property
    def arity(self) -> int:
        return len(self.args)

Term = Union[Atom, Var, Num, Str, Compound]

def is_ground(term: Term) -> bool:
    """True if the term contains no variables."""
    if isinstance(term, Var):
        return False
    if isinstance(term, Compound):
        return all(is_ground(a) for a in term.args)
    return True
```

All term types are **frozen and hashable**. This lets them serve as dictionary keys (for `Substitution`) and set members (for deduplication in forward chaining).

### 5.2. AST nodes

```python
# parser.py

@dataclass
class Fact:
    head: Compound

@dataclass
class Rule:
    head: Compound
    body: list["Goal"]

@dataclass
class Query:
    goal: Compound
    trace: bool = False

@dataclass(frozen=True)
class Comparison:
    """A numeric comparison goal: ?x ≥ 5."""
    left: Term
    op: str                   # '≥', '≤', '>', '<', '=', '≠'
    right: Term

@dataclass(frozen=True)
class Negation:
    """A negation-as-failure goal: не compound(...)."""
    inner: Compound

Goal = Union[Compound, Comparison, Negation]

@dataclass
class Program:
    facts: list[Fact]
    rules: list[Rule]
    queries: list[Query]
```

### 5.3. Substitution

```python
# unify.py

@dataclass(frozen=True)
class Substitution:
    """Immutable mapping from variables to terms."""
    bindings: tuple[tuple[Var, Term], ...]   # frozen, hashable

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
        # See Algorithms section for the full implementation.
        ...
```

Using a sorted tuple instead of a dict keeps `Substitution` hashable and trivially equality-comparable. Lookup is `O(n)` but `n` is typically under 20 for our examples, so the overhead is negligible.

### 5.4. KnowledgeBase

```python
# kb.py

from collections import defaultdict
from typing import Iterator

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
        """For the evolution engine. Returns True if the fact existed and was removed."""
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
```

### 5.5. ProofNode

```python
# tracer.py

from dataclasses import dataclass, field

@dataclass
class ProofNode:
    """A node in a proof tree."""
    goal: "Compound"
    kind: str                           # 'fact' | 'rule' | 'builtin' | 'negation'
    rule: "Rule | None" = None
    binding: "Substitution | None" = None
    children: list["ProofNode"] = field(default_factory=list)
    status: str = "proved"              # 'proved' | 'failed'

    def format_tree(self, indent: int = 0) -> str:
        """Render the tree using Unicode box-drawing characters."""
        ...

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
```

---

## 6. Algorithms

### 6.1. Unification (Robinson)

```python
def unify(t1: Term, t2: Term, subst: Substitution) -> Substitution | None:
    """Attempt to unify t1 and t2. Return an extended substitution, or None on failure."""
    t1 = walk(t1, subst)
    t2 = walk(t2, subst)

    if t1 == t2:
        return subst

    if isinstance(t1, Var):
        # Occurs check is optional and disabled by default
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

    # Atom, Num, Str — must match exactly, already handled by the equality check above
    return None


def walk(term: Term, subst: Substitution) -> Term:
    """Dereference a variable chain until we hit a non-var or an unbound var."""
    while isinstance(term, Var):
        value = subst.lookup(term)
        if value is None:
            return term
        term = value
    return term
```

`walk` is the standard Prolog trick to dereference variable chains lazily without eagerly applying the full substitution.

### 6.2. Backward chaining (SLD resolution)

```python
def solve(
    goal: Goal,
    kb: KnowledgeBase,
    subst: Substitution = Substitution.empty(),
    depth: int = 0,
    max_depth: int = 100,
) -> Iterator[Substitution]:
    """Solve a goal against the KB, yielding each successful substitution."""
    if depth > max_depth:
        raise SolveError(f"Maximum recursion depth {max_depth} exceeded")

    # Handle special goal types first
    if isinstance(goal, Comparison):
        yield from solve_comparison(goal, subst)
        return

    if isinstance(goal, Negation):
        # Negation as failure
        try:
            next(solve(goal.inner, kb, subst, depth + 1, max_depth))
            return   # inner goal succeeded → negation fails
        except StopIteration:
            yield subst   # inner goal failed → negation succeeds

    # Standard compound goal
    assert isinstance(goal, Compound)
    facts, rules = kb.lookup(goal.functor, goal.arity)

    # Try facts first
    for fact in facts:
        new_subst = unify(goal, fact.head, subst)
        if new_subst is not None:
            yield new_subst

    # Then try rules
    for rule in rules:
        fresh_rule = rename_variables(rule, suffix=f"_{depth}_{id(rule)}")
        new_subst = unify(goal, fresh_rule.head, subst)
        if new_subst is None:
            continue
        yield from solve_body(fresh_rule.body, kb, new_subst, depth + 1, max_depth)


def solve_body(
    body: list[Goal],
    kb: KnowledgeBase,
    subst: Substitution,
    depth: int,
    max_depth: int,
) -> Iterator[Substitution]:
    """Solve a conjunction of goals (the body of a rule)."""
    if not body:
        yield subst
        return
    first, *rest = body
    for new_subst in solve(first, kb, subst, depth, max_depth):
        yield from solve_body(rest, kb, new_subst, depth, max_depth)


def rename_variables(rule: Rule, suffix: str) -> Rule:
    """Produce a copy of the rule with all variables renamed with a unique suffix."""
    ...
```

### 6.3. Forward chaining (saturation)

```python
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
            break   # fixpoint reached
        for fact in new_facts:
            kb.add_fact(fact)
        total_added += len(new_facts)
    return total_added
```

### 6.4. Tracer (proof-tree construction)

```python
class Tracer:
    def trace_solve(
        self,
        goal: Goal,
        kb: KnowledgeBase,
        subst: Substitution = Substitution.empty(),
    ) -> Iterator[tuple[Substitution, ProofNode]]:
        """Like solve(), but also builds a ProofNode for each successful derivation."""
        # Structurally parallel to solve(). For each successful branch, a ProofNode is
        # constructed with the matching rule and child subproofs; on yield, both the
        # substitution and the proof node are returned together.
        ...
```

### 6.5. Evolution engine

```python
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
```

---

## 7. CLI and REPL

### 7.1. Top-level CLI commands

```
minilog run <file.ml>          — Load a file and execute every query in it
minilog repl [file.ml]         — Start the interactive shell (optionally pre-loading a file)
minilog check <file.ml>        — Parse-only check; reports syntax errors without executing
minilog version                — Print the version string
```

### 7.2. REPL commands

Inside the REPL, commands prefixed with `:` are recognized:

```
:help                — list commands
:quit | :q           — exit
:load <file>         — load a .ml file into the current KB
:stats               — show KB statistics
:list <functor>/N    — list all facts and rules for a predicate
:evolve <N>          — run N generations of production rules (for evolution examples)
:saturate            — run forward chaining to fixpoint
:trace on|off        — automatically trace all subsequent queries
:clear               — wipe the KB
```

Any line not starting with `:` is interpreted as a query or a new fact/rule.

### 7.3. Output formats

**Successful query with bindings:**
```
?- предок(авраам, ?хто).
?хто = ісак.
?хто = яків.
(2 solutions)
```

**Query with no solutions:**
```
?- літає(пінгвін).
false.
```

**Traced query:**
```
?- слід успадковує(дуб, хлорофіл).
  успадковує(дуб, хлорофіл)
  └─ rule: успадковує(?х, ?p) :- є(?х, ?y), успадковує(?y, ?p)
     ├─ є(дуб, дерево)               [fact]
     └─ успадковує(дерево, хлорофіл)
        └─ rule: успадковує(?х, ?p) :- є(?х, ?y), успадковує(?y, ?p)
           ├─ є(дерево, рослина)     [fact]
           └─ успадковує(рослина, хлорофіл)
              └─ rule: успадковує(?х, ?p) :- має(?х, ?p)
                 └─ має(рослина, хлорофіл)  [fact]
  PROVED in 5 steps.
```

**Errors (always English, always include line/column when applicable):**
```
LexError at line 5, col 12: unexpected character '@'
ParseError at line 8: expected 'якщо' after rule head, got IDENT('і')
SolveError: predicate літає/1 not found in knowledge base
SolveError: maximum recursion depth 100 exceeded while solving предок(?x, ?y)
EvaluatorError at line 23: cannot compare non-numeric terms: ісак ≥ 5
```

---

## 8. Example Files

Each `.ml` file in `examples/` is accompanied by `examples/<name>.expected.txt` containing the exact output that `minilog run` should produce for that file. This gives the integration test suite concrete regression targets.

### 8.1. `family.ml`
- ~10 facts (biblical patriarchs), 4 rules (`тато`, `мама`, `предок` base + recursive)
- Queries: `?- тато(?x, ісак)`, `?- предок(авраам, йосип)`, `?- предок(авраам, ?x)`
- Demonstrates: unification with variables, first recursion

### 8.2. `directions.ml`
- ~15 facts (Ukrainian city geography), 3 rules (`поруч`, `північніше_транзитивно`)
- Queries about symmetric and transitive relations
- Demonstrates: symmetry expressed via two rules

### 8.3. `dwh_dependencies.ml`
- ~25 facts (tables, procedures, `читає`/`модифікує`/`викликає` relations), ~10 rules
- Queries: `?- впливає_на(stg_customers, ?x)`, `?- має_цикл(?x)`, `?- конфлікт_запису(?t, ?p1, ?p2)`
- Demonstrates: multi-typed relations, transitive closure, cycle and write-conflict detection
- Bridge to Stage 4 (migvisor-axioms)

### 8.4. `biology.ml`
- ~30 facts (taxonomy plus phylogeny), ~8 rules
- Queries: `?- літає(?x)`, `?- успадковує(дуб, ?p)`, `?- слід успадковує(дуб, хлорофіл)`
- Demonstrates: two structurally identical recursions over different relations, negation, deep proof tree

### 8.5. `recipes.ml`
- ~20 facts (dishes, ingredients, categories), ~5 rules
- Queries: `?- підходить_вегетаріанцю(?x)`
- Demonstrates: multi-layer negation via intermediate predicates

### 8.6. `mythology.ml`
- ~15 facts (Slavic gods, domains, worship), ~4 rules
- Queries: `?- конфлікт_вірувань(?x, ?y)`
- Demonstrates: modeling cultural/religious structures

### 8.7. `causality.ml`
- ~15 facts (weather and transport causes), ~3 rules
- Queries: `?- призводить_до(дощ, ?x)`, `?- спільна_причина(мокра_дорога, ?x, ?c)`
- Demonstrates: transitive causation, common-cause inference

### 8.8. `terra_tacita.ml`
- ~20 facts with placeholder names (species, languages, characters, artifacts)
- **Prominent disclaimer on line 1** that this is a teaching example and NOT the real trilogy canon
- Rules: `знає_мову`, `може_говорити_прямо`, `може_говорити_через_артефакт`, `може_спілкуватися`, `може_спілкуватися_через`
- Demonstrates: multi-step mediated relations (direct contact, contact via translator artifact, contact via hybrid intermediary)
- Bridge to Stage 5 (terra-tacita-canon)

### 8.9. `biology_evolution.ml`
- Same base as `biology.ml` plus ~5 production rules (mutation, speciation, extinction)
- Used with the `:evolve N` REPL command
- Demonstrates: the original taxonomy rules continue to work on newly evolved species without modification — the core insight that formal-system rules are independent of the specific entities in the knowledge base

---

## 9. Testing Strategy

### 9.1. Unit tests (~50 total)

| Module | Test count | Covers |
|---|---|---|
| `test_terms.py` | 5 | equality, hashing, repr, `is_ground`, `arity` |
| `test_lexer.py` | 8 | keywords, comments, variables, numbers, strings, error positions, indented rules |
| `test_parser.py` | 7 | facts, both rule forms, queries, comparisons, negation, syntax errors |
| `test_unify.py` | 8 | atom–atom, var–term, compound–compound, occurs, failure modes, `walk` |
| `test_kb.py` | 4 | add/lookup/remove, indexing, stats |
| `test_engine.py` | 10 | facts, rules, recursion, MAX_DEPTH, backtracking, negation, missing predicates |
| `test_forward.py` | 4 | saturation, fixpoint, deduplication, empty KB |
| `test_tracer.py` | 4 | proof-tree construction, `to_dict`, `format_tree`, negation trace |
| `test_evaluator.py` | 3 | arithmetic, comparisons, type errors |
| `test_evolution.py` | 4 | production rules, add/remove, generation history, termination |

### 9.2. Integration tests (9 total)

Each integration test:
1. Loads `examples/<n>.ml`
2. Executes every query in the file
3. Captures stdout and compares it against `examples/<n>.expected.txt`

This gives free regression coverage: breaking backward chaining will break `test_family.py`, breaking forward chaining will break `test_biology_evolution.py`, and so on.

### 9.3. Running tests

```bash
pytest tests/unit/                               # unit only
pytest tests/integration/                         # integration only
pytest                                            # both
pytest --cov=minilog --cov-report=term-missing    # with coverage
```

Coverage target: **100% for core modules** (`terms`, `unify`, `kb`, `engine`). **≥80% for tracer, evolution, repl, cli**.

---

## 10. Task List for Claude Code

Each task has an ID, title, description, list of files to create or modify, dependencies on other tasks, acceptance criteria, and an estimated size (S = ≤ 0.5 day, M = 0.5–1 day, L = 1–2 days).

Tasks are designed so that each one can be handed to a fresh Claude Code session in order, with earlier tasks providing the context the current task needs.

---

### MINILOG-001 — Project skeleton and packaging

- **Size:** S
- **Depends on:** —
- **Files to create:**
  - `pyproject.toml`
  - `minilog/__init__.py` (empty, will hold public exports later)
  - `README.md` (minimal, just project name and one-liner)
  - `tests/__init__.py`
  - `tests/unit/__init__.py`
  - `tests/integration/__init__.py`
  - `examples/` (empty directory with `.gitkeep`)
  - `docs/` (empty directory with `.gitkeep`)

- **Description:** Set up the Python project layout and packaging. Configure `pyproject.toml` for Python 3.11+ with an entry point `minilog = minilog.cli:main`. Add `pytest` and `pytest-cov` as dev dependencies. Ensure `pip install -e .` succeeds and that `minilog version` can be invoked (even if it just prints a placeholder — the real CLI comes later).

- **Acceptance criteria:**
  - `pip install -e .` exits 0
  - `python -c "import minilog"` succeeds
  - `minilog version` prints something like `minilog 0.1.0`
  - Directory layout matches section 3.1

---

### MINILOG-002 — Term model

- **Size:** S
- **Depends on:** MINILOG-001
- **Files:**
  - `minilog/terms.py`
  - `tests/unit/test_terms.py`

- **Description:** Implement `Atom`, `Var`, `Num`, `Str`, `Compound` as frozen dataclasses. All must be hashable. Implement `__repr__` for each so that round-tripping a term through `repr` produces the expected surface form (`батько(авраам, ісак)`). Add an `arity` property on `Compound`. Implement a module-level function `is_ground(term) -> bool` that recursively checks whether a term contains any variables.

- **Acceptance criteria:**
  - All term types instantiate and compare by value equality
  - `hash(term)` works for every term type
  - `repr(Compound("батько", (Atom("авраам"), Atom("ісак"))))` equals `"батько(авраам, ісак)"`
  - `is_ground(Atom("x"))` is `True`; `is_ground(Var("y"))` is `False`; `is_ground(Compound("f", (Atom("a"), Var("b"))))` is `False`
  - ≥5 unit tests, all passing

---

### MINILOG-003 — Error hierarchy

- **Size:** S
- **Depends on:** MINILOG-001
- **Files:**
  - `minilog/errors.py`

- **Description:** Create an error class hierarchy rooted at `MinilogError`, with subclasses `LexError`, `ParseError`, `UnifyError`, `SolveError`, `EvaluatorError`. Each error carries optional `line` and `col` fields for source context. `__str__` produces an English message of the form `"{ErrorType} at line {L}, col {C}: {message}"`, gracefully omitting position info when not available.

- **Acceptance criteria:**
  - Each error type can be instantiated with `(message)`, `(line, col, message)`, or `(message=..., line=..., col=...)`
  - `str(LexError(5, 12, "unexpected character '@'"))` equals `"LexError at line 5, col 12: unexpected character '@'"`
  - `str(SolveError("predicate foo/2 not found"))` equals `"SolveError: predicate foo/2 not found"`

---

### MINILOG-004 — Lexer

- **Size:** M
- **Depends on:** MINILOG-002, MINILOG-003
- **Files:**
  - `minilog/lexer.py`
  - `tests/unit/test_lexer.py`

- **Description:** Implement the lexer producing a `list[Token]` from a source string. Support:
  - Ukrainian keywords: `факт`, `правило`, `якщо`, `і`, `не`, `слід`
  - Variables: `?ident`, `?_`
  - Identifiers: Unicode-aware (any `L*` category)
  - Numbers: int and float
  - String literals with `\n`, `\"`, `\\` escapes
  - Operators: `(`, `)`, `,`, `.`, `:`, `?-`, `≥`, `≤`, `>`, `<`, `=`, `≠`
  - Line comments `% ...`
  - Indentation tracking: emit `INDENT` / `DEDENT` for block-form rules; emit `NEWLINE` between statements

  Token fields: `type: TokenType`, `value: str`, `line: int`, `col: int`. Raise `LexError` on unrecognized input.

- **Acceptance criteria:**
  - 8+ unit tests covering: simple facts, both rule forms, comments inside and between lines, Ukrainian-named variables, numbers, strings, malformed input
  - `tokenize("батько(авраам, ісак).")` produces the exact token sequence `[IDENT, LPAREN, IDENT, COMMA, IDENT, RPAREN, DOT, EOF]` with correct line/col
  - Block-form input correctly produces `INDENT`/`DEDENT` pairs

---

### MINILOG-005 — Parser

- **Size:** L
- **Depends on:** MINILOG-004
- **Files:**
  - `minilog/parser.py`
  - `tests/unit/test_parser.py`

- **Description:** Implement a recursive-descent parser consuming the token stream from the lexer and producing a `Program` AST. Handle:
  - Facts
  - Both inline and block rule forms
  - Queries with and without the `слід` prefix
  - Negation goals (`не compound(...)`)
  - Comparison goals (`term op term`)
  - Nested compound terms
  - Proper error reporting with line/col information

  Parser must reject syntactically invalid input with a `ParseError`. It must NOT perform semantic validation (missing predicates, arity mismatches, etc.); those surface during execution.

- **Acceptance criteria:**
  - 7+ unit tests covering: single fact, inline rule, block rule, query, traced query, negation goal, comparison goal, syntax errors
  - Parsing the grammar examples from section 4 produces the expected AST
  - Error messages include line and column information

---

### MINILOG-006 — Substitution and unification

- **Size:** M
- **Depends on:** MINILOG-002
- **Files:**
  - `minilog/unify.py`
  - `tests/unit/test_unify.py`

- **Description:** Implement `Substitution` as a frozen, hashable data type with `empty()`, `extend(var, term)`, `lookup(var)`, and `apply(term)` operations. Implement `walk(term, subst)` for variable dereferencing and `unify(t1, t2, subst) -> Substitution | None` following Robinson's algorithm without the occurs check by default.

- **Acceptance criteria:**
  - 8+ unit tests covering: atom-atom success, atom-atom failure, var-binding, compound-compound success, compound-compound arity mismatch, nested unification, `walk` chain, `apply` round-trip
  - `unify(Var("x"), Atom("a"), empty())` produces a substitution where `apply(Var("x"))` returns `Atom("a")`
  - `unify(Compound("f", (Var("x"), Atom("b"))), Compound("f", (Atom("a"), Var("y"))), empty())` succeeds
  - `unify(Compound("f", (Atom("a"),)), Compound("g", (Atom("a"),)), empty())` returns `None`

---

### MINILOG-007 — Knowledge Base

- **Size:** S
- **Depends on:** MINILOG-005
- **Files:**
  - `minilog/kb.py`
  - `tests/unit/test_kb.py`

- **Description:** Implement `KnowledgeBase` with `add_fact`, `add_rule`, `lookup(functor, arity)`, `remove_fact`, `all_facts`, and `stats`. Facts and rules are stored in separate dicts keyed by `(functor, arity)`.

- **Acceptance criteria:**
  - 4+ unit tests covering: add/lookup, multiple predicates, remove, stats
  - `lookup` returns `([], [])` for unknown predicates (does not raise)
  - Stats reports correct fact, rule, and predicate counts

---

### MINILOG-008 — Evaluator

- **Size:** S
- **Depends on:** MINILOG-006
- **Files:**
  - `minilog/evaluator.py`
  - `tests/unit/test_evaluator.py`

- **Description:** Implement `evaluate(term, subst) -> Num` that resolves a term to a numeric value under a substitution, raising `EvaluatorError` on non-numeric terms. Implement `check_comparison(left, op, right, subst) -> bool` for `≥`, `≤`, `>`, `<`, `=`, `≠`. Unification equality (`=`) is deferred to the unify module — here, `=` is only used as a numeric equality check.

- **Acceptance criteria:**
  - 3+ unit tests covering arithmetic, comparisons, and non-numeric failure
  - `check_comparison(Num(5), ">", Num(3), empty())` returns `True`
  - Comparing a non-numeric term raises `EvaluatorError`

---

### MINILOG-009 — Backward-chaining engine

- **Size:** L
- **Depends on:** MINILOG-006, MINILOG-007, MINILOG-008
- **Files:**
  - `minilog/engine.py`
  - `tests/unit/test_engine.py`

- **Description:** Implement `solve(goal, kb, subst, depth, max_depth)` as a generator of substitutions, and the helper `solve_body(body, kb, subst, depth, max_depth)`. Implement `rename_variables(rule, suffix)` to produce fresh-variable copies of rules on each application. Handle:
  - Fact matching
  - Rule application with fresh variables
  - Body conjunction
  - Comparison goals (delegated to evaluator)
  - Negation-as-failure
  - MAX_DEPTH guard raising `SolveError`
  - Missing predicates raising `SolveError`

- **Acceptance criteria:**
  - 10+ unit tests covering: single fact solve, single rule solve, recursive rule, multi-solution backtracking, negation success, negation failure, comparison goal, max-depth trip, missing predicate, body with multiple goals
  - `solve` returns an iterator (not a list); solutions stream lazily

---

### MINILOG-010 — Forward chaining

- **Size:** M
- **Depends on:** MINILOG-009
- **Files:**
  - `minilog/forward.py`
  - `tests/unit/test_forward.py`

- **Description:** Implement `saturate(kb, max_iterations) -> int` that repeatedly applies all rules in the KB, adding newly derivable ground facts until no new facts are produced (fixpoint) or `max_iterations` is reached. Uses `solve_body` from the engine internally. Must dedupe: a fact already in the KB is not added again.

- **Acceptance criteria:**
  - 4+ unit tests covering: simple saturation, fixpoint detection, empty KB, no-op KB with no rules
  - Running `saturate` twice in a row returns `>0` the first time and `0` the second time (idempotence at fixpoint)

---

### MINILOG-011 — Tracer and proof trees

- **Size:** M
- **Depends on:** MINILOG-009
- **Files:**
  - `minilog/tracer.py`
  - `tests/unit/test_tracer.py`

- **Description:** Implement `ProofNode` dataclass and `Tracer.trace_solve(goal, kb, subst)` that mirrors `solve` structurally but also constructs a `ProofNode` tree for each successful derivation. Implement `ProofNode.format_tree()` using Unicode box-drawing characters (`├─`, `└─`, `│`) to render the proof tree as a printable string. Implement `ProofNode.to_dict()` for JSON export (this will be consumed by Stage 3 and Stage 5).

- **Acceptance criteria:**
  - 4+ unit tests covering: proof node for a fact, proof node for a rule application, nested proof tree, `to_dict` round-trip
  - `format_tree()` on a proof for a 3-level recursive derivation produces output with the expected indentation and box-drawing characters

---

### MINILOG-012 — Evolution engine

- **Size:** M
- **Depends on:** MINILOG-010
- **Files:**
  - `minilog/evolution.py`
  - `tests/unit/test_evolution.py`

- **Description:** Implement `ProductionRule` dataclass and `run_generations(kb, rules, n)` that runs `n` generations. In each generation: for every production rule, find all substitutions that satisfy the condition, then apply each rule's `add` and `remove` lists under that substitution. Return a history list of dicts per generation, recording which facts were added and removed.

- **Acceptance criteria:**
  - 4+ unit tests covering: add-only rule, remove-only rule, mixed rule, termination after N generations
  - Running a mutation rule 3 times on a seed KB produces the expected cumulative state

---

### MINILOG-013 — CLI and REPL

- **Size:** L
- **Depends on:** MINILOG-009, MINILOG-011 (trace output)
- **Files:**
  - `minilog/cli.py`
  - `minilog/repl.py`

- **Description:** Implement the top-level CLI (`run`, `repl`, `check`, `version`) using `argparse`. Implement the interactive REPL with the colon-prefixed commands listed in section 7.2. The REPL must:
  - Maintain a persistent `KnowledgeBase` across commands
  - Parse each non-`:` line as either a fact, rule, or query
  - Pretty-print query results and proof trees
  - Handle errors gracefully (catch `MinilogError` subclasses, print them, continue)
  - Support command history via `readline` when available

  The CLI `run` command loads a file, executes every query, and prints output in the format shown in section 7.3. `check` performs only parsing and reports success or syntax errors. `repl [file]` optionally pre-loads a file, then enters the interactive loop.

- **Acceptance criteria:**
  - `minilog run examples/family.ml` produces the expected output (integration tests in MINILOG-014 cover the full check)
  - `minilog check examples/family.ml` exits 0 on valid input, non-zero on syntax errors
  - `minilog repl` starts, accepts queries, handles `:stats`, `:list`, `:clear`, `:quit`
  - Error messages are English and include line/column when applicable

---

### MINILOG-014 — Examples: family, directions, dwh_dependencies

- **Size:** M
- **Depends on:** MINILOG-013
- **Files:**
  - `examples/family.ml`
  - `examples/family.expected.txt`
  - `examples/directions.ml`
  - `examples/directions.expected.txt`
  - `examples/dwh_dependencies.ml`
  - `examples/dwh_dependencies.expected.txt`
  - `tests/integration/test_family.py`
  - `tests/integration/test_directions.py`
  - `tests/integration/test_dwh_dependencies.py`

- **Description:** Author the first three example files per section 8. Each file contains the facts, rules, and queries described in the overview. Produce the matching `.expected.txt` files by running `minilog run` and capturing the output (after reviewing it for correctness). Write an integration test per example that asserts `minilog run <file>` reproduces the expected output byte for byte.

- **Acceptance criteria:**
  - All three examples parse without errors
  - `minilog run examples/family.ml` output matches `examples/family.expected.txt`
  - Same for `directions.ml` and `dwh_dependencies.ml`
  - Integration tests pass
  - `dwh_dependencies.ml` actually detects the seeded cycle and write conflict

---

### MINILOG-015 — Examples: biology, recipes, mythology, causality, terra_tacita

- **Size:** M
- **Depends on:** MINILOG-014
- **Files:**
  - `examples/biology.ml` + `.expected.txt`
  - `examples/recipes.ml` + `.expected.txt`
  - `examples/mythology.ml` + `.expected.txt`
  - `examples/causality.ml` + `.expected.txt`
  - `examples/terra_tacita.ml` + `.expected.txt`
  - `tests/integration/test_biology.py`
  - `tests/integration/test_recipes.py`
  - `tests/integration/test_mythology.py`
  - `tests/integration/test_causality.py`
  - `tests/integration/test_terra_tacita.py`

- **Description:** Author the five mid-complexity examples per section 8. `terra_tacita.ml` must begin with a prominent multi-line `%` comment explaining that it is a teaching example with placeholder names and is NOT the real canon for Vitalii's trilogy (the real canon lives in the separate Stage 5 project).

- **Acceptance criteria:**
  - All five examples parse and execute without errors
  - `biology.ml` supports both `?- літає(?x)` and `?- слід успадковує(дуб, хлорофіл)` with the proof tree rendered correctly
  - `terra_tacita.ml` starts with the required disclaimer comment
  - All integration tests pass

---

### MINILOG-016 — Evolution example: biology_evolution

- **Size:** M
- **Depends on:** MINILOG-012, MINILOG-015
- **Files:**
  - `examples/biology_evolution.ml`
  - `examples/biology_evolution.expected.txt`
  - `tests/integration/test_biology_evolution.py`

- **Description:** Author `biology_evolution.ml`, which builds on `biology.ml` and adds production rules for mutation, speciation, and extinction. The example exercises the `:evolve N` REPL command. The integration test must verify that after running 10 generations, the original taxonomy rules from `biology.ml` still successfully apply to newly evolved species.

- **Acceptance criteria:**
  - `minilog repl examples/biology_evolution.ml` followed by `:evolve 10` runs without errors
  - After evolution, at least one new species exists that was not in the initial KB
  - Querying `?- успадковує(<new_species>, крила)` still produces a valid proof tree using the unchanged base rules
  - Integration test passes

---

### MINILOG-017 — Documentation and polish

- **Size:** M
- **Depends on:** MINILOG-013, MINILOG-014, MINILOG-015, MINILOG-016
- **Files:**
  - `docs/language-reference.md` (written in **Ukrainian** — this is the one Ukrainian-language artifact in the project)
  - `README.md` (expanded, in English)

- **Description:** Write the language reference in Ukrainian, documenting: the full syntax with examples, the nine built-in examples and what each one demonstrates, REPL commands, CLI commands, error-message conventions, and the deliberate omissions (no cut, no disjunction, etc.). Expand `README.md` (English) with installation instructions, a quickstart example, a link to the Ukrainian language reference, and the project roadmap pointing at Stages 2–5.

- **Acceptance criteria:**
  - `docs/language-reference.md` covers every language feature from section 4
  - `README.md` quickstart runs successfully as documented
  - Both documents render cleanly on GitHub

---

## 11. Task Dependency Graph

```
                 MINILOG-001 (skeleton)
                      │
            ┌─────────┼─────────┐
            ▼         ▼         ▼
      MINILOG-002  MINILOG-003   ·
      (terms)      (errors)
            │         │
            └────┬────┘
                 ▼
            MINILOG-004
              (lexer)
                 │
                 ▼
            MINILOG-005
             (parser)
                 │
      ┌──────────┼──────────┐
      ▼          ▼          ▼
 MINILOG-006 MINILOG-007   ·
  (unify)      (kb)
      │          │
      └────┬─────┘
           ▼
      MINILOG-008
      (evaluator)
           │
           ▼
      MINILOG-009
      (engine)
      ┌────┼──────────┐
      ▼    ▼          ▼
MINILOG-010 MINILOG-011  ·
 (forward)  (tracer)
      │         │
      ▼         │
MINILOG-012     │
(evolution)     │
      │         │
      └────┬────┘
           ▼
      MINILOG-013
      (cli + repl)
           │
           ▼
      MINILOG-014
  (examples 1-3 + tests)
           │
           ▼
      MINILOG-015
  (examples 4-8 + tests)
           │
           ▼
      MINILOG-016
 (evolution example + test)
           │
           ▼
      MINILOG-017
  (docs and polish)
```

**Parallelization hints:**

- MINILOG-002 and MINILOG-003 can run in parallel after MINILOG-001
- MINILOG-006 and MINILOG-007 can run in parallel after MINILOG-005
- MINILOG-010, MINILOG-011, and MINILOG-012 can run in parallel after MINILOG-009 (MINILOG-012 needs MINILOG-010)
- Example-authoring tasks (MINILOG-014, MINILOG-015, MINILOG-016) must be sequential because each builds on the preceding one for regression stability

**Suggested execution order for a sequential session-by-session workflow:**

1. MINILOG-001 → MINILOG-002 → MINILOG-003
2. MINILOG-004 → MINILOG-005
3. MINILOG-006 → MINILOG-007 → MINILOG-008
4. MINILOG-009
5. MINILOG-010 → MINILOG-011 → MINILOG-012
6. MINILOG-013
7. MINILOG-014 → MINILOG-015 → MINILOG-016
8. MINILOG-017

Each numbered group is a natural stopping point: the project is in a consistent, testable state after each one, and you can leave it and come back without losing context.

---

## 12. Stage 1 Completion Criteria

Stage 1 is considered complete when **all** of the following hold:

1. `pip install -e .` succeeds in a fresh Python 3.11+ virtualenv
2. `minilog version` prints the expected version string
3. `minilog run examples/family.ml` produces the expected output
4. `minilog run examples/directions.ml` produces the expected output
5. `minilog run examples/dwh_dependencies.ml` correctly detects the seeded cyclic dependency AND the seeded write conflict
6. `minilog run examples/biology.ml` produces the expected output, including a traced query with a proof tree of depth ≥ 5
7. `minilog run examples/recipes.ml` produces the expected output
8. `minilog run examples/mythology.ml` produces the expected output
9. `minilog run examples/causality.ml` produces the expected output
10. `minilog run examples/terra_tacita.ml` produces the expected output and includes the disclaimer comment on line 1
11. `minilog repl examples/biology_evolution.ml` followed by `:evolve 10` runs without errors, and post-evolution the unchanged base taxonomy rules still apply to newly evolved species
12. `minilog repl` starts, accepts interactive queries, and correctly handles every `:`-prefixed command from section 7.2
13. `pytest` passes: all ~50 unit tests and all 9 integration tests green
14. Coverage ≥ 100% on `terms`, `unify`, `kb`, `engine`; ≥ 80% on `tracer`, `evolution`, `repl`, `cli`
15. `docs/language-reference.md` exists, is written in Ukrainian, and documents every feature from section 4
16. `README.md` contains a working quickstart

---

## 13. What Comes Next

Once Stage 1 ships and all completion criteria are met, the roadmap progresses as documented in the separate stage documents:

- **Stage 2 — codex-axioms** (Notion: "Codex Analyzer — Axiomatic Layer Module Spec (Stage 1d)") — formal axiomatic layer for the Codex Seraphinianus analyzer
- **Stage 3 — ca-evolution** (Notion: "Three Stages — Long-Term Research Roadmap") — evolving cellular-automata rules via logical inference
- **Stage 4 — migvisor-axioms** (Notion: "Stage 4 — migvisor-axioms") — formal architectural validation for migVisor DWH scans
- **Stage 5 — terra-tacita-canon** (Notion: "Stage 5 — terra-tacita-canon") — canon keeper for the Terra Tacita trilogy

Stage 1 is the foundation for all four. Stage 4 and Stage 5 consume minilog as a library; Stage 2 and Stage 3 reuse its ideas and vocabulary.

The immediate next step after Stage 1 is Stage 2 (codex-axioms), which already has its own full specification in Notion and is ready to implement.
