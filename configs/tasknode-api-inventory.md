# Task Node HTTP API inventory (from the open-source route registry)

Source: `fixtures/tasknode-api-reference.md` — generated from the route-policy
registry in the public `postfiatorg/tasknode` repo (HEAD 14e4914c, cloned
2026-11-13). The full 213-row table is the fixture; this file groups it and
records which routes were probed live (anonymous, no credentials) on
2026-11-13 02:35–02:42 UTC. Full probe outputs: `outputs/tn-*.json`.

## Route policies by authentication mode (213 total)

| Auth mode | Routes | Meaning |
| --- | --- | --- |
| `session` | 94 | Valid Task Node browser session required |
| `none` | 33 | Public route; no caller identity |
| `handler` | 32 | Route handler enforces its own session/wallet policy |
| `bearer` | 23 | Route-specific bearer token required |
| `optional` | 21 | Session used when present; anonymous access allowed |
| `admin_bearer` | 5 | Configured administrative bearer token required |
| `oauth_state` | 4 | Single-use, provider-bound OAuth state required |
| `webhook_secret` | 1 | Configured webhook secret required |

## Agent work-request / submission / verification surface

These are the routes an agent uses to request work, act on a task, submit
evidence, and be verified. All mutations require a session (browser) or a
bearer token (terminal agent); none are anonymous.

| Route | Methods | Auth | Live probe (anonymous) |
| --- | --- | --- | --- |
| `GET /api/tasks` | GET | optional | 200 — `personalRequestEnabled: true`, `networkRequestEnabled: false`, `alphaRequestEnabled: false`, `dailyRewardCap: 8` |
| `GET /api/tasks/requests` | GET | optional | not probed (same auth class as /api/tasks) |
| `GET /api/tasks/detail` | GET | optional | 400 `task_id_required` without a taskId |
| `POST /api/tasks/request-intent` | POST | handler | not probed (mutation; needs session) |
| `POST /api/tasks/request` | POST | handler | 401 `task_request_login_required` |
| `POST /api/tasks/action` | POST | handler | 401 `task_login_required` |
| `POST /api/tasks/submission` | POST | handler | 401 `task_submission_login_required` |
| `GET /api/terminal/tasknode/tasks` | GET | bearer | not probed (needs bearer token) |
| `GET /api/terminal/tasknode/requests` | GET/POST | bearer | not probed |
| `GET /api/terminal/tasknode/tasks/{id}` | GET | bearer | not probed |
| `POST /api/terminal/tasknode/tasks/{id}/action` | POST | bearer | not probed |
| `POST /api/terminal/tasknode/tasks/{id}/evidence` | POST | bearer | not probed |
| `GET /api/terminal/tasknode/balance` | GET | bearer | not probed |
| `GET /api/terminal/tasknode/rewards` | GET | bearer | not probed |
| `GET /api/app-state` | GET | optional | 200 (17,602 B) |
| `GET /api/session` | GET | optional | 200 (2,722 B) |
| `GET /api/directory/leaderboard` | GET | optional | 200 (276,491 B) |
| `GET /api/directory/rewarded-tasks` | GET | optional | 200 (205,446 B) |
| `GET /api/hive/projects` | GET | optional | 200 (1,485,087 B) |
| `GET /api/hive/bm-feed` | GET | none | 400 `unknown_board` without a board; 200 with `board=board_pf_terminal` |
| `GET /connect.md` | GET | none | 200 — agent connect instructions |
| `GET /install` , `GET /install/tasknode.mjs` | GET | none | not probed (installer distribution) |
| `POST /mcp` | POST | handler | not probed |
| `GET /api/health` | GET | none | 200 `{"ok":true,"service":"tasknodeofficial","environment":"production"}` |
| `GET /api/readiness` | GET | none | 200 — providers telegram/discord/x/github/email |
| `GET /api/system/status` | GET | none | 200 (32,331 B) |

## Message shapes (from the live anonymous probes)

- `GET /api/tasks` → `{"personalRequestEnabled":true,"networkRequestEnabled":false,
  "alphaRequestEnabled":false,"dailyRewardCap":8,"requests":{"items":[],"sync":
  {"source":"task_requests","status":"wallet_required", ...}}}` — anonymous callers
  see the request switches and an empty item list; a wallet is required to see
  personal requests.
- `GET /api/hive/bm-feed?board=board_pf_terminal` → `{"ok":true,"board":
  {"id":"board_pf_terminal","title":"PF Terminal","status":"active",
  "phase_label":"Submission review"},"agent":{"online":true,"last_seen":...},
  "budget":{"daily_budget_pft":50000,"per_task_cap_pft":5000,
  "per_user_7d_cap_pft":60000,"spent_today_pft":0}, ...}`
- `POST /api/tasks/request` (anonymous, `{}`) → 401
  `{"ok":false,"action":"task_request","error":"task_request_login_required",
  "message":"Sign in before requesting a task.","actionRequired":"Use an account
  login, link a PFT wallet, unlock the local vault, then request again."}`
- `POST /api/tasks/action` (anonymous, `{}`) → 401 `task_login_required`,
  "Sign in before changing a task."
- `POST /api/tasks/submission` (anonymous, `{}`) → 401
  `task_submission_login_required`, "Sign in before submitting task evidence."
- `POST /api/tasks/*` without `Content-Type: application/json` → 415
  `unsupported_media_type`, "The request body does not match this route's
  contract." — the central boundary rejects malformed requests before auth.

## Boundaries (what was NOT probed, and why)

- No session-authenticated route was called: no browser session, cookie, or
  credential was used anywhere in this pack. Session and bearer routes are
  documented from the public source registry only.
- No mutation was attempted with valid credentials (none exist for this pack).
- The `task_request` / `task_action` / `task_submission` request bodies are
  strict JSON (≤ 8,388,608 bytes) per the registry; the exact field contracts
  live in the server handlers, not in the generated reference.
