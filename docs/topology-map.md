# Validator topology map — PostFiat testnet (measured 2026-11-13)

The map and tables below are generated from the live Validator History
Service (VHS) API responses shipped in `outputs/` (`src/topology.py`
regenerates them deterministically). All counts are the 02:36–02:37 UTC
snapshot; see `outputs/derived/vhs.json` for the machine-readable numbers.

```mermaid
flowchart TB
    subgraph UNL[UNL — 25 validators, quorum 17]
        U1[25 UNL members<br/>all on postfiatd 1.0.9<br/>all with verified domains]
    end
    subgraph NONUNL[Non-UNL validators — 41]
        N1[41 validators<br/>30 with verified domains<br/>versions 1.0.9 / 1.0.4 / 1.0.0 / 1.0.8]
    end
    subgraph TOPO[P2P topology — 71 nodes, 730 edges]
        H0[Hub n9M7RRXWAEZY…<br/>Atlanta, United States<br/>inbound 47 / outbound 10]
        H1[Hub n9K5JWvHTSyL…<br/>Atlanta, United States<br/>inbound 47 / outbound 10]
        H2[Hub n9LYanpKcAGs…<br/>Atlanta, United States<br/>inbound 46 / outbound 10]
        R[Other 68 nodes<br/>median io_latency 1 ms]
    end
    RPC[rpc.testnet.postfiat.org<br/>public JSON-RPC :443<br/>node n9K4AomB… (Canary Wharf)<br/>21 peers, server_state full]
    VHS[vhs.testnet.postfiat.org<br/>Validator History Service API<br/>/v1/network/validators + /v1/network/topology]
    EXP[explorer.testnet.postfiat.org<br/>/api/v1/metrics + /api/v1/health]
    UNL -->|validations, 17/25 quorum| RPC
    NONUNL -->|validations| RPC
    TOPO -->|crawled peer graph| VHS
    RPC -->|server_info / ledger / fee| EXP
```

## Counts

| Layer | Count | Source |
| --- | --- | --- |
| Validators with manifests (VHS) | 66 | `outputs/vhs-testnet-v1-network-validators.json` |
| UNL members | 25 | same, `unl: true` |
| Non-UNL validators | 41 | same |
| P2P topology nodes | 71 | `outputs/vhs-testnet-v1-network-topology-nodes.json` |
| P2P edges (inbound total = outbound total) | 730 | same, summed per-node counts |
| Probed node's peers (single-node view) | 21 | `outputs/cadence-run1.jsonl` (constant across 21 samples) |
| Proposers in last close | 25 | same |
| Validation quorum | 17 | same |

## Geography (topology nodes)

| Country | Nodes |
| --- | --- |
| United States | 17 |
| Philippines | 11 |
| Germany | 10 |
| United Kingdom | 5 |
| France | 5 |
| Canada | 3 |
| Singapore | 3 |
| Switzerland | 3 |

(8 countries shown; the 71 nodes span 17 distinct countries in total —
see `derived/vhs.json`.)

## Node versions (topology nodes)

| Version | Nodes |
| --- | --- |
| 1.0.9 | 59 |
| 1.0.4 | 9 |
| 1.0.0 | 2 |
| 1.0.8 | 1 |

## Hub nodes (highest inbound peer count)

| Node (prefix) | City, country | Inbound | Outbound | Version |
| --- | --- | --- | --- | --- |
| `n9M7RRXWAEZYgFBH…` | Atlanta, United States | 47 | 10 | 1.0.9 |
| `n9K5JWvHTSyLgYdD…` | Atlanta, United States | 47 | 10 | 1.0.9 |
| `n9LYanpKcAGsZfBF…` | Atlanta, United States | 46 | 10 | 1.0.9 |

## What the numbers mean

- **66 validators vs 25 UNL vs 71 nodes.** Three different populations:
  validators with published manifests (66); the subset the network trusts
  for consensus (UNL, 25); and P2P nodes the VHS crawler has seen (71,
  which includes non-validating nodes). The UNL is 37.9% of validators.
- **Quorum 17 of 25 (68%).** `validation_quorum: 17` was constant in all 21
  cadence samples, and `proposers: 25` in every `last_close`. 17/25 ≈ 68%,
  matching the amendment majority threshold 0.67 configured in the VHS
  `.env.testnet` (fixture `vhs-env-testnet.txt`). This is the *ledger
  validation* quorum of the live rippled-style consensus — not the Cobalt
  ratification quorum `q_S = ceil(4·n_S/5)` of the l1v2 design (see
  `docs/consensus-flow.md`).
- **Agreement is near-perfect.** 24h missed validations: 48 of 1,881,457
  (0.00255%); 1h missed: 0. 62 of 66 validators scored a perfect 1.00000
  over 24h. UNL members missed 6 of 714,025 (99.9992% agreement).
- **Version skew is confined to non-UNL seats.** All 25 UNL members run
  1.0.9; the 12 lagging validators (9×1.0.4, 2×1.0.0, 1×1.0.8) are all
  non-UNL, so consensus itself is unaffected (finding F-05).
- **Concentration.** Three Atlanta nodes carry 140 of 730 inbound edges
  (~19%). The top three countries hold 38 of 71 nodes. 13 nodes report 0
  inbound peers and null `server_state` — in the crawler's record but not
  currently reachable or not reporting state.
- **The probed RPC node is identifiable in both views.** `server_info`
  returns node key `n9K4AomB…` (hostid MUFF, uptime 1,417,552 s at 02:32
  UTC); the VHS topology lists the same key at 192.248.151.4, Canary Wharf,
  London, inbound 11 / outbound 10, uptime 1,417,847 s at ~02:37 UTC — the
  uptimes agree to within the elapsed time, cross-validating the two sources.
- **Operator identity is domain-based.** 57 of 66 validators publish a
  domain; 55 are verified. The 25 UNL domains are 25 distinct
  community/operator domains (e.g. `pft.bigwoodnode.com`,
  `lc66validator.postfiatcn.org`, `validator.pftperry.com`); the 3
  `postfiat.org`-domain validators are all non-UNL (finding F-08).
- **Node keys ≠ validation keys.** Topology nodes are keyed by node public
  key, validators by validation public key; the two sets cannot be joined on
  key. The VHS topology summary's `link_count: 0` contradicts its own node
  records (730 edges) — use the per-node counts (finding F-09).
