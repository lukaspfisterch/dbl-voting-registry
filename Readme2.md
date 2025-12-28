# KL vs. DBL (Conceptual Positioning)

This project is built under two distinct but complementary layers:

## KL (Kernel Logic)
**KL is a conceptual constraint model**, not a runtime dependency.  
It defines the thinking discipline under which this Domainrunner is designed:

- **no implicit normativity**
- **no derivation of decisions from observations**
- **no hidden state transitions**
- **no semantic shortcuts**

KL does not provide APIs or executable components. It governs what is admissible to model and what must be made explicit.

In this repository, KL is present through:
- the absence of implicit decision logic
- the strict refusal to derive state from observational data
- the requirement that all normative effects appear as explicit events

**KL acts as a normative guardrail.** You do not import it. You either respect it or violate it.

## DBL (Deterministic Boundary Layers)
**DBL is an operational substrate.**  
`dbl-core` provides the concrete mechanisms that make KL-style constraints enforceable and testable:

- **canonical event representation** (`DblEvent`)
- **explicit separation of data** (normative) vs observational
- **append-only, ordered event stream** (`BehaviorV`)
- **deterministic canonical projection** (digest)
- **replayable audit without re-execution**

DBL is where conceptual constraints become verifiable invariants.

In this project, DBL is used directly to:
- encode all normativity as `DECISION` events
- record observations as non-interfering `PROOF` events
- guarantee digest stability under observational variation
- enable deterministic replay of normative state

## Relationship
1.  **KL defines what must not happen.**
2.  **DBL ensures violations cannot be hidden.**

This Domainrunner demonstrates what remains when both are applied.

- **KL constrains the design space.**
- **DBL constrains the execution space.**

The code is intentionally small because the guarantees live in the substrate, not in feature logic.