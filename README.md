# PostFiat Network Architecture and Agent Integration Reference

Public testnet observations (2026-11-13, 02:29–02:44 UTC) plus the complete
public agent work-request, submission, and verification surface of the Task
Node. Results page: `docs/index.html`.

## Headline numbers (measured, 2026-11-13)

| Metric | Value |
| --- | --- |
| Ledger close interval | mean **3.036 s**, median 3.000 s, range 2.727–3.333 s (21 samples / 600 s) |
| Ledger-height growth | **+198 ledgers in 600.0 s** (19.80/min); seq 8,001,214 → 8,001,412 |
| Validation quorum / UNL | **17 / 25** (68%); 66 validators total, 41 non-UNL |
| 24h validation agreement | **48 missed of 1,881,457** (0.00255%); 1h missed 0 |
| P2P topology | **71 nodes, 730 edges**, 17 countries; 3 Atlanta hubs carry ~19% of edges |
| Fee burn | **10 drops/ledger** (supply −60 drops in 31 s, directly observed) |
| Probed node | `rpc.testnet.postfiat.org`, postfiatd 1.0.9, network_id 2025, 21 peers, server_state full |
| Task Node API | **213 route policies, 8 auth modes**; mutations require a session (401 anonymous) |

## Layout

| Path | Contents |
| --- | --- |
| `docs/index.html` | Results page (summary, diagrams, findings) |
| `docs/citations.md` | Every primary source with fetch times |
| `docs/methodology.md` | How each number was obtained; limitations |
| `docs/topology-map.md` | Validator-topology map + tables (generated from live VHS data) |
| `docs/consensus-flow.md` | Live testnet consensus (measured) vs l1v2 design (specified) |
| `docs/agent-integration.md` | Public agent surface: endpoints, message shapes, runnable probes |
| `docs/findings-report.md` | 13 severity-scored findings + remediation (0 High, 3 Medium, 6 Low, 4 Info) |
| `docs/decision-memo.md` | Decisions, evidence, alternatives rejected, open questions |
| `docs/claim-evidence-index.md` | Every claim mapped to its evidence file |
| `configs/` | Pinned endpoints, Task Node API inventory, live-observation summary |
| `fixtures/` | Pinned source copies: VHS env/docs, Task Node API reference, l1v2 excerpts, whitepaper excerpts, pinned commits |
| `outputs/` | Unedited probe outputs (JSON-RPC, VHS, explorer, Task Node, WS, cadence) + `derived/` aggregates |
| `scripts/` | `run_all.sh`, `clean_reproduce.sh`, `compare_reproduce.py`, probes, analysis, failure-recovery demos |
| `src/topology.py` | Generates the topology map from the shipped VHS outputs |
| `findings.json` | Machine-readable findings |
| `run-manifest.json` | Run record: window, tools, counts, reproduction result |
| `SHA256SUMS` | Digests of every pack file (see `scripts/verify_digests.sh`) |

## Reproduce

```bash
./scripts/run_all.sh          # analysis + demos + live re-check + compare
./scripts/clean_reproduce.sh  # fresh-copy run; writes outputs/fresh-clone-*
python3 scripts/analyze.py    # recompute every headline number from outputs/
python3 scripts/failure_recovery_demo.py
./scripts/verify_digests.sh   # SHA256SUMS check
```

Live values drift (ledger height grows ~20 ledgers/min); the compare script
checks ranges and structural invariants for live values and exact equality
only for deterministic recomputations over the shipped files.

## The one distinction that matters

The **live testnet** runs `postfiatd` 1.0.9 (a rippled fork: XRPL-style
proposals + validations, quorum 17/25, ~3 s closes). The **l1v2 design**
(Consensus v2 prepare/precommit QCs + Cobalt trust ratification, ML-DSA-65)
is specified in the whitepaper and the `postfiatl1v2` repo — it is **not**
what the live testnet runs today. This pack keeps the two in separate
sections everywhere; conflating them would misstate both.

## Boundaries

- All observations are from **public, unauthenticated** endpoints. No
  session, account, wallet, credential, or private surface was used.
- Session/bearer Task Node routes are documented from the public route
  registry only and were not called.
- No Discord content anywhere in this pack.

## Privacy redaction (applied before publication)

The Task Node public-directory probe outputs (`outputs/tn-api-directory-*.json*`,
`outputs/tn-api-hive-projects.json.body`, `outputs/tn-api-system-status.json.body`)
originally embedded per-user records (internal account IDs, wallet addresses,
handles, display names) served by those public unauthenticated endpoints.
Those fields are redacted in the shipped files (`accountId` → `acct_REDACTED`,
`wallet`/`walletAddress` → `rREDACTED`, `handle`/`displayName` → `REDACTED`)
by `scripts/redact_operator_records.py`; record counts, totals, scores, task
titles, statuses, timestamps and all aggregate figures are unchanged.
Validator-topology addresses (VHS) and the public genesis account are public
ledger infrastructure and were not redacted. See `run-manifest.json`
(`redactions`) for the full record.
