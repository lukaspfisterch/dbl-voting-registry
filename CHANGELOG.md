# Changelog

## [v0.1.1] - 2025-12-28

### DBL Compliance Refactor
- **Changed**: `ELIGIBILITY_CHECKED` moved to `PROOF` (Observational).
- **Added**: `VOTER_ADMITTED` is the explicit `DECISION` event for authorization.
- **Verified**: Tests prove non-interference (observational data changes do not affect normative digests).
