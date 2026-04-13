# minilog Phase 10.5 — Evolution Subsystem Completion

## Context

Phase 10 delivered the first example-driven completion package: arithmetic expressions (Phase 9) plus a geometry example that put them to use (MINILOG-025..028). Phase 10.5 applies the same pattern to a different subsystem — **evolution / production rules** — which currently has an 80%-finished implementation in `minilog/evolution.py` and `minilog/repl.py` but cannot be used end-to-end because there is no surface syntax for production rules in `.ml` files.

The evolution subsystem is conceptually different from the regular rule engine: instead of backward chaining (query-driven derivation), it performs forward, mutating evaluation where production rules add and remove facts over discrete generations. This is the mechanism behind Phase 3 (ca-evolution) and will also be used by Phase 5 (terra-tacita-canon) simulations. Having a working evolution subsystem with natural syntax is a prerequisite for any downstream phase that wants to simulate dynamic knowledge bases.

Like Phase 10, Phase 10.5 is a **cohesive package**: parser work, KB integration, engine fix, REPL wiring, one flagship example, one explainer document, and README integration, delivered as a single sprint.

---

## Issues Summary Table

| # | ID | Title | Size | Dependencies |
|---|---|---|---|---|
| 93 | MINILOG-093 | Production rule parser syntax | M | MINILOG-005 |
| 94 | MINILOG-094 | KnowledgeBase integration for production rules | S | MINILOG-093, MINILOG-007 |
| 95 | MINILOG-095 | Fix `run_generations` two-phase semantics and fixpoint detection | M | MINILOG-094 |
| 96 | MINILOG-096 | REPL `:evolve <N>` command full implementation | S | MINILOG-094, MINILOG-095 |
| 97 | MINILOG-097 | Evolution example: population aging simulation | M | MINILOG-096 |
| 98 | MINILOG-098 | Explainer document: production rules and generations | M | MINILOG-097 |
| 99 | MINILOG-099 | README and language reference integration | S | MINILOG-097, MINILOG-098 |

**Size legend:** S = ≤ 0.5 day, M = 0.5–1 day, L = 1–2 days
**Total effort:** ~3-4 days

---

## Locked Architectural Decisions

| Decision | Choice |
|---|---|
| Production rule surface syntax | Keyword-based: `продукція <name> якщо <condition> додати <terms> видалити <terms> коли <guard>.` |
| Keyword `продукція` | New top-level keyword, parallel to `правило` and `факт` |
| `додати` / `видалити` clauses | Both optional individually, but at least one must be non-empty (pure condition with no effect is rejected as error) |
| `коли <guard>` | Optional, accepts a single comparison goal or negation, evaluated after condition match |
| Production rules storage | Separate `_production_rules: list[ProductionRule]` field in `KnowledgeBase`, not mixed with regular `_rules` |
| Generation semantics | Two-phase: collect all matches over snapshot, then apply all changes atomically |
| Fixpoint detection | Enabled by default; early exit from `run_generations` if a generation produces no changes |
| Max generations safeguard | Hard cap at 10000 generations with warning; protects REPL from infinite loops |
| Oscillation detection | **Deferred** — not in Phase 10.5 scope; revisit if practice shows need |
| Interaction with backward chaining | `:evolve N` mutates KB in place; subsequent queries operate on the new state; this is the intended workflow for experimentation |
| Interaction with `:saturate` | `:saturate` (forward chaining over regular rules) and `:evolve` (production rules) are **independent mechanisms** and do not interact automatically; user controls the order |
| REPL output per generation | Summary line per generation (`Generation 1: +3 facts, -1 fact`) with final totals; verbose mode deferred |
| Error handling | Invalid production rules (missing both add/remove, unparseable guard) produce clear parser errors at load time, not runtime |
| Arithmetic binding in effects | `?v_новий = ?v + 10` works through the existing `=` evaluator from Phase 9 arithmetic — no new binding mechanism needed. The aging example relies on this for increment semantics in `додати` clauses |
| `KnowledgeBase.remove_fact` | Already exists from Phase 1 (MINILOG-007), returns `bool`. No changes required |
| `KnowledgeBase.add_fact_if_new` | New method added in MINILOG-094. Returns `bool` (True on insertion, False on duplicate). Required because current `add_fact` does not check for duplicates or return a status |

---

## MINILOG-093 — Production rule parser syntax

**Description:**
Add surface syntax for production rules to `minilog/parser.py` so that production rules can be written in `.ml` source files alongside facts and regular rules. The syntax uses a new top-level keyword `продукція` (parallel to `правило`) and three sub-clauses: `якщо` for the condition, `додати` for facts to add, `видалити` for facts to remove, plus an optional `коли` guard.

**Syntax:**

```
продукція <name> якщо <condition>
    додати <term>[, <term>...]
    видалити <term>[, <term>...]
    [коли <guard>].
```

- `<name>` is an atom identifier used in history output and debugging
- `<condition>` is a compound term or conjunction of goals (same as rule body)
- `додати` and `видалити` are each followed by a comma-separated list of compound terms; variables in these terms refer to bindings from the condition
- At least one of `додати` or `видалити` must be present and non-empty
- `коли <guard>` is optional; if present, accepts a single comparison (e.g., `?x > 60`) or negation (e.g., `не помер(?x)`) that acts as a filter after condition matching

**What needs to be done:**

- Add tokens to `minilog/lexer.py`: new keywords `продукція`, `додати`, `видалити`, `коли`. These are recognized as reserved identifiers when parsing top-level forms
- Add a new AST class `ProductionRuleDef` in `minilog/parser.py`:
  ```python
  @dataclass
  class ProductionRuleDef:
      name: str
      condition: Goal  # single Compound or list of Goals for conjunction
      add: list[Compound]
      remove: list[Compound]
      guard: Goal | None  # optional Comparison or Negation
  ```
- Add grammar production `production_rule` that parses the full syntax and validates:
  - Name is a valid atom identifier
  - Condition is well-formed
  - At least one of `додати`/`видалити` is non-empty (reject `продукція X якщо Y додати [] видалити [].` with clear error)
  - Guard, if present, is a `Comparison` or `Negation` (not an arbitrary compound)
- Extend `Program` dataclass with new field `production_rules: list[ProductionRuleDef]`
- Update `parse()` to dispatch production rules into `Program.production_rules`
- Write ≥10 unit tests in `tests/unit/test_parser_production.py`:
  - Minimal valid production rule (condition + додати)
  - Minimal valid production rule (condition + видалити)
  - Full production rule with name + condition + додати + видалити + коли
  - Production rule with conjunctive condition (`батько(?x, ?y) і вік(?x, ?v)`)
  - Multiple terms in додати (e.g., `додати старий(?x), потребує_догляду(?x)`)
  - Guard with numeric comparison (`коли ?v > 60`)
  - Guard with negation (`коли не помер(?x)`)
  - Error: missing both додати and видалити
  - Error: missing `якщо` clause
  - Error: malformed guard (not a comparison/negation)
  - Round-trip test: parse → `__repr__` → parse again gives the same AST

**Dependencies:** MINILOG-005

**Expected result:**
Production rules can be written in `.ml` files and parsed into `ProductionRuleDef` instances stored in `Program.production_rules`. The parser rejects malformed production rules at parse time with clear error messages.

**Acceptance criteria:**
- [ ] `ProductionRuleDef` class exists in `parser.py`
- [ ] Grammar supports all three shapes (додати-only, видалити-only, both)
- [ ] Optional `коли` guard parses correctly
- [ ] Validation rejects empty effect clause
- [ ] `Program.production_rules` contains parsed rules
- [ ] 10+ unit tests passing
- [ ] No regressions in existing parser tests
- [ ] Clear error messages for malformed input

---

## MINILOG-094 — KnowledgeBase integration for production rules

**Description:**
Extend `minilog/kb.py` to store production rules alongside facts and regular rules. This makes production rules first-class members of the knowledge base, so that `:load`, `:kb`, `:stats`, and `:clear` all handle them correctly, and `:evolve` can retrieve them without being passed a separate list.

**What needs to be done:**

- In `KnowledgeBase.__init__`, add new field `self._production_rules: list[ProductionRule] = []`
- Add method `add_production_rule(rule: ProductionRule) -> None` that appends to the list
- Add method `production_rules() -> list[ProductionRule]` that returns a copy of the list (defensive, to prevent accidental mutation)
- Add method `clear_production_rules() -> None` that empties the list
- Add method `add_fact_if_new(fact: Fact) -> bool` that adds a fact only if an equal fact is not already present in `_facts[(functor, arity)]`, returning `True` on insertion and `False` on duplicate. This is a new method — the existing `add_fact` always appends without checking duplicates and returns `None`, which is insufficient for `run_generations` deduplication and change detection
- Add conversion helper: `ProductionRuleDef` (from parser) → `ProductionRule` (from `evolution.py`). This may be a module-level function `build_production_rule(def_: ProductionRuleDef) -> ProductionRule` that wraps the condition and guard into the single `Compound` expected by `evolution.ProductionRule`
- Update `KnowledgeBase.stats()` to include production rule count:
  ```python
  {"facts": N, "rules": M, "production_rules": K, "predicates": P}
  ```
- Update REPL `:load` to call `kb.add_production_rule` for each `ProductionRuleDef` in the parsed program (loop through `program.production_rules`)
- Update REPL `:clear` to also clear production rules
- Update REPL `:stats` to display production rule count if non-zero
- Update REPL `:kb` dump to show production rules in a separate `% Production rules` section
- Write ≥6 unit tests in `tests/unit/test_kb_production.py`:
  - Empty KB has no production rules
  - Adding a production rule increases count
  - `production_rules()` returns a defensive copy
  - `clear_production_rules` empties only production rules, not facts/rules
  - `stats()` reflects production rule count
  - Loading a `.ml` file with production rules populates KB correctly

**Dependencies:** MINILOG-093, MINILOG-007

**Expected result:**
Production rules are stored in the knowledge base as first-class members. Loading a file with production rules adds them to the KB; clearing the KB removes them; statistics report them; the `:kb` dump shows them.

**Acceptance criteria:**
- [ ] `_production_rules` field exists in `KnowledgeBase`
- [ ] Production rule CRUD methods (`add`, `list`, `clear`) work correctly
- [ ] New `add_fact_if_new` method added, returns `True` on insertion and `False` on duplicate
- [ ] `stats()` includes production rule count
- [ ] REPL `:load` populates production rules from parsed program
- [ ] REPL `:clear` removes them
- [ ] REPL `:kb` dumps them in a labeled section
- [ ] 6+ unit tests passing
- [ ] No regressions in existing KB tests

---

## MINILOG-095 — Fix `run_generations` two-phase semantics and fixpoint detection

**Description:**
The current `run_generations()` in `minilog/evolution.py` has two correctness issues that must be fixed before production rules can be reliably used. First, it mutates the knowledge base during iteration over condition matches, which creates a race condition where facts added by earlier substitutions can be matched by later substitutions in the same generation, making the result order-dependent and non-reproducible. Second, it always runs the full N generations even when a generation produces no changes, wasting time and obscuring the fact that a fixpoint has been reached.

This issue replaces the implementation with the classical two-phase approach used by Rete-based production systems (OPS5, CLIPS): in each generation, first collect **all** matches for **all** rules against an immutable snapshot of the KB, then apply all resulting additions and removals atomically.

**What needs to be done:**

- Rewrite `run_generations(kb, rules, n, detect_fixpoint=True, max_cap=10000)` in `minilog/evolution.py`:

  ```python
  def run_generations(
      kb: KnowledgeBase,
      rules: list[ProductionRule],
      n: int,
      detect_fixpoint: bool = True,
      max_cap: int = 10000,
  ) -> list[dict]:
      effective_n = min(n, max_cap)
      history: list[dict] = []
      for gen in range(effective_n):
          # Phase 1: collect all planned changes over current KB
          planned_adds: list[Fact] = []
          planned_removes: list[Fact] = []
          snapshot = kb  # reads are safe; no writes yet in this phase
          for rule in rules:
              for subst in solve(rule.condition, snapshot):
                  # Apply optional guard
                  if rule.guard is not None:
                      if not _evaluate_guard(rule.guard, subst):
                          continue
                  for add_term in rule.add:
                      planned_adds.append(Fact(head=subst.apply(add_term)))
                  for remove_term in rule.remove:
                      planned_removes.append(Fact(head=subst.apply(remove_term)))

          # Phase 2: apply changes, deduplicated
          added: list[Fact] = []
          seen_adds: set = set()
          for fact in planned_adds:
              key = repr(fact.head)
              if key in seen_adds:
                  continue
              seen_adds.add(key)
              if kb.add_fact_if_new(fact):
                  added.append(fact)

          removed: list[Fact] = []
          seen_removes: set = set()
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
  ```

- The snapshot concept is implemented trivially by using `kb` itself during the collection phase, provided no writes happen during collection. Python's iteration over `solve()` does not mutate the KB, so a true copy is unnecessary — discipline is enforced by not calling `kb.add_fact` inside the inner loop
- Add helper `_evaluate_guard(guard, subst) -> bool` that handles `Comparison` and `Negation` guards by calling `check_comparison` from `evaluator.py` or the negation-as-failure path from `engine.py`
- `KnowledgeBase.add_fact_if_new` is added in MINILOG-094; this issue only consumes it for deduplication and change detection
- `KnowledgeBase.remove_fact` already exists from Phase 1 (MINILOG-007) and returns `bool` indicating whether the fact was found and removed — no changes required to `kb.py` for removal semantics
- Ordering: the order of `planned_adds` and `planned_removes` should be deterministic. Use insertion order (Python dicts preserve insertion order since 3.7), and process rules in the order they appear in the input list
- Write ≥10 unit tests in `tests/unit/test_evolution.py`:
  - Empty KB, empty rules: `run_generations` returns empty history after one iteration (fixpoint)
  - Single rule that adds one fact: history shows one added fact in generation 0, fixpoint in generation 1
  - Rule that adds then removes: verify atomic semantics
  - Two rules in same generation: verify they see the same snapshot
  - Rule with guard that filters all matches: no changes
  - Rule with guard that accepts some matches: only those are applied
  - Fixpoint detection: after 3 generations with no changes, `run_generations(kb, rules, 100)` returns history of length 4 (3 + 1 fixpoint)
  - Max cap: `run_generations(kb, rules, 20000)` runs at most 10000 generations
  - Deterministic ordering: multiple calls produce identical history
  - Race condition regression test: a rule whose condition matches facts added by the rule itself in the same generation does NOT trigger recursion within one generation

**Dependencies:** MINILOG-094

**Expected result:**
Production rules run with correct atomic semantics (no intra-generation race conditions), stop early when fixpoint is reached, and are safely bounded by the max cap. History reflects exactly what changed in each generation.

**Acceptance criteria:**
- [ ] Two-phase collect/apply implemented
- [ ] Guard evaluation works for comparison and negation
- [ ] Fixpoint detection exits early
- [ ] Max cap prevents infinite loops
- [ ] Deterministic ordering verified by repeatable tests
- [ ] 10+ unit tests passing
- [ ] Race condition regression test passes
- [ ] No regressions in existing evolution tests

---

## MINILOG-096 — REPL `:evolve <N>` command full implementation

**Description:**
The REPL `_cmd_evolve` method currently parses the argument `N` but then does nothing meaningful — it prints `"no production rules loaded (use programmatic API)"`. This issue wires the command to the fixed `run_generations` from MINILOG-095 and the KB production rules from MINILOG-094, with user-friendly output formatting.

**What needs to be done:**

- Rewrite `_cmd_evolve` in `minilog/repl.py`:

  ```python
  def _cmd_evolve(self, arg: str) -> None:
      try:
          n = int(arg) if arg else 1
      except ValueError:
          print("Usage: :evolve <N> (N must be a positive integer)")
          return
      if n <= 0:
          print("Usage: :evolve <N> (N must be positive)")
          return
      if n > 10000:
          print(f"Warning: capping at 10000 generations (requested {n})")
          n = 10000

      rules = self.kb.production_rules()
      if not rules:
          print("No production rules in the knowledge base. Load a file with `продукція` declarations.")
          return

      rule_label = "rule" if len(rules) == 1 else "rules"
      gen_label = "generation" if n == 1 else "generations"
      print(f"Running up to {n} {gen_label} of {len(rules)} production {rule_label}...")

      try:
          history = run_generations(self.kb, rules, n)
      except MinilogError as e:
          print(f"Error during evolution: {e}")
          return

      # Pretty-print history
      total_added = 0
      total_removed = 0
      fixpoint_gen = None
      for entry in history:
          gen = entry["generation"]
          added = entry["added"]
          removed = entry["removed"]
          total_added += len(added)
          total_removed += len(removed)
          if not added and not removed:
              fixpoint_gen = gen + 1
              print(f"  Generation {gen + 1}: no changes (fixpoint reached)")
              break
          parts = []
          if added:
              parts.append(f"+{len(added)} fact{'s' if len(added) != 1 else ''}")
          if removed:
              parts.append(f"-{len(removed)} fact{'s' if len(removed) != 1 else ''}")
          print(f"  Generation {gen + 1}: {', '.join(parts)}")

      executed = len(history)
      print(f"Done. {executed} {'generation' if executed == 1 else 'generations'} executed, "
            f"{total_added} added, {total_removed} removed.")
  ```

- Error message reminds the user how to load production rules (`продукція` keyword)
- Output format: one line per generation with counts, final summary line
- Max generations cap with warning (matches `run_generations` cap)
- Write ≥6 integration tests in `tests/integration/test_repl_evolve.py`:
  - `:evolve 1` with no production rules prints friendly error
  - `:evolve abc` prints usage error
  - `:evolve 0` prints usage error
  - `:evolve 3` on a KB with one production rule runs and reports correctly
  - `:evolve 100` reaches fixpoint early and reports it
  - `:evolve 20000` prints warning and caps at 10000

**Dependencies:** MINILOG-094, MINILOG-095

**Expected result:**
After this issue, `:evolve <N>` is a fully working REPL command. A user can load a `.ml` file with production rules, run `:evolve 10`, see a generation-by-generation summary of changes, and then inspect the resulting KB state with `:kb`, `?- query.`, or `:stats`.

**Acceptance criteria:**
- [ ] `:evolve <N>` reads production rules from KB
- [ ] Generation-by-generation output with counts
- [ ] Fixpoint detection reported in output
- [ ] Max cap warning printed when exceeded
- [ ] Error messages for invalid arguments
- [ ] 6+ integration tests passing
- [ ] Help text in `HELP_TEXT` remains accurate

---

## MINILOG-097 — Evolution example: population aging simulation

**Description:**
Create a flagship example that showcases production rules through a realistic simulation scenario. The example models a small population over time, where individuals age, transition between life stages (child → adult → elder), and eventually die. This is the evolution subsystem analogue of what `examples/family.ml` is for the backward chaining engine — a single clear example that users run first to understand the feature.

**Scenario:**
A population of 5-8 named individuals with initial ages. Each generation represents roughly 10 years passing. Production rules handle:
- Aging: increment every individual's age by 10
- Child → Adult transition at age 18
- Adult → Elder transition at age 60
- Death: individuals over age 90 die and are removed from the living population

This is small enough to be fully auditable (the user can predict every state change), but dynamic enough to showcase multiple generations producing meaningful change. A `.expected.txt` file captures the state after each evolution step via queries.

**What needs to be done:**

- Create `examples/evolution_aging.ml` (~120 lines) containing:
  - Header comment explaining the scenario, what it demonstrates, and the contrast with regular rules
  - Initial facts: 5-8 individuals with ages (e.g., `особа(марко, 12)`, `особа(анна, 45)`, `особа(василь, 88)`, etc.)
  - Initial stage facts: `дитина(марко)`, `дорослий(анна)`, `літній(василь)` depending on initial age
  - A `живий/1` predicate for individuals currently in the population
  - ~4-5 production rules demonstrating various aspects:
    ```
    продукція старіння якщо особа(?x, ?v) і живий(?x)
        додати особа(?x, ?v_новий)
        видалити особа(?x, ?v)
        коли ?v_новий = ?v + 10.

    продукція повноліття якщо дитина(?x) і особа(?x, ?v)
        додати дорослий(?x)
        видалити дитина(?x)
        коли ?v ≥ 18.

    продукція літність якщо дорослий(?x) і особа(?x, ?v)
        додати літній(?x)
        видалити дорослий(?x)
        коли ?v ≥ 60.

    продукція смерть якщо літній(?x) і особа(?x, ?v)
        видалити живий(?x), літній(?x), особа(?x, ?v)
        коли ?v > 90.
    ```
  - Queries showing state before any evolution runs (baseline):
    ```
    ?- особа(?x, ?v).
    ?- дитина(?x).
    ?- дорослий(?x).
    ?- літній(?x).
    ```
  - REPL usage note in comment: "Run `:evolve 5` to simulate 50 years passing, then repeat the queries above to see state evolution"

- Create `examples/evolution_aging.expected.txt` with expected query output at the initial state (before any `:evolve` is run). The evolution-applied state is not included in expected.txt because it depends on the REPL session order. Alternative: include both baseline and post-evolution state, with a clear marker dividing them

- Create `tests/integration/test_evolution_aging.py` that:
  - Loads the example file
  - Verifies baseline queries match expected.txt
  - Programmatically runs `run_generations(kb, rules, 5)` and verifies the resulting state matches expected post-evolution snapshot
  - Uses deterministic ordering so results are reproducible

**Dependencies:** MINILOG-096

**Expected result:**
A flagship example that demonstrates production rules in a scenario readable by anyone: individuals age, transition through life stages, eventually die. Users can load it, run `:evolve 5`, and observe the population dynamics change meaningfully. Contrasts with Phase 1 examples that had static knowledge bases.

**Acceptance criteria:**
- [ ] `examples/evolution_aging.ml` exists and runs
- [ ] `examples/evolution_aging.expected.txt` exists and matches baseline output
- [ ] 4-5 production rules covering aging, stage transitions, death
- [ ] Conditional guards use `коли` clause
- [ ] Multi-term `видалити` clauses demonstrated
- [ ] Integration test passes
- [ ] File length ~100-130 lines
- [ ] Header comment explains scenario and how to use

---

## MINILOG-098 — Explainer document: production rules and generations

**Description:**
Create `docs/evolution-production-rules-explained.md` as the companion document to `examples/evolution_aging.ml`, mirroring the structure of `docs/geometry-triangles-explained.md` from Phase 10. This is a conceptual walkthrough of what production rules are, how they differ from regular rules and forward chaining, what generations mean, and why the two-phase atomic semantics matter.

**What needs to be done:**

Create `docs/evolution-production-rules-explained.md` with nine sections (Ukrainian main text, English technical terms, no emoji, style matching `prolog-state-2025.md`, `prolog-engine-explained.md`, and `geometry-triangles-explained.md`):

1. **Introduction** — what the document covers, who it is for, relation to `examples/evolution_aging.ml` and the REPL command `:evolve`

2. **Three reasoning modes in minilog** — backward chaining (regular rules, query-driven, declarative), forward chaining / saturation (regular rules, data-driven, monotonic), and evolution (production rules, data-driven, non-monotonic with add/remove). Table comparing them. Why all three exist and when to use each

3. **Production rules formally** — definition as `продукція <n> якщо C додати A видалити R коли G` mapping to an `(C, G, A, R)` tuple. Operational semantics: for every substitution σ such that σ(C) holds and σ(G) is satisfied, plan `σ(A)` additions and `σ(R)` removals

4. **Generations and atomic semantics** — why the two-phase approach matters. The race condition that would occur if mutations happened during iteration, illustrated with a small example. How Rete-based systems (OPS5, CLIPS) handle this historically. The importance of reproducibility in simulations

5. **Fixpoint and termination** — when a generation produces no changes, the simulation has reached a fixpoint. Why detecting fixpoints is important (performance, correctness signal). Why some production rule systems never reach fixpoint (oscillating rules). Why minilog has a max generations cap

6. **Guards and why they matter** — the `коли` clause as a filter after condition matching. Contrast with including guards directly in the condition body (would be checked during condition solving, often slower for combinatorial conditions). Examples with `?v > 60`, `не мертвий(?x)`

7. **Walkthrough of the aging example** — step-by-step execution of the four production rules over 5 generations on the initial population from `evolution_aging.ml`. Show the state after each generation. Make clear which rule triggers for which individual. Point out where fixpoint would be reached and why

8. **Relation to other phases and broader context** — Phase 3 (ca-evolution) will use production rules for Codex Seraphinianus category dynamics. Phase 5 (terra-tacita-canon) may use them for character state in literary simulation. Historical context: production rules as a knowledge representation paradigm (OPS5, CLIPS, JESS, Drools). Relation to cellular automata and agent-based modeling

9. **Strengths and limitations** — Strengths: declarative state transitions, atomic semantics, clean separation from backward chaining queries. Limitations: no conflict resolution strategies (all matching rules fire), no priorities, no event-driven triggers, single-threaded. What would require Phase 11+

**Formatting:** ~10-14 pages (500-700 markdown lines), Ukrainian text with English technical terms, no emoji, all code snippets must match `examples/evolution_aging.ml` exactly, cross-links to `language-reference.md` (REPL commands section) and `prolog-engine-explained.md` (backward chaining).

**Dependencies:** MINILOG-097

**Acceptance criteria:**
- [ ] Document exists at `docs/evolution-production-rules-explained.md`
- [ ] Length 10-14 pages
- [ ] All nine sections present
- [ ] All code snippets match `examples/evolution_aging.ml`
- [ ] Cross-links work
- [ ] No emoji
- [ ] Renders cleanly on GitHub preview
- [ ] Section 7 walkthrough traces 5 generations accurately

---

## MINILOG-099 — README and language reference integration

**Description:**
Integrate the new evolution subsystem and example into user-facing documentation surfaces: add production rule syntax to `docs/language-reference.md`, update `README.md` to mention the new capability and example, ensure readers can discover the feature naturally.

**What needs to be done:**

- Update `docs/language-reference.md`:
  - Add new section "Виробничі правила (production rules)" describing:
    - Syntax of `продукція` with all three clauses (`додати`, `видалити`, `коли`)
    - Difference from regular rules (`правило`)
    - When to use each
    - Cross-link to `evolution-production-rules-explained.md` for deep explanation
  - Add `:evolve <N>` to the REPL commands section with syntax and brief example
  - Add `:saturate` to the REPL commands section (missing today) with brief description
  - Add entry for `evolution_aging.ml` in the "Приклади" section
- Update `README.md`:
  - Add mention of `evolution_aging.ml` in the examples list
  - One-sentence description: "Population dynamics simulation using production rules over generations"
  - Link to the companion document
  - If README has a roadmap, mark Phase 10.5 complete
- Update `docs/language-reference.md` table of contents if present
- Verify all cross-links work
- Optionally: add a short "What's new" blurb to README noting that production rules now work end-to-end in the REPL

**Dependencies:** MINILOG-097, MINILOG-098

**Acceptance criteria:**
- [ ] `language-reference.md` has new section on production rules
- [ ] `language-reference.md` mentions `:evolve` and `:saturate` in REPL commands
- [ ] `language-reference.md` examples section includes `evolution_aging.ml`
- [ ] `README.md` mentions the evolution example
- [ ] All cross-links verified
- [ ] No broken links
- [ ] If README has roadmap, Phase 10.5 status updated

---

## Phase 10.5 scope notes

Phase 10.5 is a **single cohesive package** — one subsystem completion delivered with full supporting material, matching the pattern established by Phase 10. The work is broken into seven issues with a strict dependency chain:

- MINILOG-093 (parser) is the foundation; all other issues depend on it transitively
- MINILOG-094 (KB) depends on parser output shape
- MINILOG-095 (engine fix) is independent of parser but must complete before REPL command can be reliably tested
- MINILOG-096 (REPL) wires the previous three together
- MINILOG-097 (example) needs the working REPL command to produce expected output
- MINILOG-098 (explainer) needs the example to reference it accurately
- MINILOG-099 (integration) is the final polish step

**Total effort:** ~3-4 days (M + S + M + S + M + M + S).

**Hard prerequisites:**
- Phase 1 core (parser, KB, engine, REPL, unify, terms) — all merged
- Phase 9 arithmetic (MINILOG-021..024) — required because the aging example uses numeric comparison in guards (`коли ?v ≥ 18`) and increment in production rule effects (`?v_новий = ?v + 10`)

Without Phase 9, the example could still be written but would need to use facts like `старший(18, 28)` as explicit lookup tables instead of arithmetic, which defeats the purpose of showing realistic simulation.

**Files created by Phase 10.5:**
- `examples/evolution_aging.ml` (~120 lines)
- `examples/evolution_aging.expected.txt` (generated)
- `tests/unit/test_parser_production.py` (~200 lines)
- `tests/unit/test_kb_production.py` (~100 lines)
- `tests/unit/test_evolution.py` (new file or extension; ~250 lines)
- `tests/integration/test_repl_evolve.py` (~150 lines)
- `tests/integration/test_evolution_aging.py` (~60 lines)
- `docs/evolution-production-rules-explained.md` (~600 lines)

**Files modified by Phase 10.5:**
- `minilog/lexer.py` (new keywords)
- `minilog/parser.py` (new grammar, new AST class)
- `minilog/kb.py` (new storage and methods)
- `minilog/evolution.py` (rewritten `run_generations`)
- `minilog/repl.py` (working `_cmd_evolve`)
- `docs/language-reference.md` (production rules section, REPL commands, examples list)
- `README.md` (examples list, roadmap)

**Files NOT touched by Phase 10.5:**
- `minilog/engine.py` — the backward chaining engine is untouched; production rules use `solve()` as a black box for condition matching
- `minilog/unify.py`, `minilog/terms.py` — term model unchanged
- `minilog/evaluator.py`, `minilog/forward.py` — independent mechanisms
- `minilog/tracer.py` — production rules do not currently produce proof trees; traced generations are a potential future enhancement

**After Phase 10.5 is merged,** minilog has a complete evolution subsystem with end-to-end workflow: write production rules in `.ml` files, load them into KB, run `:evolve N` to advance state, query the evolved state normally. This enables the next wave of examples where knowledge bases change over time — a prerequisite for Phase 3 (ca-evolution) and useful for any agent-based or simulation-style use case in future phases.

---

**Document status:** draft for review. All seven issues are fully detailed with acceptance criteria and implementation notes. Ready for implementation after human review of the architectural decisions table.

**No code changes made. Plan only.**
