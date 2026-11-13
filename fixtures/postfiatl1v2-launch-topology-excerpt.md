# Launch Topology and Independence Thresholds

**Status:** Proposal — awaiting the operator's thresholds
**Date:** 2026-09-01
**Author:** Domagoj Ravlic (dravlic)
**Decision owner:** Post Fiat
**Purpose:** D3 of the [testnet-path milestone](../plans/active/l1v2-public-testnet-path-milestone.md) — concrete numeric topology and independence thresholds for a public-testnet launch, reusing the fork's strict-gate machinery.
**Related:** the locked [testnet genesis and launch specification](l1v2-testnet-genesis-and-launch-spec.md) (§3.3 trust-graph arithmetic, §5 launch gates, §5.2 independence calculation), the [genesis-registry proposal path](genesis-registry-proposal-path.md), the [release-gate inventory](../status/release-gate-inventory.md) row 20, and the [public launch boundary](../security/public-launch-boundary.md)

This document decides nothing. Every number below is a proposal awaiting the
operator's confirmation; the operator may adopt, tighten, or replace any of
them. Fork rules are cited from the read-only clones `dynamic-unl-scoring`
and `validator-scoring-sidecar`.

## 1. Shared arithmetic

All thresholds are stated at the genesis specification's minimum registry
size and scale with it (§3.3, §5.1–5.2 of the launch specification):

```text
n_S ≥ 12                                  registry size (launch minimum)
q_S = ceil(4 * n_S / 5) = 10 at n_S = 12  ratification quorum
n_S - q_S = 2                             unavailability margin
n_S - q_S + 1 = 3                         blocking threshold (any 3 seats can stall)
t_S = min(3, 4, 7) = 3 at n_S = 12        tolerated-fault bound
```

A correlated group that reaches `q_S` can ratify alone; a group that reaches
`n_S - q_S + 1` can stall registry evolution. The caps below are set against
those two numbers.

## 2. Dimensions

### 2.1 Hosting provider / ASN concentration

- **Fork rule today:** no hard cap. Provider-family and country counts are
  precomputed (`dynamic-unl-scoring/scoring_service/services/provider_families.py`,
  `compute_concentration`) and injected into the scoring prompt as the sole
  concentration evidence (`dynamic-unl-scoring/prompts/scoring_v10.txt`,
  diversity rules); concentration only lowers the diversity sub-score, which
  carries weight 10 of 100 in the deterministic final score
  (`dynamic-unl-scoring/docs/DeterministicFinalScore.md`). A dominant provider
  is scored down, never excluded.
- **Proposed l1v2 launch threshold:** at most **2 of 12** registry seats per
  hosting-provider family (general form: family weight ≤ `n_S - q_S`), and
  the same **2-seat** cap per individual ASN, using the fork's family
  normalization so corporate variants of one operator count together.
- **Rationale:** a single provider-wide outage must leave at least `q_S`
  validators standing, so no family may reach the blocking threshold of 3.
- **Checked by:** built — `python/postfiat_rpc/placement_preflight.py`
  (tests `python/tests/test_placement_preflight.py`) enforces the family and
  ASN caps over declared fields using the fork's family normalization ported
  from `provider_families.py`, and fails closed on unresolved endpoints.
  Feeding it fork-side ASN resolution
  (`dynamic-unl-scoring/scoring_service/clients/asn.py`, public pyasn data)
  for real operators is community-facing work under gate L3.

### 2.2 Geographic concentration

- **Fork rule today:** no hard cap. Country counts come from DB-IP Lite
