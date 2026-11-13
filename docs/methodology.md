# Methodology

## Observation window

All live observations were made on 2026-11-13, 02:29–02:44 UTC (09:29–09:44 WIB),
from a single Linux VM (4 CPUs, Python 3.12.3, Node 24.22.1, OpenSSL 3.0.13,
curl, git). Every probe records its own fetch timestamp inside its output
file; the numbers in this pack are a snapshot of that window, not standing
values.

## Tools (all in `scripts/`)

| Tool | Purpose |
| --- | --- |
| `probe_rpc.py` | POST one JSON-RPC method to `https://rpc.testnet.postfiat.org/`; records HTTP status, RTT, fetch time, raw body length, parsed response |
| `probe_http.py` | Anonymous GET/POST of a public URL; records status, RTT, content type, body bytes, first 600 bytes, and saves the full body alongside |
| `ws_subscribe.mjs` | Node 24 built-in WebSocket client; subscribes to the `ledger` stream, logs every event with timestamps |
| `cadence_sample.py` | Polls `server_info` every N seconds for M samples; logs validated seq, age, peers, proposers, quorum, converge time |
| `analyze.py` | Recomputes every headline number from the shipped `outputs/` files into `outputs/derived/*.json` (deterministic) |
| `failure_recovery_demo.py` | Runs the four failure-recovery demos against shipped outputs (real) + labeled synthetic cases |
| `topology.py` (in `src/`) | Builds the Mermaid topology map and tables from the shipped VHS outputs (deterministic) |
| `probe_all.sh` | Re-runs the full live observation suite (see `run_all.sh`) |

## How each headline number was obtained

- **Ledger cadence**: 21 `server_info` samples at 30 s intervals (600.0 s span).
  Close interval per gap = elapsed wall time / ledgers closed in that gap.
  Mean 3.036 s, median 3.000 s, min 2.727 s, max 3.333 s. Per-sample gaps:
  10 ledgers (×16), 9 (×3), 11 (×1). The 30 s poll cadence means the
  interval is an average over ~10 ledgers per sample, not a per-ledger
  measurement; the explorer's `ledger_interval` 3.022 s agrees with it.
- **Ledger-height growth**: validated seq 8,001,214 → 8,001,412 = +198 ledgers
  in 600.0 s = 19.80 ledgers/min.
- **Fee burn**: `total_coins` 99,999,999,967,500,634 → 99,999,999,967,500,574
  drops over 31.0 s (60 drops) between two ledger headers 11 ledgers apart —
  consistent with the 10-drop base fee per ledger (6 ledgers × 10 drops in
  that window, within the headers' close times).
- **Validator set**: one `GET /v1/network/validators` (51,357 B, 66 records)
  and one `GET /v1/network/topology/nodes` (32,940 B, 71 records) from the VHS
  API. All aggregates in `derived/vhs.json` are computed from those two files
  by `analyze.py`; re-running it reproduces them exactly.
- **Peer counts**: the probed node's `peers: 21` is constant across all 21
  cadence samples; the 71-node figure is the VHS crawler's view. These are
  different measurements (one node's peer table vs the crawler's node
  registry) and are never added together.
- **Task Node API**: route inventory from the generated `docs/api-reference.md`
  in the public tasknode repo (213 policies, counted by `analyze.py`-style
  parse in the build notes); live probes are anonymous GETs of `none`/`optional`
  routes plus anonymous POSTs that document the 401/415 boundary. No
  session or bearer route was called.

## What "unedited output" means

Probe scripts write the server's response verbatim (parsed JSON re-serialized
with indentation, plus a `.body` file holding the exact bytes for HTTP probes).
No response was hand-edited. The only transformations are the derived
aggregates in `outputs/derived/`, which are recomputed from the shipped files
by `scripts/analyze.py` and `src/topology.py`.

## Drift tolerance

Live values move: ledger height grows ~20 ledgers/min, validator agreement
changes with every validation, and the VHS counts change as validators join
or leave. `scripts/compare_reproduce.py` therefore checks **structural
invariants and ranges** for live re-checks (network_id == 2025, quorum == 17,
ledger seq strictly greater than the shipped seq, validator count within ±10
of 66, base fee == 10 drops) and **exact equality** only for deterministic
recomputations over the shipped files (cadence aggregates, VHS aggregates,
demo results).

## Limitations

1. **Single observation window.** 15 minutes of polling. Cadence and agreement
   figures are a snapshot; a longer window would tighten the interval
   distribution but would not change the architecture.
2. **Single vantage point.** All testnet queries hit one public RPC node
   (`rpc.testnet.postfiat.org`, node `n9K4AomB…`, Canary Wharf). Peer counts,
   RTT, and `complete_ledgers` are that node's view. The VHS API gives the
   network-wide view and is cited wherever a network-wide claim is made.
3. **No WebSocket stream.** The public WS endpoint requires authorization
   (401), so no live ledger-close stream was captured from PostFiat itself.
   Cadence is therefore derived from polling, not from a push stream. The
   control (XRPL public testnet WS, same client, same VM) proves the client
   works.
4. **No consecutive headers.** The pack holds ledger headers 8,001,203 and
   8,001,214 (11 apart), so the parent-hash chain is not fully verified here;
   time ordering and per-index hash uniqueness are checked instead.
5. **No authenticated surface.** Everything behind a session or bearer token
   (task detail with content, evidence submission, wallet, rewards) is
   documented from the public route registry only. Nothing in this pack
   proves what an authenticated call returns.
6. **L1v2 is design, not live.** The `postfiatl1v2` repository describes the
   future L1. Its consensus (prepare/precommit QCs, Cobalt ratification as
   protocol state) is **not** what the live testnet runs today (postfiatd,
   XRPL-style proposals + validations). The pack labels the two explicitly.
7. **Explorer metrics are cached.** The explorer's `/api/v1/metrics` returned
   byte-identical values ~10 minutes apart; do not treat them as live.
8. **VHS `/v1/network/networks` lists two `webhook.site` entries** (networks
   `1` and `2`) that look like test/dev artifacts in the VHS database; they
   are reported as returned, not interpreted.
