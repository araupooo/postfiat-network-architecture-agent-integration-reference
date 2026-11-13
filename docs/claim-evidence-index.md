# Claim-to-evidence index

Each claim states its kind: **measured** (live public query in the observation
window 2026-11-13 02:29–02:44 UTC) or **specified** (primary source, not a
live measurement). "Reproduce" tells a reviewer how to re-check it.

## Measured claims (live testnet)

| # | Claim | Evidence | Reproduce |
| --- | --- | --- | --- |
| M1 | Testnet network_id is 2025; node software is postfiatd 1.0.9 | `outputs/rpc-ledger.json` (network_id in server_info), first `server_info` snapshot 02:32:48 UTC | `python3 scripts/probe_rpc.py rpc.testnet.postfiat.org server_info '{}'` |
| M2 | Validated ledger grew 8,001,214 → 8,001,412 in 600.0 s (198 ledgers, 19.80/min) | `outputs/cadence-run1.jsonl`, `derived/cadence.json` | `python3 scripts/analyze.py` |
| M3 | Mean close interval 3.036 s, median 3.000 s, range 2.727–3.333 s | same | same |
| M4 | Validation quorum is 17, proposers 25, peers 21 — constant across all 21 samples | same | same |
| M5 | Converge time ≈ 2.0 s (2.000–2.010) in every sample | same | same |
| M6 | Base fee 10 drops, median fee 5,000 drops, queue 0/2000 | `outputs/rpc-fee.json`, `derived/ledger.json` | probe_rpc `fee` |
| M7 | Total supply fell 60 drops in 31 s (fee burn, 10 drops/ledger) | `outputs/rpc-ledger.json` vs `rpc-ledger_data.json`, `derived/ledger.json` | probe_rpc `ledger` + `ledger_data` |
| M8 | 66 validators, 25 UNL (37.9%), 41 non-UNL; 0 revoked, 0 partial | `outputs/vhs-testnet-v1-network-validators.json.body`, `derived/vhs.json` | `python3 scripts/analyze.py` |
| M9 | 24h agreement: 48 missed of 1,881,457 (0.00255%); 1h missed 0; 62/66 perfect 24h | same | same |
| M10 | All 25 UNL members run 1.0.9 and have domains; 12 non-UNL validators run older versions | same | same |
| M11 | 57/66 validators have domains, 55 verified; 3 `postfiat.org` validators, all non-UNL | same | same |
| M12 | 71 topology nodes, 730 inbound = 730 outbound edges; 3 Atlanta hubs (46–47 inbound each); 13 nodes with 0 inbound | `outputs/vhs-testnet-v1-network-topology-nodes.json.body`, `derived/vhs.json`, `derived/topology.md` | same |
| M13 | Nodes span 17 countries; top US 17, PH 11, DE 10 | same | same |
| M14 | Probed node `n9K4AomB…` is at 192.248.151.4, Canary Wharf, inbound 11 / outbound 10 | `outputs/vhs-testnet-v1-network-topology-nodes.json.body` + `server_info` | cross-check the two files |
| M15 | No divergent ledger hash at any sampled index (1 hash per index: 8,001,283 and 8,001,284) | `derived/vhs.json` (`distinct_hashes_per_index`), demo 4 in `scripts/failure_recovery_demo.py` | `python3 scripts/failure_recovery_demo.py` |
| M16 | Public WS ledger stream fails (401 on 443, close 1006 on :6005, 0 closes); same client works against XRPL public testnet WS | `outputs/ws-ledger-443.jsonl`, `ws-ledger-6005.jsonl`, `ws-control-xrpl.jsonl` | `node scripts/ws_subscribe.mjs wss://rpc.testnet.postfiat.org 30 <out>` |
| M17 | Admin RPC methods `validators`/`peers` return HTTP 403 | `outputs/rpc-validators.json`, `rpc-peers.json` | probe_rpc `validators` / `peers` |
| M18 | Unknown RPC method returns `unknownCmd` (error_code 32) over HTTP 200 | `outputs/rpc-invalid-method.json` | probe_rpc `no_such_method` |
| M19 | Explorer `/api/v1/health` returns `{"message":"rippled unreachable"}` while `/api/v1/metrics` works | `outputs/explorer-testnet-health.json`, `explorer-testnet-metrics-1.json` | probe_http on both paths |
| M20 | Explorer metrics byte-identical across two fetches ~10 min apart | `outputs/explorer-testnet-metrics-1.json` vs `-2.json` | diff the two files |
| M21 | Task Node anonymous `GET /api/tasks`: personalRequestEnabled true, networkRequestEnabled false, alphaRequestEnabled false, dailyRewardCap 8 | `outputs/tn-api-tasks.json` | probe_http `https://tasknode.postfiat.org/api/tasks` |
| M22 | Task Node mutations without a session return 401 (`task_login_required`, `task_request_login_required`, `task_submission_login_required`); without `Content-Type: application/json` return 415 | `outputs/tn-post-*.noauth.txt`, `outputs/tn-post-tasks-*.json` | curl POST `{}` to `/api/tasks/request` |
| M23 | Task Node has 213 route policies across 8 auth modes (session 94, none 33, handler 32, bearer 23, optional 21, admin_bearer 5, oauth_state 4, webhook_secret 1) | `fixtures/tasknode-api-reference.md`, `configs/tasknode-api-inventory.md` | count rows in the fixture |
| M24 | Hive board `board_pf_terminal` is active with daily budget 50,000 PFT, per-task cap 5,000 PFT, spent today 0 | `outputs/tn-api-hive-bm-feed-board.json` | probe_http with `?board=board_pf_terminal` |
| M25 | Ledger retention on the probed node: `complete_ledgers` 7,950,054–8,001,412 (~51,359 ledgers) | `outputs/cadence-run1.jsonl` | read first/last `complete_ledgers` |

## Specified claims (primary sources, not live measurements)

| # | Claim | Source |
| --- | --- | --- |
| S1 | The chain inherits the XRP category: known validators, deterministic finality, fixed-supply native asset, fee burn, no validator subsidy | Whitepaper §1 (fixture `whitepaper-excerpts.md`) |
| S2 | Validator-trust changes become protocol state ratified by Cobalt; accounts and validators sign with ML-DSA from genesis | Whitepaper §1 |
| S3 | The current fleet is six Foundation-administered validators with separate keys and "establishes no independent control"; independently operated validators remain a proposal | Whitepaper §1.8 |
| S4 | Devnet trust graph is one six-validator subset, t_S=1, q_S=5 (five-of-six ratifies) | Whitepaper §1.8; genesis spec §3.3 |
| S5 | Consensus v2: f = floor((n-1)/3), q = floor(2n/3)+1; q prepare votes form the lock, q precommit votes form the only commit QC | Whitepaper §1.8; fixture `postfiatl1v2-finality.md` |
| S6 | Cobalt subsets must satisfy t_S < 2q_S − n_S and 2t_S < q_S | Whitepaper §1.8; genesis spec §3.3 |
| S7 | August 2026 campaign path: admission → selector → Cobalt (RBC→ABBA→MVBA→DABC) → ML-DSA-65 authorizations (≥ q) → Consensus v2 orders update → execution applies; height-924 rotation of validator 5 committed | Whitepaper §1.8 |
| S8 | Genesis launch profile: q_S = ceil(4·n_S/5); quorum loss halts registry evolution (`REGISTRY_EVOLUTION_HALTED`), recovery is a successor testnet | Genesis spec §3.3, §4.4 (fixture `postfiatl1v2-genesis-spec-excerpt.md`) |
| S9 | Launch topology proposal: ≤2 of 12 seats per hosting-provider family, ≤4 of 12 per country (≥4 countries); all numbers are proposals awaiting the operator | Launch-topology doc (fixture `postfiatl1v2-launch-topology-excerpt.md`) |
| S10 | Testnet endpoints: `rpc.testnet.postfiat.org:5006`, `wss://rpc.testnet.postfiat.org`, NETWORK_ID `test`, amendment majority 3 days / 0.67 | VHS `.env.testnet` (fixture `vhs-env-testnet.txt`), `fixtures/vhs-postfiat.md` |
| S11 | The cross-phase current-view fence is a proposed normative rule; its enforcement in the current runtime is unestablished; no exploit is claimed | Whitepaper §1.8 ("The consensus obligation, stated exactly") |
| S12 | A committed block may contain a rejected transaction; wallets must check the receipt code, not just block finality | Fixture `postfiatl1v2-finality.md` ("Client finality") |

## Claims this pack does NOT make

- It does not claim the l1v2 Consensus v2 / Cobalt stack is running anywhere
  (it is specified, not live).
- It does not claim the UNL is independently operated (domain diversity is
  not proof of independent control).
- It does not claim the full parent-hash chain was verified (headers 11
  ledgers apart; see methodology limitation 4).
- It does not claim anything about authenticated Task Node behavior (no
  session was used).
