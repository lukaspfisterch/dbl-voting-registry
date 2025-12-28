# dbl-voting-registry

[![tests](https://github.com/lukaspfisterch/dbl-voting-registry/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/lukaspfisterch/dbl-voting-registry/actions/workflows/tests.yml)

## What this is
A minimal reference Domainrunner that demonstrates DBL-compliant deterministic voting over an append-only event log.

## DBL invariants demonstrated
- **Normativity is expressed exclusively via DECISION events.**
- **Observational events (PROOF) are non-interfering**: changing observational payload does not change digests.
- **Ingress is mandatory**: all external inputs are admitted and frozen before any decision is made.

Example (observational payload only):
```json
{
  "event_kind": "PROOF",
  "data": {
    "type": "ELIGIBILITY_CHECKED",
    "user_id": "Alice"
  },
  "observational": {
    "proof_details": {
      "meta": { "timestamp": "12:00", "ip": "1.1.1.1" }
    }
  }
}
```

- **Replay determinism**: with deterministic identifiers, identical inputs produce identical event sequences and identical log digests.

## Proof (tests)
```bash
python -m pytest -q
```

Key tests:
- `tests/test_auditability.py`
- `tests/test_determinism.py`


## Mini-Walkthrough
- **Events** (`events.py`): All normative changes are `DECISION` events. All checks are `PROOF` events.
- **Ingress** (`dbl_ingress.shape_input`): All external input is validated and frozen before use.
- **Lifecycle** (`registry.py`): `check_eligibility()` emits a `PROOF` (what was observed) and, if valid, a `DECISION` (`VOTER_ADMITTED`).
- **Projection**: In-memory state (for validation only) is derived exclusively from `DECISION` events.

## Demo (Audit View)
Running `python demo.py` exposes the strict separation of `PROOF` vs `DECISION`.

```text
[Audit View]
IDX  KIND       TYPE
--------------------------------------------------------------------------------
0    DECISION   PROPOSAL_SUBMITTED
1    PROOF      ELIGIBILITY_CHECKED
2    DECISION   VOTER_ADMITTED
...
```

**Canonical Projection (Digests)**
```text
0: 754869d0de2c1ed6086e313a4d3beae2554c8c5457ad1899a9d3c8196c0d65fc
1: ad02a23c5b600a0edd0806c3428be6a7773976b86911d0db40b86c60bed90e99
2: e5feb936fcadbfe43c358e81cddb023d4ac4bd95be5ab65c52722d17b5ca9275
...
```

**Invariance Check (Live Proof)**
```text
Proof 1 Digest (t=12:00): 20fc612dd1837e73c27b552654f48cd2be8f50565a304eaa567c4820d46c72be
Proof 2 Digest (t=12:01): 20fc612dd1837e73c27b552654f48cd2be8f50565a304eaa567c4820d46c72be
Match? True
```

## Project Layout
- `src/dbl_voting_registry/`: Domain logic and event definitions
- `tests/`: Verification of invariants (auditability, determinism)
- `demo.py`: End-to-end execution example

## Why ingress is separate
Ingress (dbl-ingress) is the mandatory boundary gate. It performs strict validation and freezing only.
Domain logic consumes AdmissionRecord data and must not accept raw input dictionaries directly.

> Non-goal: This project does not address policy quality, correctness, or distributed consensus. It demonstrates structural determinism and auditability only.

---

If you want the full DBL model and repository map, see:
https://github.com/lukaspfisterch/deterministic-boundary-layer

