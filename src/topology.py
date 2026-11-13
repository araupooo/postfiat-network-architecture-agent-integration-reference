#!/usr/bin/env python3
"""topology.py — build the validator-topology map + tables from the shipped VHS outputs.
Deterministic: same inputs give the same docs/topology-map.md content.
Usage: python3 src/topology.py [pack_dir]"""
import json, os, sys, collections

PACK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PACK, "outputs")

def load_body(name):
    with open(os.path.join(OUT, name + ".body")) as f:
        return json.load(f)

vals = load_body("vhs-testnet-v1-network-validators.json")["validators"]
nodes = load_body("vhs-testnet-v1-network-topology-nodes.json")["nodes"]
unl = [x for x in vals if x["unl"]]
hubs = sorted(nodes, key=lambda x: -(x.get("inbound_count") or 0))[:3]
countries = collections.Counter(x.get("country") for x in nodes if x.get("country")).most_common(8)
versions = collections.Counter(x.get("version") for x in nodes)

lines = []
lines.append("# Validator topology — generated from live VHS data")
lines.append("")
lines.append("Source: `outputs/vhs-testnet-v1-network-topology-nodes.json` + "
             "`outputs/vhs-testnet-v1-network-validators.json`, fetched 2026-11-13 02:36–02:37 UTC. "
             "Regenerate with `python3 src/topology.py`.")
lines.append("")
lines.append("```mermaid")
lines.append("flowchart TB")
lines.append("    subgraph UNL[UNL — 25 validators, quorum 17]")
lines.append("        U1[25 UNL members<br/>all on postfiatd 1.0.9<br/>all with verified domains]")
lines.append("    end")
lines.append("    subgraph NONUNL[Non-UNL validators — 41]")
lines.append("        N1[41 validators<br/>30 with verified domains<br/>versions 1.0.9 / 1.0.4 / 1.0.0 / 1.0.8]")
lines.append("    end")
lines.append("    subgraph TOPO[P2P topology — 71 nodes, 730 edges]")
for i, h in enumerate(hubs):
    lines.append(f"        H{i}[Hub {h['node_public_key'][:12]}…<br/>{h.get('city')}, {h.get('country')}<br/>inbound {h.get('inbound_count')} / outbound {h.get('outbound_count')}]")
lines.append("        R[Other 68 nodes<br/>median io_latency 1 ms]")
lines.append("    end")
lines.append("    RPC[rpc.testnet.postfiat.org<br/>public JSON-RPC :443<br/>node n9K4AomB… (Canary Wharf)<br/>21 peers, server_state full]")
lines.append("    VHS[vhs.testnet.postfiat.org<br/>Validator History Service API<br/>/v1/network/validators + /v1/network/topology]")
lines.append("    EXP[explorer.testnet.postfiat.org<br/>/api/v1/metrics + /api/v1/health]")
lines.append("    UNL -->|validations, 17/25 quorum| RPC")
lines.append("    NONUNL -->|validations| RPC")
lines.append("    TOPO -->|crawled peer graph| VHS")
lines.append("    RPC -->|server_info / ledger / fee| EXP")
lines.append("```")
lines.append("")
lines.append("## Counts")
lines.append("")
lines.append("| Layer | Count | Source |")
lines.append("| --- | --- | --- |")
lines.append(f"| Validators with manifests (VHS) | {len(vals)} | vhs-testnet-v1-network-validators.json |")
lines.append(f"| UNL members | {len(unl)} | same, `unl: true` |")
lines.append(f"| Non-UNL validators | {len(vals) - len(unl)} | same |")
lines.append(f"| P2P topology nodes | {len(nodes)} | vhs-testnet-v1-network-topology-nodes.json |")
lines.append(f"| P2P edges (inbound total = outbound total) | {sum(x.get('inbound_count') or 0 for x in nodes)} | same, summed per-node counts |")
lines.append(f"| Probed node's peers (single-node view) | 21 | rpc server_info, cadence-run1.jsonl |")
lines.append(f"| Proposers in last close | 25 | same |")
lines.append(f"| Validation quorum | 17 | same |")
lines.append("")
lines.append("## Geography (topology nodes)")
lines.append("")
lines.append("| Country | Nodes |")
lines.append("| --- | --- |")
for c, n in countries:
    lines.append(f"| {c} | {n} |")
lines.append("")
lines.append("## Node versions (topology nodes)")
lines.append("")
lines.append("| Version | Nodes |")
lines.append("| --- | --- |")
for v, n in sorted(versions.items(), key=lambda kv: -kv[1]):
    lines.append(f"| {v} | {n} |")
lines.append("")
lines.append("## Hub nodes (highest inbound peer count)")
lines.append("")
lines.append("| Node (prefix) | City, country | Inbound | Outbound | Version |")
lines.append("| --- | --- | --- | --- | --- |")
for h in hubs:
    lines.append(f"| `{h['node_public_key'][:16]}…` | {h.get('city')}, {h.get('country')} | {h.get('inbound_count')} | {h.get('outbound_count')} | {h.get('version')} |")
lines.append("")
lines.append("## Reading notes")
lines.append("")
lines.append("- Node keys and validation keys are different key types: the 71 topology nodes and the 66 validators cannot be joined on public key. The probed RPC node (`n9K4AomB…`) is the one node identified in both views because `server_info` returns its node key and the VHS topology lists the same key with its IP and geo.")
lines.append("- The VHS `/v1/network/topology` summary reports `link_count: 0` while its own node records sum to 730 inbound and 730 outbound edges. Use the per-node counts, not the summary field (see finding F-09).")
lines.append("- 13 of 71 nodes report 0 inbound peers and null `server_state`; they are in the crawler's record but not currently reachable or not reporting state. They are counted, not excluded.")
lines.append("- The 3 `postfiat.org`-domain validators are all non-UNL. The 25 UNL seats are held by 25 distinct community/operator domains.")
os.makedirs(os.path.join(OUT, "derived"), exist_ok=True)
with open(os.path.join(OUT, "derived", "topology.md"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("wrote derived/topology.md (%d lines)" % len(lines))
