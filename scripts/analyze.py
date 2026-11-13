#!/usr/bin/env python3
"""analyze.py — derive headline numbers from the shipped unedited outputs.
Reads pack/outputs/*, writes pack/outputs/derived/*.json. Deterministic:
it recomputes every number in the docs from the shipped files, so a reviewer
can re-run it and get identical values. Live values are NOT re-fetched here.
Usage: python3 scripts/analyze.py [pack_dir]"""
import json, statistics, collections, datetime, os, sys

PACK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PACK, "outputs")
DER = os.path.join(OUT, "derived")
os.makedirs(DER, exist_ok=True)

def load(name):
    with open(os.path.join(OUT, name)) as f:
        return json.load(f)

def load_body(name):
    with open(os.path.join(OUT, name + ".body")) as f:
        return json.load(f)

def strkeys(d):
    return {(k if k is not None else "null"): v for k, v in d.items()}

def w(name, obj):
    with open(os.path.join(DER, name), "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    print("wrote derived/" + name)

# --- cadence ---
rows = [json.loads(l) for l in open(os.path.join(OUT, "cadence-run1.jsonl")) if l.strip()]
seqs = [r["validated_seq"] for r in rows]
times = [datetime.datetime.strptime(r["wall_utc"], "%Y-%m-%dT%H:%M:%SZ") for r in rows]
span_s = (times[-1] - times[0]).total_seconds()
intervals = [(t2 - t1).total_seconds() / (s2 - s1)
             for (t1, t2), (s1, s2) in zip(zip(times, times[1:]), zip(seqs, seqs[1:]))]
cadence = {
    "samples": len(rows), "span_s": span_s,
    "first_seq": seqs[0], "last_seq": seqs[-1], "growth": seqs[-1] - seqs[0],
    "ledgers_per_min": round((seqs[-1] - seqs[0]) / (span_s / 60), 2),
    "close_interval_s": {"mean": round(statistics.mean(intervals), 3),
                         "median": round(statistics.median(intervals), 3),
                         "min": round(min(intervals), 3), "max": round(max(intervals), 3)},
    "per_sample_seq_gaps": dict(collections.Counter(b - a for a, b in zip(seqs, seqs[1:]))),
    "peers": sorted(set(r["peers"] for r in rows)),
    "proposers": sorted(set(r["proposers"] for r in rows)),
    "validation_quorum": sorted(set(r["validation_quorum"] for r in rows)),
    "converge_time_s_range": [min(r["converge_time_s"] for r in rows), max(r["converge_time_s"] for r in rows)],
    "validated_age_range": [min(r["validated_age"] for r in rows), max(r["validated_age"] for r in rows)],
    "rtt_s_mean": round(statistics.mean(r["rtt_s"] for r in rows), 3),
    "complete_ledgers_first": rows[0]["complete_ledgers"],
    "complete_ledgers_last": rows[-1]["complete_ledgers"],
    "first_wall_utc": rows[0]["wall_utc"], "last_wall_utc": rows[-1]["wall_utc"],
}
w("cadence.json", cadence)

# --- ledger / fee burn ---
lh1 = load("rpc-ledger.json")["response"]["result"]["ledger"]
lh2 = load("rpc-ledger_data.json")["response"]["result"]["ledger"]
t1 = datetime.datetime.strptime(lh1["close_time_iso"], "%Y-%m-%dT%H:%M:%SZ")
t2 = datetime.datetime.strptime(lh2["close_time_iso"], "%Y-%m-%dT%H:%M:%SZ")
fee = load("rpc-fee.json")["response"]["result"]
ledger = {
    "first_seq": int(lh1["ledger_index"]), "second_seq": int(lh2["ledger_index"]),
    "first_total_coins_drops": int(lh1["total_coins"]), "second_total_coins_drops": int(lh2["total_coins"]),
    "burned_drops": int(lh1["total_coins"]) - int(lh2["total_coins"]),
    "elapsed_s": (t2 - t1).total_seconds(),
    "base_fee_drops": int(fee["drops"]["base_fee"]),
    "median_fee_drops": int(fee["drops"]["median_fee"]),
    "current_queue_size": int(fee["current_queue_size"]),
    "max_queue_size": int(fee["max_queue_size"]),
    "reserve_base_drops": int(lh1.get("reserve_base_xrp", 0)) if "reserve_base_xrp" in lh1 else None,
    "close_time_resolution_s": lh1["close_time_resolution"],
}
w("ledger.json", ledger)

# --- VHS validators + topology ---
vals = load_body("vhs-testnet-v1-network-validators.json")["validators"]
nodes = load_body("vhs-testnet-v1-network-topology-nodes.json.body".replace(".body", "")) if False else load_body("vhs-testnet-v1-network-topology-nodes.json")["nodes"]
unl = [x for x in vals if x.get("unl")]
def agree(key):
    m = sum(x[key]["missed"] for x in vals)
    t = sum(x[key]["total"] for x in vals)
    return {"missed": m, "total": t, "miss_rate_pct": round(100 * m / t, 5) if t else None}
vhs = {
    "validators_total": len(vals),
    "unl_count": len(unl), "non_unl_count": len(vals) - len(unl),
    "unl_share_pct": round(100 * len(unl) / len(vals), 1),
    "revoked": sum(1 for x in vals if x.get("revoked")),
    "partial": sum(1 for x in vals if x.get("partial")),
    "with_domain": sum(1 for x in vals if x.get("domain")),
    "domain_verified": sum(1 for x in vals if x.get("domain_verified")),
    "postfiat_org_domain": sum(1 for x in vals if x.get("domain") == "postfiat.org"),
    "postfiat_org_domain_unl": sum(1 for x in vals if x.get("domain") == "postfiat.org" and x.get("unl")),
    "server_versions": dict(collections.Counter(x.get("server_version") for x in vals)),
    "base_fee_drops": sorted(set(x.get("base_fee") for x in vals)),
    "agreement_24h": agree("agreement_24h"),
    "agreement_1h": agree("agreement_1h"),
    "agreement_24h_perfect": sum(1 for x in vals if x["agreement_24h"]["score"] == "1.00000"),
    "unl_agreement_24h": {"missed": sum(x["agreement_24h"]["missed"] for x in unl),
                           "total": sum(x["agreement_24h"]["total"] for x in unl)},
    "unl_all_on_1_0_9": all(x.get("server_version") == "1.0.9" for x in unl),
    "unl_all_have_domains": all(x.get("domain") for x in unl),
    "current_index_range": [min(x["current_index"] for x in vals), max(x["current_index"] for x in vals)],
    "distinct_hashes_per_index": {str(k): len(v) for k, v in
        ((idx, set(x["ledger_hash"] for x in vals if x["current_index"] == idx))
         for idx in sorted(set(x["current_index"] for x in vals)))},
    "topology_nodes": len(nodes),
    "topology_versions": dict(collections.Counter(x.get("version") for x in nodes)),
    "topology_countries_top": collections.Counter(x.get("country") for x in nodes).most_common(8),
    "topology_countries_distinct": len(set(x.get("country") for x in nodes if x.get("country"))),
    "inbound_total": sum(x.get("inbound_count") or 0 for x in nodes),
    "outbound_total": sum(x.get("outbound_count") or 0 for x in nodes),
    "zero_inbound_nodes": sum(1 for x in nodes if (x.get("inbound_count") or 0) == 0),
    "hub_nodes": [{"pubkey_prefix": n["node_public_key"][:16], "inbound": n.get("inbound_count"),
                   "outbound": n.get("outbound_count"), "country": n.get("country"), "city": n.get("city")}
                  for n in sorted(nodes, key=lambda x: -(x.get("inbound_count") or 0))[:3]],
    "server_state": strkeys(collections.Counter(x.get("server_state") for x in nodes)),
    "io_latency_ms_median": statistics.median([x["io_latency_ms"] for x in nodes if x.get("io_latency_ms") is not None]),
}
w("vhs.json", vhs)

# --- Task Node public probes ---
tn = {}
for name in sorted(os.listdir(OUT)):
    if name.startswith("tn-") and name.endswith(".json"):
        d = load(name)
        tn[name] = {"http_status": d["http_status"], "rtt_s": d["rtt_s"],
                    "body_bytes": d["body_bytes"], "fetched_at_utc": d["fetched_at_utc"],
                    "body_head": d["body_head"][:200]}
w("tasknode-probes.json", tn)

# --- RPC probes ---
rpc = {}
for name in sorted(os.listdir(OUT)):
    if name.startswith("rpc-") and name.endswith(".json"):
        d = load(name)
        rpc[name] = {"method": d["method"], "http_status": d["http_status"], "rtt_s": d["rtt_s"],
                     "fetched_at_utc": d["fetched_at_utc"]}
w("rpc-probes.json", rpc)
print("OK: cadence %d samples, %d validators, %d UNL, %d nodes" % (len(rows), len(vals), len(unl), len(nodes)))
