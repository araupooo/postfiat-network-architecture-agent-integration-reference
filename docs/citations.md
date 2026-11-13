# Citations — primary sources

Every measured claim in this pack links to an unedited output in `outputs/`.
Every specification-derived claim cites one of the sources below. Fetch times
are UTC on 2026-11-13 unless stated otherwise. No source was accessed with a
credential, session, or account.

## Live public endpoints (measured)

| # | Source | What it establishes | Fetched | Output |
| --- | --- | --- | --- | --- |
| L1 | `POST https://rpc.testnet.postfiat.org/` (`server_info`) | postfiatd 1.0.9, network_id 2025, 21 peers, quorum 17, proposers 25, validated seq 8,001,180, complete ledgers 7,950,054–8,001,180 | 02:32:48 | `outputs/rpc-server_info` (in cadence + probe files; first snapshot in the run log) |
| L2 | `POST https://rpc.testnet.postfiat.org/` (`ledger`, `ledger_closed`, `ledger_data`, `fee`, `account_info`) | Ledger headers, close times, total-coins burn, fee levels, queue state; XRPL genesis account not found on this network | 02:34:00–02:34:31 | `outputs/rpc-ledger.json`, `rpc-ledger_closed.json`, `rpc-ledger_data.json`, `rpc-fee.json`, `rpc-account_info-genesis.json` |
| L3 | `POST https://rpc.testnet.postfiat.org/` (`validators`, `peers`) | Admin methods blocked at the public proxy: HTTP 403 `Forbidden` | 02:34:15–02:34:16 | `outputs/rpc-validators.json`, `rpc-peers.json` |
| L4 | `POST https://rpc.testnet.postfiat.org/` (`no_such_method`) | Unknown method returns HTTP 200 with `unknownCmd` (error_code 32) | 02:41:43 | `outputs/rpc-invalid-method.json` |
| L5 | `wss://rpc.testnet.postfiat.org` (443 and :6005) | WebSocket subscribe fails: close 1006, 0 ledger closes; upgrade returns HTTP 401 | 02:34:42–02:37:12 | `outputs/ws-ledger-443.jsonl`, `outputs/ws-ledger-6005.jsonl` |
| L6 | `wss://s.altnet.rippletest.net:51233` (control) | Same client, same VM, receives ledger closes from the XRPL public testnet — the failure in L5 is endpoint-specific, not client-side | 02:37:45–02:38:00 | `outputs/ws-control-xrpl.jsonl` |
| L7 | `https://vhs.testnet.postfiat.org/v1/network/validators` | 66 validators, 25 UNL, agreement scores, domains, versions | 02:36 | `outputs/vhs-testnet-v1-network-validators.json` (+ `.body`) |
| L8 | `https://vhs.testnet.postfiat.org/v1/network/topology/nodes` | 71 topology nodes, geo, versions, inbound/outbound counts | 02:36 | `outputs/vhs-testnet-v1-network-topology-nodes.json` (+ `.body`) |
| L9 | `https://vhs.testnet.postfiat.org/v1/network/topology` | `node_count: 71`, `link_count: 0` (inconsistent with L8's per-node sums) | 02:36 | `outputs/vhs-testnet-v1-network-topology.json` (+ `.body`) |
| L10 | `https://vhs.testnet.postfiat.org/v1/network/networks` | 3 networks recorded (test + 2 webhook.site entries) | 02:42 | `outputs/vhs-testnet-v1-network-networks.json` (+ `.body`) |
| L11 | `https://vhs.testnet.postfiat.org/v1/health`, `/v1/validators` | Health `{"count":"12"}`; `/v1/validators` returns the API index | 02:36 | `outputs/vhs-testnet-v1-health.json`, `outputs/vhs-testnet-v1-validators.json` |
| L12 | `https://explorer.testnet.postfiat.org/api/v1/metrics` (×2) | base_fee 0.00001, txn_sec 0.09, ledger_interval 3.022 — identical across two fetches ~10 min apart | 02:29, 02:42 | `outputs/explorer-testnet-metrics-1.json`, `outputs/explorer-testnet-metrics-2.json` |
| L13 | `https://explorer.testnet.postfiat.org/api/v1/health` | `{"message":"rippled unreachable"}` while metrics works | 02:29 | `outputs/explorer-testnet-health.json` |
| L14 | `https://tasknode.postfiat.org/api/*` (anonymous GETs) | health/readiness/system-status/app-state/session/tasks/providers/chat-modes/leaderboard/rewarded-tasks/hive-projects/bm-feed/wallet-actions/context-actions/usage-actions/connect.md | 02:35–02:42 | `outputs/tn-*.json` |
| L15 | `POST https://tasknode.postfiat.org/api/tasks/{action,request,submission}` (anonymous, `{}`) | 401 login-required errors with exact messages | 02:42 | `outputs/tn-post-*.noauth.txt` |
| L16 | Cadence run: `server_info` polled every 30 s × 21 samples | 198 ledgers in 600.0 s; close interval mean 3.036 s, median 3.000 s | 02:34:32–02:44:32 | `outputs/cadence-run1.jsonl`, `outputs/cadence-run1.log` |

## Public repositories (pinned clones, shallow, 2026-11-13)

| # | Source | Commit | What it establishes |
| --- | --- | --- | --- |
| R1 | `github.com/postfiatorg/validator-history-service` | `d301c4ce78e109f1771d4429e17876a97e2654f3` | Testnet/mainnet/devnet RPC endpoints, NETWORK_ID, amendment majority time (3 d) and threshold (0.67); VHS API routes (`docs/DEPLOYMENT.md`, `docs/MIGRATIONS.md`) |
| R2 | `github.com/postfiatorg/tasknode` | `14e4914c5511305439e928b75d476c8b80ce7050` | 213-route HTTP API inventory with auth modes (`docs/api-reference.md`, fixture copy) |
| R3 | `github.com/postfiatorg/explorer` | `74161a20f200b6ad093e9d6d884fc4c370acb93c` | Explorer server routes (`/api/v1/metrics`, `/api/v1/health`); rippled WS connection model |
| R4 | `github.com/postfiatorg/postfiatl1v2` | `ccf960139a49652c84b1e2c2e90b5405fe0b1d8d` | L1v2 design: Cobalt trust graph, Consensus v2 finality, transaction lifecycle, launch topology thresholds (all *proposals/design*, not live testnet behavior) |

## Published pages

| # | Source | Crawled | What it establishes |
| --- | --- | --- | --- |
| P1 | `https://postfiat.org/` | 02:29 | 53 validators, 3,000+ community members; validator snapshot Sep 21 2026: 53 validators, 39 verified domains, 52 with 24h agreement 99.9%+, 6.5M ledger index |
| P2 | `https://postfiat.org/whitepaper/` | 02:30 | XRP-category chain; Cobalt ratification; ML-DSA from genesis; six-validator devnet (t_S=1, q_S=5); "one organization administers the current validator fleet"; independently operated validators still a proposal; August 2026 campaign; height-924 rotation |
| P3 | `https://docs.postfiat.org` | 02:41 (curl, HTTP 200, 22,512 B) | Notion-hosted docs site exists and is reachable; linked from the VHS docs as the documentation home |

## What was NOT used

- No signed-in session, account, wallet, credential, or private surface was
  used for any observation. Session/bearer Task Node routes are documented
  from the public source registry (R2) only and were not called.
- The live testnet runs `postfiatd` (a rippled fork). The `postfiatl1v2`
  repository (R4) describes a *different, future* protocol (Consensus v2,
  Cobalt ratification as protocol state). This pack keeps the two apart: live
  measurements are labeled **measured (live testnet)**; R4 claims are labeled
  **specified (l1v2 design)**.
