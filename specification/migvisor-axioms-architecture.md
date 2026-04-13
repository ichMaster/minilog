# migvisor-axioms — Reasoning Architecture Design

**Status:** draft for review
**Scope:** reasoning layer for Phase 4 migvisor-axioms over Neo4j knowledge graph
**Document type:** architectural decision record (ADR) + recommendation
**Related:** Phase 4 — migvisor-axioms (Notion)

---

## Problem Statement

migvisor-axioms is the axiomatic validation layer for data warehouse migration projects. It operates over a knowledge graph of schemas, tables, columns, dependencies, lineage, and migration artifacts stored in Neo4j. The layer must support five categories of reasoning tasks:

- **A — Simple graph analysis.** Impact analysis, transitive dependencies, pattern matching, lineage traversal. Example: "which reports break if column X is removed?"
- **B — Rule-based classification.** Derivation of schema properties from base facts. Example: "is this schema a star, snowflake, or data vault?"
- **C — Optimization.** Constraint-based planning. Example: "find the optimal migration order for 500 tables that minimizes downtime while respecting all foreign-key dependencies."
- **D — Formal verification.** Semantic preservation axioms. Example: "prove that migration A → B preserves the semantics of all SELECT queries."
- **E — All of the above** in the same project, in different proportions.

The question: **which reasoning tool(s) should migvisor-axioms use** to cover all five categories without reinventing the wheel or locking into a single technology that does not fit all cases?

---

## Non-Goals

This document does NOT cover:

- Neo4j schema design for migvisor-axioms (separate concern)
- ETL pipelines that populate the Neo4j graph (handled by migvisor ingestion layer)
- UI/API layer on top of the reasoning engine
- minilog or any educational Prolog — these are out of scope for production reasoning over Neo4j

---

## Why Not Prolog / minilog

A natural first thought is "use Prolog (or minilog) as the rule engine." This is rejected for the following reasons:

1. **Prolog is in-memory, not database-backed.** Every query requires exporting facts from Neo4j to Prolog clauses, loading them into the interpreter, running the query, and writing results back. This is an ETL cycle per query and does not scale beyond thousands of facts
2. **No built-in constraint propagation.** Pure Prolog does chronological backtracking without memory of conflicts. For combinatorial search (category C), this is orders of magnitude slower than modern SAT-based solvers
3. **No optimization primitives.** Finding an optimal plan (as opposed to any valid plan) requires weighted constraints, which vanilla Prolog does not express
4. **minilog specifically is an educational tool**, not production infrastructure. It is Phase 1 of a teaching language, not a reasoner designed for enterprise data volumes
5. **Loss of Neo4j benefits.** Exporting to Prolog means losing the indexes, persistence, concurrency, and transactional guarantees of the graph database

Prolog remains the right choice for categories that need proof trees as primary deliverable (explainability-first contexts), but migvisor-axioms is not primarily explainability-driven — it is correctness-driven and performance-driven.

---

## Recommended Architecture: Three-Tier Reasoning Stack

The recommendation is a layered architecture where each tier handles the tasks it is best suited for, and tiers communicate through well-defined interfaces.

### Tier 1 — Cypher + Neo4j GDS (Graph Data Science)

**Purpose:** primary tool for categories A (simple graph analysis) and parts of B (simple classification).

**What it covers:**

- Transitive closure through Cypher's `[:REL*]` variable-length path operator
- Shortest path and all-paths queries
- Pattern matching with complex predicates (subqueries via `CALL { }`)
- Built-in graph algorithms from the GDS library: PageRank, community detection, centrality measures, topological sort, cycle detection, strongly connected components, weakly connected components, all-pairs shortest paths
- Aggregations, grouping, windowing
- Recursive queries through `WITH RECURSIVE` (in newer GQL-compliant Cypher versions)

**Estimated coverage:** 60–70% of typical migration analysis tasks. Impact analysis, lineage queries, dependency traversal, cycle detection in FK graphs, topological sorting for migration order — all of these are solved natively without any external reasoner.

**Advantages:**

- Native to Neo4j: zero data movement, leverages indexes and caches
- Fast on large graphs (millions of nodes)
- Mature ecosystem with tooling (Bloom for visualization, Browser for exploration, Desktop for local dev)
- Standard query language already known to data engineers
- No additional dependencies, no Python bridge, no serialization overhead

**Limitations:**

- No rule-based inference with defaults or exceptions
- No optimization (can find paths but not optimal paths with cost functions over complex constraints)
- Transitive closure produces all paths, which can be expensive without `DISTINCT`
- Multi-type transitive reasoning (`A depends on B through FK OR view OR ETL`) requires verbose UNION queries
- No formal verification capabilities

### Tier 2 — Soufflé (Datalog) or Clingo (ASP) via Python Bridge

**Purpose:** secondary reasoner for categories B (rule-based derivation) and C (optimization).

**Why two candidates:**

Soufflé and Clingo solve overlapping but distinct problems. Soufflé is a pure Datalog compiler that produces C++ code and runs extremely fast on large fact bases (millions of facts). It is the right choice when the task is expressible as recursive rules without default negation or optimization. Clingo is an ASP solver that handles rule-based reasoning with defaults, choice rules, and optimization constraints. It is the right choice when the task involves combinatorial search, optimization, or non-monotonic reasoning.

**Recommended split:**

- **Use Soufflé** for rule-based derivation that is purely monotonic. Classification rules ("this table is a fact table if it has at least 2 FKs to dimension tables"), transitive derivation with composition ("depends on through any of 5 relation types"), taxonomy-style inference. These are Datalog's bread and butter
- **Use Clingo** for optimization and constraint satisfaction. Migration planning ("find minimum-cost migration order subject to dependency constraints"), consistency checking with multiple models, resource allocation problems. These are ASP's bread and butter

**Integration pattern** (same for both):

1. Cypher query extracts relevant subgraph from Neo4j
2. Python glue code converts the result into the reasoner's fact format (Soufflé `.facts` files or Clingo ground atoms)
3. The reasoner runs against pre-written rule files, producing derived facts or answer sets
4. Python converts results back into Cypher MERGE statements or property updates
5. Neo4j is updated with the derivation results as new relationships or node properties

This is the **export-reason-import loop**, and it is the standard pattern used in production systems that combine graph databases with external reasoners.

**Estimated coverage:** 20–30% of tasks. Everything Tier 1 cannot express naturally, plus all optimization tasks.

**Advantages of Soufflé:**

- Compiles Datalog to C++ for extreme speed on large fact bases
- Pure logic, no non-monotonic complications, easy to reason about
- Used in production for static analysis (Doop, various compiler toolchains)
- Clean syntax, close to what humans expect from rule systems

**Advantages of Clingo:**

- Native optimization with `#minimize` and `#maximize`
- Non-monotonic reasoning with default negation and choice rules
- Handles multi-model problems (diagnostic reasoning, abductive inference)
- Rich Python API for embedding in larger systems
- Battle-tested on hard combinatorial problems (planning, scheduling, configuration)

**Limitations of both:**

- Require Python bridge — not "native" to Neo4j
- In-memory: large fact bases must be materialized before reasoning starts
- Cold-start cost: loading facts takes time proportional to subgraph size
- No transactional guarantees — reasoning is read-only, with results written back in a separate transaction

### Tier 3 — SHACL or Theorem Prover (Optional)

**Purpose:** formal verification for category D, when needed.

**When needed:**

This tier is only relevant if migvisor-axioms must prove formal properties about migrations — for example, semantic preservation (migration A → B preserves the result of every SELECT query over the old schema when rewritten for the new schema). This is research-level work and most production migration projects do not need it.

**Candidates:**

- **SHACL shapes via neosemantics (n10s)**: a Neo4j plugin that adds RDF import/export, basic OWL inference, and SHACL validation. If axioms can be expressed as structural constraints ("every fact table must have a primary key; every FK must reference an existing PK"), SHACL is sufficient and stays within Neo4j
- **Z3 SMT solver**: if axioms involve arithmetic, type systems, or query equivalence, Z3 is the standard tool. Python bindings make integration straightforward
- **Lean or Coq**: for true theorem proving about schema migrations. Overkill for almost all production uses

**Estimated coverage:** 0–5% of tasks for typical migration projects, potentially higher for mission-critical systems (banking, medical records, regulatory compliance).

---

## Decision Matrix by Task Category

| Category | Primary Tier | Fallback | Notes |
|---|---|---|---|
| **A** Simple graph analysis | Tier 1 (Cypher + GDS) | — | Native coverage, zero external dependencies |
| **B** Rule-based classification | Tier 2 (Soufflé) | Tier 1 for simple cases | Datalog is the natural fit; use Cypher only for trivial classifications |
| **C** Optimization and planning | Tier 2 (Clingo) | — | ASP is the right tool; do not attempt in Cypher |
| **D** Formal verification | Tier 3 (SHACL or Z3) | Tier 2 (Clingo with constraints) | Only for projects that genuinely need formal proofs |
| **E** Mixed workloads | All tiers | — | Route each task to the appropriate tier |

---

## Comparison to Alternative Architectures

### Alternative 1: "All Cypher, no external tools"

**Pros:** simplest stack, no Python bridge, no serialization, no additional dependencies.

**Cons:** cannot handle categories C (optimization) and D (formal verification) at all. Category B (classification) becomes awkward for anything beyond trivial rules. Risks being insufficient for real migration projects.

**Verdict:** acceptable ONLY if the project scope can be firmly limited to categories A and simple B.

### Alternative 2: "All Clingo, Neo4j as dumb storage"

**Pros:** single reasoning tool, consistent mental model, handles all five categories (A through D with some effort).

**Cons:** forces every query through the Python bridge even when Cypher would solve it natively in milliseconds. Grounding bottleneck for large graphs (Clingo's grounder can blow up memory on million-node graphs). Loses the speed advantage of Neo4j's indexes for basic traversal. Team must learn ASP, which has a steeper learning curve than Cypher.

**Verdict:** rejected. Misuses Clingo for tasks Cypher does better, and fights the database instead of cooperating with it.

### Alternative 3: "Switch to GraphDB + RDF + OWL + SHACL"

**Pros:** RDF/OWL is the traditional stack for knowledge engineering with formal axioms. SHACL gives validation out of the box. OWL reasoners give inference out of the box. Federated queries over external RDF datasets (DBpedia, Wikidata).

**Cons:** requires abandoning Neo4j as primary storage, which is architecturally significant. Property graph model is not RDF — conversion is lossy or verbose. Team must learn SPARQL, Turtle, and OWL semantics. Smaller ecosystem than Neo4j.

**Verdict:** rejected for this project because Neo4j is already selected and the overhead of migration is not justified by the gain. Would be the right choice if starting from scratch with a formal-axioms-first mandate.

### Alternative 4: "Neo4j + RDFox as embedded Datalog reasoner"

**Pros:** RDFox is a high-performance Datalog reasoner with native RDF support and can run embedded alongside a graph database. Handles rule-based derivation at production scale. Commercial with academic free edition.

**Cons:** RDFox operates on RDF, not property graph. Requires converting Neo4j data to RDF on every reasoning run, similar to Soufflé but with a different format. Commercial licensing for production use.

**Verdict:** viable alternative to Soufflé in Tier 2 if budget allows and the team prefers a commercial product with support. Functionally similar.

---

## Implementation Plan (High-Level)

The recommended rollout is incremental, starting from Tier 1 and adding Tier 2 only when actual use cases demand it.

### Phase 4.1 — Tier 1 Baseline

**Duration estimate:** 2–3 weeks

- Install Neo4j locally with GDS and neosemantics (n10s) plugins
- Load a representative test dataset (a small DWH with 20–50 tables, FK dependencies, views, ETL lineage)
- Write a reference library of 20–30 Cypher queries covering common migration analysis tasks (impact analysis, lineage, pattern detection, cycle detection, topological sort)
- Document coverage: which tasks work natively in Cypher, which need more power
- Establish Cypher query style guide for the team

**Deliverable:** Cypher query library + coverage report. After this phase, it should be clear how much of migvisor-axioms can be covered by Tier 1 alone.

### Phase 4.2 — Tier 2 Integration

**Duration estimate:** 3–4 weeks (triggered only if Phase 4.1 coverage report shows significant gaps)

- Choose between Soufflé and Clingo based on which tasks dominate the gap (Soufflé if mostly classification; Clingo if mostly optimization; both if mixed)
- Build a Python bridge service that: accepts a task specification (Cypher query for data extraction + rule set identifier), extracts data, invokes reasoner, writes results back
- Write initial rule sets for the most common derivation and optimization tasks
- Integrate with migvisor CI/CD so that reasoning runs on every schema change

**Deliverable:** reasoning service + rule library covering Tier 1 gaps.

### Phase 4.3 — Tier 3 (Optional)

**Duration estimate:** 4–8 weeks (triggered only if formal verification becomes a requirement)

- Evaluate whether SHACL shapes are sufficient or full theorem proving is needed
- If SHACL: add neosemantics-based shape validation to the CI pipeline
- If Z3: build a separate verification service that checks specific axioms on critical migrations

**Deliverable:** formal verification capability for critical migrations.

---

## Open Questions

The following questions are deferred to later design iterations:

1. **Axiom authoring experience.** Who writes the axioms? Data engineers (in which case Cypher and Python are fine) or domain experts (in which case a higher-level DSL may be needed)?
2. **Real-time vs. batch reasoning.** Are migvisor-axioms checks run on-demand during schema changes, or periodically as a batch validation job? Real-time requires incremental solving (which Clingo supports through its Python API) and careful caching
3. **Explainability requirements.** If the output of reasoning must be explainable to non-technical stakeholders (regulators, auditors), the reasoner must produce proof traces. Datalog and Prolog excel at this; Clingo and SAT-based tools less so
4. **Reasoning result persistence.** Are derived facts written back to Neo4j as first-class nodes and relationships (making them queryable), or kept as ephemeral query results? The former adds storage but enables composition of reasoning steps
5. **Rule versioning and governance.** Axiom rules are code. They need version control, review, testing, and a release process. This is standard software engineering but easy to overlook when the rules live outside the main codebase

---

## Recommendation Summary

**Primary stack:** Neo4j + Cypher + GDS + neosemantics (n10s), covering 60–70% of reasoning tasks natively.

**Secondary stack:** Python bridge to Soufflé (for rule-based derivation) and Clingo (for optimization), covering the remaining 20–30% of tasks that Cypher cannot express elegantly or at all.

**Optional tier:** SHACL shapes via n10s for structural validation, Z3 for formal verification, activated only when project scope explicitly requires formal proofs.

**Explicitly rejected:** Prolog or minilog as the reasoning backbone. These are the wrong tools for production reasoning over a Neo4j knowledge graph. minilog stays in its role as an educational tool and as the backbone for the separate text extraction pipeline (Phases 11–14 in the main minilog spec).

**Recursive rules are well-supported in both recommended reasoners.** Cypher handles transitive closure through `[:REL*]`. Soufflé and Clingo handle full recursive rules with guaranteed termination (Soufflé because Datalog has no function symbols; Clingo because grounding produces a finite propositional program). Recursion is not a concern in this architecture.

---

**Document status:** draft for review. No code changes made. Plan only.
