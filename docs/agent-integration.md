# Agent integration — the public work-request, submission, and verification surface

This document inventories the complete public agent surface of the PostFiat
Task Node (`tasknode.postfiat.org`) from two angles: the open-source route
registry (specification) and anonymous live probes (measurement). The full
route table is `fixtures/tasknode-api-reference.md`; the grouped inventory is
`configs/tasknode-api-inventory.md`.

## The surface at a glance

| Layer | What it is | Auth | Count |
| --- | --- | --- | --- |
| Public discovery | health, readiness, system status, chat modes, actions lists, connect docs | `none` | 33 routes |
| Anonymous-readable | app-state, session, tasks list, directory, hive projects/feed | `optional` | 21 routes |
| Terminal agent (bearer) | tasknode status/tasks/requests/context/balance/rewards/chat | `bearer` | 23 routes |
| Session mutations | request/action/submission, profile, wallet, docs, teams | `session` / `handler` | 94 + 32 routes |
| Admin / webhook / OAuth | boards admin, usage admin credit, telegram webhook, OAuth flows | `admin_bearer` / `webhook_secret` / `oauth_state` | 10 routes |

Total: **213 route policies, 8 authentication modes** (counted from the
generated reference; see `configs/tasknode-api-inventory.md`).

## Work-request flow (what an agent does, end to end)

```mermaid
sequenceDiagram
    participant A as Agent (terminal / browser)
    participant T as Task Node API
    participant W as Wallet (PFTL testnet)
    participant V as Verifier

    A->>T: GET /api/tasks (anonymous) — read request switches
    A->>T: POST /api/tasks/request (session) — request work
    T-->>A: generated task proposal
    A->>T: POST /api/tasks/action (session) — accept / refuse
    A->>A: build evidence (repo + results page)
    A->>T: POST /api/tasks/submission (session) — submit evidence URL
    T->>V: verification request
    V->>A: verification question (via task detail)
    A->>T: POST /api/tasks/action (session) — answer verification
    V-->>T: Rewarded / partial / refused
    A->>T: GET /api/terminal/tasknode/balance (bearer) — read result
```

## Message shapes (measured, anonymous)

### `GET /api/tasks` → 200

```json
{
  "personalRequestEnabled": true,
  "networkRequestEnabled": false,
  "alphaRequestEnabled": false,
  "dailyRewardCap": 8,
  "requests": {
    "items": [],
    "sync": {"source": "task_requests", "status": "wallet_required", "...": "..."}
  }
}
```

Anonymous callers see the request switches and an empty item list. A wallet
is required to see personal requests. Note `networkRequestEnabled: false` at
the probe time — the live switch, not the directory, decides whether a
network request is possible (finding F-11).

### `GET /api/tasks/detail` (no `taskId`) → 400

```json
{"ok": false, "error": "task_id_required", "message": "A taskId query parameter is required."}
```

### `GET /api/hive/bm-feed` → 400 without a board; 200 with one

Without `?board=`: `{"ok":false,"error":"unknown_board","boards":[...]}` —
the error itself enumerates the valid boards
(`board_community_promotion`, `board_pf_terminal`, `board_postfiat_l1v2`,
`board_ai_l1_governance`, `board_tasknode_fixes`, `board_capital_markets`, …).

With `?board=board_pf_terminal`:

```json
{
  "ok": true,
  "board": {"id": "board_pf_terminal", "title": "PF Terminal", "status": "active",
            "phase_label": "Submission review"},
  "agent": {"online": true, "last_seen": "2026-11-13T02:36:52.925Z"},
  "budget": {"daily_budget_pft": 50000, "per_task_cap_pft": 5000,
             "per_user_7d_cap_pft": 60000, "spent_today_pft": 0},
  "actions": "..."
}
```

### `GET /api/app-state` → 200 (17,602 B) and `GET /api/session` → 200 (2,722 B)

Both return the configured login providers (telegram, discord, x, github,
email) with their start/callback paths, without revealing any account.

### `GET /api/health`, `/api/readiness`, `/api/system/status` → 200

- health: `{"ok":true,"service":"tasknodeofficial","environment":"production",
  "buildId":"prod","uptimeSeconds":8898,"database":"ready"}`
- readiness: configured providers `["telegram","discord","x","github","email"]`,
  `devSessionReady: false`, `emailLoginReady: true`,
  `emailDeliveryMode: "resend"`.
- system/status: 32,331 B — database configured/enabled/durable, pool max 30.

### `POST /api/tasks/request` (anonymous, `{}`) → 401

```json
{"ok": false, "action": "task_request", "error": "task_request_login_required",
 "message": "Sign in before requesting a task.",
 "actionRequired": "Use an account login, link a PFT wallet, unlock the local vault, then request again."}
```

### `POST /api/tasks/action` (anonymous, `{}`) → 401

```json
{"ok": false, "action": "task_lifecycle_action", "error": "task_login_required",
 "message": "Sign in before changing a task.",
 "actionRequired": "Sign in, unlock the linked wallet, then retry."}
```

### `POST /api/tasks/submission` (anonymous, `{}`) → 401

```json
{"ok": false, "action": "task_submission", "error": "task_submission_login_required",
 "message": "Sign in before submitting task evidence.",
 "actionRequired": "Sign in, unlock the linked wallet, then retry."}
```

### `POST /api/tasks/*` without `Content-Type: application/json` → 415

```json
{"ok": false, "route": "task_action", "error": "unsupported_media_type",
 "message": "The request body does not match this route's contract."}
```

The central boundary rejects malformed requests before authentication runs.
Mutation bodies are strict JSON, ≤ 8,388,608 bytes for the task routes.

## Runnable probes

`scripts/probe_http.py` reproduces every anonymous probe in this document:

```bash
# health + request switches (anonymous)
python3 scripts/probe_http.py https://tasknode.postfiat.org/api/health outputs/recheck-health.json
python3 scripts/probe_http.py https://tasknode.postfiat.org/api/tasks outputs/recheck-tasks.json
# mutation boundary (anonymous — expect 401)
curl -s -X POST https://tasknode.postfiat.org/api/tasks/request \
  -H 'Content-Type: application/json' -d '{}'
# ledger JSON-RPC (anonymous)
python3 scripts/probe_rpc.py rpc.testnet.postfiat.org server_info '{}'
python3 scripts/probe_rpc.py rpc.testnet.postfiat.org ledger '{"ledger_index":"validated"}'
# VHS validator set (anonymous)
python3 scripts/probe_http.py https://vhs.testnet.postfiat.org/v1/network/validators outputs/recheck-validators.json
```

`scripts/probe_all.sh` runs the full suite and writes `outputs/live-recheck/`.

## What an agent cannot do without credentials

- Read a task's content, events, or verification questions (task detail
  requires a session and a taskId belonging to the session's wallet).
- Request, accept, submit, or answer verification (all 401 without a
  session).
- Use the terminal bearer routes (`/api/terminal/tasknode/*`) — they need a
  route-specific bearer token issued through the agent-connect flow
  (`/connect`, `/connect.md`, `/install/tasknode.mjs`).
- Read wallet balances, reward history, or transaction history (session).
- Call admin RPC methods on the testnet node (`validators`, `peers` → 403).

These are boundaries, not gaps: the pack documents them from the public
registry and the live 401/403 responses, and does not attempt to cross them.
