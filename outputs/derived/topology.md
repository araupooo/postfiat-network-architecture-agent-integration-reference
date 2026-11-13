# Validator topology — generated from live VHS data

Source: `outputs/vhs-testnet-v1-network-topology-nodes.json` + `outputs/vhs-testnet-v1-network-validators.json`, fetched 2026-11-13 02:36–02:37 UTC. Regenerate with `python3 src/topology.py`.

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
| Validators with manifests (VHS) | 66 | vhs-testnet-v1-network-validators.json |
| UNL members | 25 | same, `unl: true` |
| Non-UNL validators | 41 | same |
| P2P topology nodes | 71 | vhs-testnet-v1-network-topology-nodes.json |
| P2P edges (inbound total = outbound total) | 730 | same, summed per-node counts |
| Probed node's peers (single-node view) | 21 | rpc server_info, cadence-run1.jsonl |
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

## Reading notes

- Node keys and validation keys are different key types: the 71 topology nodes and the 66 validators cannot be joined on public key. The probed RPC node (`n9K4AomB…`) is the one node identified in both views because `server_info` returns its node key and the VHS topology lists the same key with its IP and geo.
- The VHS `/v1/network/topology` summary reports `link_count: 0` while its own node records sum to 730 inbound and 730 outbound edges. Use the per-node counts, not the summary field (see finding F-09).
- 13 of 71 nodes report 0 inbound peers and null `server_state`; they are in the crawler's record but not currently reachable or not reporting state. They are counted, not excluded.
- The 3 `postfiat.org`-domain validators are all non-UNL. The 25 UNL seats are held by 25 distinct community/operator domains.
