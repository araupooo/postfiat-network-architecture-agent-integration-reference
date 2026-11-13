### 3.3 Template trust graph

`T0` assigns every validator the same template trust view: one essential subset `S = G0`, with `n_S = |G0|` and:

```text
q_S = ceil(4 * n_S / 5)
t_S = min(ceil(n_S / 5), floor((q_S - 1) / 2), 2*q_S - n_S - 1)
```

These are reviewed launch-profile parameters, not Consensus v2 constants.

The `4/5` quorum targets agreement by a large supermajority while retaining approximately one-fifth non-participation headroom before integer rounding. `t_S` takes the most conservative of:

1. the same one-fifth launch-fault budget;
2. the bound required by `2*t_S < q_S`; and
3. the bound required by `t_S < 2*q_S - n_S`.

The checker enforces those inequalities and Cobalt linkage independently of this profile. Changing the profile therefore requires a new reviewed payload but cannot bypass checker soundness.

Worked launch examples:

```text
n_S = 12:
q_S = ceil(48/5) = 10
t_S = min(ceil(12/5), floor(9/2), 20-12-1)
    = min(3, 4, 7) = 3
checks: 3 < 8 and 6 < 10

n_S = 20:
q_S = 16
t_S = min(4, 7, 11) = 4
checks: 4 < 12 and 8 < 16
```

Uniform views reduce launch complexity; they are not permanent. A heterogeneous view is valid only through a signed, versioned trust-view proposal included in frozen transition evidence. `χ_t` deterministically checks its syntax, linkage, local soundness, and old-new matrix. A free-form operator declaration cannot alter `T_t`.

### 3.4 Genesis ratification

Each `G0` operator’s ratification client independently:

1. fetches and verifies every pinned dependency and evidence digest;
2. replays the genesis round to the published selection;
3. computes `G0 = Selected ∩ Receipted`;
4. validates every receipt and uniqueness rule;
5. reconstructs `T0`;
6. runs the pinned `χ0` against `G0`, `T0`, and `π0`; and
7. recomputes `genesis_payload_hash`.

A ratifier signs:

```text
digest(
  "L1V2_GENESIS_RATIFICATION_SIGNATURE_V1",
  genesis_payload_hash
)
```

The detached certificate is valid only with signatures from at least `q_S` distinct members of `G0`. Signatures from unknown, duplicate, or non-member keys are rejected.

After finalization, genesis ratifiers have no override authority under [whitepaper](../whitepaper.md) §6. Changing the payload or certificate produces a different genesis envelope and therefore a fork, not an in-chain governance action.

### 4.4 Quorum degradation and permanent halt

Operators monitor the number of currently reachable ratification clients and publish an alert when it falls below:

```text
required reveal threshold + π_t.liveness_margin
```

The margin is a reviewed profile parameter; it does not alter quorum. Key rotations and evidence-driven removals should be proposed while the old registry can still ratify them.

If the active registry can no longer produce a valid transition certificate:

1. the current registry and trust graph remain unchanged;
2. no administrator, Foundation key, launch signer, or genesis ratifier may lower quorum or edit membership;
3. Consensus and transition clients expose the state `REGISTRY_EVOLUTION_HALTED`;
4. operators continue attempts only under the existing rules; and
5. if quorum loss is judged permanent, recovery is a coordinated successor testnet with a new chain ID and new genesis payload, not an in-chain transition.

A successor genesis must use a new named frozen round, the same deterministic construction and receipt rules, and a new L1–L6 evaluation. Its launch record identifies the halted predecessor and the evidence used to classify the halt. This is an explicit terminal-state procedure: it preserves fail-closed operation and does not represent the successor as having been validated by unavailable old rules.

