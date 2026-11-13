# Decision memo — PostFiat network architecture and agent integration

## Decision

**Adopt the public-surface architecture documented in this pack as the
reference for agent integration work, with the boundaries stated below.**
Specifically: (1) treat the VHS API as the canonical public source for the
validator set and topology; (2) treat the Task Node `/api/tasks` live switch
as the authority on request eligibility; (3) use HTTP polling, not WebSocket,
for ledger tracking on the public testnet; (4) keep the live testnet
(postfiatd, XRPL-style consensus) and the l1v2 design (Consensus v2 +
Cobalt) in separate sections of any future documentation.

## Evidence for each decision

### 1. VHS API as the canonical public validator source

- The public RPC node blocks the admin methods that enumerate validators
  (`validators`, `peers` → HTTP 403; `outputs/rpc-validators.json`).
- The VHS API returns the full validator set (66 records with agreement,
  domains, versions) and the topology (71 nodes with geo and peer counts) in
  single anonymous GETs (`outputs/vhs-testnet-v1-network-validators.json`,
  `outputs/vhs-testnet-v1-network-topology-nodes.json`).
- The VHS service is itself the project's own fork of Ripple's validator
  history service, documented in its public repo
  (`fixtures/vhs-postfiat.md`, repo commit `d301c4ce`).
- Alternative considered: crawling peer lists from individual nodes. Rejected
  — a single node's peer table (21 peers) covers only ~30% of the network
  (finding F-13), and no public node exposes the full peer graph.

### 2. `/api/tasks` live switch as the authority on request eligibility

- Anonymous `GET /api/tasks` returns `personalRequestEnabled: true`,
  `networkRequestEnabled: false`, `alphaRequestEnabled: false`,
  `dailyRewardCap: 8` (`outputs/tn-api-tasks.json`).
- The network-task directory still serves entries while the switch is off
  (finding F-11), so the directory alone misleads.
- The route registry (fixture `tasknode-api-reference.md`, 213 policies)
  marks `/api/tasks` as `optional` auth — readable anonymously by design.

### 3. HTTP polling, not WebSocket, for ledger tracking

- The public WS endpoint requires authorization (401 on upgrade; close 1006
  on :6005) with 0 ledger closes received on either port
  (`outputs/ws-ledger-443.jsonl`, `outputs/ws-ledger-6005.jsonl`).
- The control proves the client works (XRPL public testnet WS delivered
  ledger closes from the same VM: `outputs/ws-control-xrpl.jsonl`).
- Polling `server_info` every 30 s produced 21/21 successful samples with
  a mean RTT of 0.927 s and a monotonic validated sequence
  (`outputs/cadence-run1.jsonl`). At a ~3 s close cadence, 30 s polling
  tracks the validated height reliably; 3–5 s polling would be needed to
  track individual closes.
- The failure-recovery demo (`scripts/failure_recovery_demo.py`, demo 1)
  encodes the fallback: on WS close/error, poll `server_info`, compare
  `validated_seq` with the last known seq, and resume from the new validated
  ledger.

### 4. Separate the live testnet from the l1v2 design

- Live: postfiatd 1.0.9, network_id 2025, XRPL-style proposals/validations,
  quorum 17/25, ~3.036 s closes (measured).
- Design: Consensus v2 prepare/precommit QCs (`q = floor(2n/3)+1`), Cobalt
  trust-graph ratification, ML-DSA-65 signing — specified in the whitepaper
  and `postfiatl1v2` docs, with an explicitly open obligation (the
  cross-phase current-view fence is proposed, enforcement unestablished).
- Conflating them would misstate both the live network's safety argument
  (quorum intersection over 25 UNL validators, not prepare/precommit QCs)
  and the design's status (specified, not deployed). See
  `docs/consensus-flow.md`.

## Alternatives considered and rejected

| Alternative | Why rejected |
| --- | --- |
| Use the explorer's `/api/v1/metrics` as the live cadence source | Values are byte-identical across fetches ~10 min apart — cached, not live (F-03) |
| Use the explorer's `/api/v1/health` as the liveness signal | Reports "rippled unreachable" while the service works (F-02) |
| Enumerate the UNL from the RPC node | Admin methods return 403 on the public proxy (F-04) |
| Subscribe to the ledger stream over WS | Requires authorization (401) (F-01) |
| Claim "independently operated validators" from domain diversity | Domain diversity does not prove independent control; the whitepaper says independent operation remains a proposal (F-08) |
| Verify the full parent-hash chain | The pack holds headers 11 ledgers apart; only time ordering + per-index hash uniqueness are checkable (methodology limitation 4) |

## Risks and open questions

1. **Single-window snapshot.** All measurements are from a 15-minute window
   on 2026-11-13. Cadence, agreement, and counts will drift; the compare
   script tolerates drift by range, not by exact value.
2. **VHS as a single point of trust.** The validator set and topology both
   come from one service. Cross-checks performed: the probed node's key,
   IP, geo, and uptime agree between `server_info` and the VHS topology;
   the quorum (17) agrees with the 0.67 threshold in the VHS config; the
   close interval agrees with the explorer's (cached) `ledger_interval`.
3. **The l1v2 fence obligation.** The whitepaper's open consensus obligation
   (cross-phase current-view fence) is unresolved in the cited sources. Any
   future claim that Consensus v2 is safe must address it, not assume it.
4. **Operator independence is unproven.** The UNL's 25 distinct domains are
   consistent with, but do not prove, independent operation. The
   launch-topology proposal's control-group and ASN checks are the right
   next step; they need operator-declared evidence that is not public today.

## Recommendation

Ship this pack as the reference. Re-run `scripts/run_all.sh` before citing
any number older than a day — the numbers move, the architecture does not.
