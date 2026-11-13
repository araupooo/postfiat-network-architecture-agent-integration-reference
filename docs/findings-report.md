# Findings and remediation report

Severity: **High** = consensus safety or data integrity at risk; **Medium** =
an integration path is broken or a public signal is misleading;
**Low** = a real defect with limited blast radius; **Info** = an observation
worth recording, no defect implied.

Summary: **0 High, 3 Medium, 6 Low, 4 Info** (13 findings).

## F-01 — Medium: Public WebSocket ledger stream requires authorization

- **Observation.** `wss://rpc.testnet.postfiat.org` (port 443) fails the
  handshake with HTTP 401; port 6005 closes with code 1006. The subscribe
  client received 0 ledger-close events on both endpoints. The same client
  on the same VM successfully subscribed to the XRPL public testnet WS and
  received ledger closes, so the failure is endpoint-specific, not
  client-side. Meanwhile the JSON-RPC endpoint on the same host answers
  unauthenticated `server_info`/`ledger`/`fee` calls.
- **Evidence.** `outputs/ws-ledger-443.jsonl`, `outputs/ws-ledger-6005.jsonl`,
  `outputs/ws-control-xrpl.jsonl`, `outputs/rpc-ledger.json`.
- **Impact.** Agents cannot subscribe to live ledger closes on the public
  testnet; they must poll `server_info`/`ledger` (observed RTT ~0.7–1.3 s),
  which adds latency and load and makes sub-second close detection
  impossible from the public surface.
- **Remediation.** Either publish the WS endpoint for anonymous `ledger`
  subscriptions (read-only, rate-limited), or document polling as the
  supported public pattern with a recommended interval (30 s is sufficient
  for a ~3 s close cadence when only the validated height is needed; 3–5 s
  polling is needed to track individual closes).

## F-02 — Medium: Explorer health endpoint reports "rippled unreachable" while the explorer works

- **Observation.** `GET /api/v1/health` on `explorer.testnet.postfiat.org`
  returns `{"message":"rippled unreachable"}` at the same time
  `/api/v1/metrics` returns live-looking data and the homepage returns
  HTTP 200. The health check hits a P2P socket path that fails while the
  metrics path (which reads the same rippled connection differently) works.
- **Evidence.** `outputs/explorer-testnet-health.json`,
  `outputs/explorer-testnet-metrics-1.json`,
  `outputs/explorer-testnet-metrics-2.json`.
- **Impact.** Any monitoring agent or status page that trusts `/api/v1/health`
  will page a false alarm; the endpoint is currently unusable as a health
  signal.
- **Remediation.** Fix the health check to use the same rippled connection
  the metrics path uses, or return a structured status (`{"ok":false,
  "detail": ...}`) that distinguishes "metrics path down" from "P2P socket
  down". Until fixed, consumers should treat this endpoint as advisory only.

## F-03 — Medium: Explorer metrics are cached/static, not live

- **Observation.** `/api/v1/metrics` returned byte-identical values in two
  fetches ~10 minutes apart (`base_fee 0.00001`, `txn_sec 0.09`,
  `txn_ledger 0.26`, `ledger_interval 3.022`, `avg_fee 0.00001000`) while the
  validated ledger advanced ~200 ledgers and the live close interval measured
  3.036 s mean. The `ledger_interval` 3.022 is close to the measured 3.036 s,
  so the snapshot is plausible — but it is a snapshot, not a live reading.
- **Evidence.** `outputs/explorer-testnet-metrics-1.json`,
  `outputs/explorer-testnet-metrics-2.json`, `outputs/cadence-run1.jsonl`.
- **Impact.** Agents that poll metrics for live throughput or fee changes
  will see no change and may conclude the network is idle or stuck.
- **Remediation.** Either serve live values (or a short TTL with a
  `generatedAt` timestamp in the payload), or document the endpoint as a
  cached snapshot with its refresh interval.

## F-04 — Low: Admin RPC methods are blocked at the public proxy (no public UNL enumeration from the node)

- **Observation.** `validators` and `peers` JSON-RPC methods return HTTP 403
  `Forbidden` from `rpc.testnet.postfiat.org`. The VHS documentation says UNL
  validators are fetched via the admin `validators` RPC, so the public node
  cannot be used to enumerate the UNL; the VHS API is the only public source.
- **Evidence.** `outputs/rpc-validators.json`, `outputs/rpc-peers.json`,
  fixture `vhs-postfiat.md`.
- **Impact.** Agents that need the UNL must depend on the VHS service (a
  second system with its own availability) rather than the node itself.
- **Remediation.** Publish a read-only, rate-limited UNL endpoint (or a
  `validators` method that returns public keys + domains without admin data),
  or document the VHS API as the canonical public UNL source.

## F-05 — Low: 12 of 66 validators run pre-1.0.9 versions

- **Observation.** Node versions: 1.0.9 (59), 1.0.4 (9), 1.0.0 (2), 1.0.8 (1).
  All 25 UNL members run 1.0.9, so consensus is unaffected; the 12 lagging
  validators are all non-UNL.
- **Evidence.** `outputs/derived/vhs.json`, `outputs/vhs-testnet-v1-network-validators.json.body`.
- **Impact.** Non-UNL validators on old versions may serve stale data or
  miss protocol fixes; if any of them is promoted to the UNL without an
  upgrade, the version skew moves into the consensus set.
- **Remediation.** Gate UNL admission on running the current release (or
  document the minimum version), and publish the version distribution in the
  VHS API summary.

## F-06 — Low: P2P topology concentrates on three Atlanta hub nodes

- **Observation.** Three nodes in Atlanta, US carry 46–47 inbound peers each
  (140 of 730 inbound edges, ~19%); the top three countries hold 38 of 71
  nodes. 13 of 71 nodes report 0 inbound peers.
- **Evidence.** `outputs/derived/vhs.json`, `outputs/derived/topology.md`.
- **Impact.** The peer graph depends heavily on three nodes; their loss
  would force ~19% of edges to re-form. This is a testnet property, not a
  consensus failure (validations flow over the UNL, not the P2P graph), but
  it weakens the claim of a well-meshed testnet.
- **Remediation.** Compare against the launch-topology proposal's caps
  (≤2 of 12 seats per provider family, ≤4 of 12 per country) at the
  *registry* level, and track hub concentration as a standing metric in the
  VHS API.

## F-07 — Low: 9 of 66 validators publish no domain; operator identity is domain-only

- **Observation.** 57 of 66 validators publish a domain; 55 are verified.
  9 publish none, 2 publish unverified domains. The public record's only
  operator-identity signal is the domain field.
- **Evidence.** `outputs/derived/vhs.json`.
- **Impact.** Operators without a verified domain cannot be distinguished
  from each other or held accountable by name; control-group analysis (shared
  operator behind multiple seats) is impossible for those seats from public
  data.
- **Remediation.** Require a verified domain for UNL admission (all 25
  current UNL members already have one — the gap is only in the non-UNL
  set), and publish the verification method.

## F-08 — Info: Single-organization administration vs a community-domain UNL

- **Observation.** The whitepaper states "one organization administers the
  current validator fleet" and that independently operated validators remain
  a proposal (devnet context: six Foundation-administered validators). The
  live testnet UNL is 25 seats on 25 distinct community/operator domains,
  and the 3 `postfiat.org`-domain validators are all non-UNL.
- **Evidence.** fixture `whitepaper-excerpts.md` (§1.8),
  `outputs/derived/vhs.json` (`postfiat_org_domain_unl: 0`).
- **Impact.** The public record shows a community-domain UNL, which is
  consistent with a transition toward independent operation — but domain
  diversity does not prove independent control (shared hosting, shared
  funding, or a common operator behind several domains are all invisible
  from public data). Do not claim "independently operated" from this pack.
- **Remediation.** Publish the operator-identity evidence (control-group
  checks, hosting/ASN diversity) the launch-topology proposal calls for, so
  the independence claim becomes checkable.

## F-09 — Info: VHS topology summary `link_count: 0` contradicts its own node records

- **Observation.** `/v1/network/topology` reports `node_count: 71`,
  `link_count: 0`, while `/v1/network/topology/nodes` records sum to 730
  inbound and 730 outbound edges.
- **Evidence.** `outputs/vhs-testnet-v1-network-topology.json`,
  `outputs/vhs-testnet-v1-network-topology-nodes.json`.
- **Impact.** Consumers that trust the summary field will conclude the
  network has no peer links.
- **Remediation.** Fix the summary to sum the node records, or drop the
  field. Consumers should sum per-node counts until then.

## F-10 — Info: Ledger retention window is ~51k ledgers on the probed node

- **Observation.** `complete_ledgers: 7,950,054–8,001,412` at the end of the
  cadence run — about 51,359 ledgers, or ~43 hours at 3 s per ledger.
  History before ledger 7,950,054 is not available from this node.
- **Evidence.** `outputs/cadence-run1.jsonl`.
- **Impact.** Full-history queries (old transactions, old ledger states)
  need an archive node or the VHS/explorer backends; the public RPC node
  alone cannot serve them.
- **Remediation.** Document the retention window on the RPC endpoint (or in
  the explorer), and point archive queries at the VHS service.

## F-11 — Low: Task Node request switch and directory can diverge

- **Observation.** Anonymous `GET /api/tasks` reports
  `networkRequestEnabled: false` while `GET /api/directory/rewarded-tasks`
  still serves a 100-item network-task directory. The live switch and the
  directory disagree about whether network work is requestable.
- **Evidence.** `outputs/tn-api-tasks.json`,
  `outputs/tn-api-directory-rewarded-tasks.json`.
- **Impact.** An agent that reads the directory to decide what to request
  will attempt a request the live switch rejects.
- **Remediation.** Agents should read `/api/tasks` (live) for request
  eligibility and treat the directory as a historical record. The service
  could annotate directory entries with the live switch state.

## F-12 — Info: Fee burn is directly observable and matches the whitepaper

- **Observation.** `total_coins` fell by exactly 60 drops over 31 s between
  two ledger headers 11 ledgers apart — 10 drops per ledger, the base fee.
  No validator subsidy exists; fees burn.
- **Evidence.** `outputs/rpc-ledger.json`, `outputs/rpc-ledger_data.json`,
  `derived/ledger.json`.
- **Impact.** None (confirmation, not a defect). It is the one whitepaper
  economic claim this pack verifies directly from live data.
- **Remediation.** None.

## F-13 — Low: One node's peer count (21) is not the network size (71)

- **Observation.** The probed node reports `peers: 21` (constant across all
  21 cadence samples) while the VHS crawler sees 71 nodes. A single node's
  peer table covers ~30% of the network.
- **Evidence.** `outputs/cadence-run1.jsonl`,
  `outputs/vhs-testnet-v1-network-topology-nodes.json`.
- **Impact.** Agents that quote "21 peers" as the network size understate
  the testnet by 3×.
- **Remediation.** Always pair a node's `peers` figure with the VHS
  topology count, and label which one is being quoted.

## Machine-readable findings

`findings.json` (pack root) carries the same 13 findings with severity,
evidence file paths, and remediation text.
