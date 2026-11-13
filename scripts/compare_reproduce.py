#!/usr/bin/env python3
"""compare_reproduce.py — compare a fresh run against the shipped evidence.
Exact equality for deterministic recomputations (cadence/VHS/ledger aggregates
over the shipped outputs, demo results, topology map). Ranges and structural
invariants for live re-check values (they drift by design):
  network_id == 2025, validation_quorum == 17, base_fee == 10 drops,
  live ledger seq > shipped last seq, VHS validator count within +/-10 of 66,
  VHS node count within +/-10 of 71, explorer metrics well-formed.
Exit 0 iff all checks pass. Usage: python3 scripts/compare_reproduce.py [pack_dir]"""
import json, os, sys

PACK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, DER, LR = (os.path.join(PACK, p) for p in ("outputs", "outputs/derived", "outputs/live-recheck"))
checks = []

def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + ((" — " + str(detail)) if detail else ""))

def load(p):
    with open(p) as f:
        return json.load(f)

# --- deterministic recomputations (exact) ---
for name in ("cadence", "vhs", "ledger"):
    shipped = load(os.path.join(DER, name + ".json.shipped")) if os.path.exists(os.path.join(DER, name + ".json.shipped")) else None
    fresh = load(os.path.join(DER, name + ".json"))
    if shipped is not None:
        check(f"derived/{name}.json identical to shipped", shipped == fresh,
              "" if shipped == fresh else "recomputed aggregates differ from shipped")
    else:
        check(f"derived/{name}.json present", True, "no shipped copy to compare (first run)")
fr = load(os.path.join(DER, "failure-recovery.json"))
check("failure-recovery demos all passed", fr["all_passed"],
      "demos: " + ", ".join(f"{k}={v['passed']}" for k, v in fr["demos"].items()))
if os.path.exists(os.path.join(DER, "topology.md.shipped")):
    same = open(os.path.join(DER, "topology.md")).read() == open(os.path.join(DER, "topology.md.shipped")).read()
    check("derived/topology.md identical to shipped", same)
else:
    check("derived/topology.md present", os.path.exists(os.path.join(DER, "topology.md")))

# --- live re-check (ranges / invariants) ---
def recheck(name):
    p = os.path.join(LR, name)
    return load(p) if os.path.exists(p) else None

si = recheck("recheck-server_info.json")
if si is None:
    check("live server_info fetched", False, "no recheck file (network?)")
else:
    info = si["response"]["result"]["info"]
    check("live network_id == 2025", info["network_id"] == 2025, info["network_id"])
    check("live validation_quorum == 17", info["validation_quorum"] == 17, info["validation_quorum"])
    check("live build_version == 1.0.9", info["build_version"] == "1.0.9", info["build_version"])
    shipped_last = load(os.path.join(DER, "cadence.json"))["last_seq"]
    check("live validated seq > shipped last seq", info["validated_ledger"]["seq"] > shipped_last,
          f"live {info['validated_ledger']['seq']} vs shipped {shipped_last}")
    check("live server_state == full", info["server_state"] == "full", info["server_state"])
    check("live peers >= 1", info["peers"] >= 1, info["peers"])

fee = recheck("recheck-fee.json")
if fee is None:
    check("live fee fetched", False)
else:
    check("live base_fee == 10 drops", fee["response"]["result"]["drops"]["base_fee"] == "10",
          fee["response"]["result"]["drops"]["base_fee"])

vv = recheck("recheck-vhs-validators.json")
if vv is None:
    check("live VHS validators fetched", False)
else:
    body = load(os.path.join(LR, "recheck-vhs-validators.json.body"))
    check("live VHS validator count within 56..76", 56 <= body["count"] <= 76, body["count"])
    unl = sum(1 for x in body["validators"] if x.get("unl"))
    check("live VHS UNL count within 20..30", 20 <= unl <= 30, unl)

vn = recheck("recheck-vhs-nodes.json")
if vn is None:
    check("live VHS nodes fetched", False)
else:
    body = load(os.path.join(LR, "recheck-vhs-nodes.json.body"))
    check("live VHS node count within 61..81", 61 <= body["count"] <= 81, body["count"])

em = recheck("recheck-explorer-metrics.json")
if em is None:
    check("live explorer metrics fetched", False)
else:
    body = json.loads(open(os.path.join(LR, "recheck-explorer-metrics.json.body")).read())
    check("live explorer metrics well-formed", set(body) >= {"base_fee", "txn_sec", "ledger_interval"},
          list(body.keys()))

tn = recheck("recheck-tn-tasks.json")
if tn is None:
    check("live Task Node tasks fetched", False)
else:
    body = json.loads(open(os.path.join(LR, "recheck-tn-tasks.json.body")).read())
    check("live Task Node tasks well-formed", "personalRequestEnabled" in body,
          f"personal={body.get('personalRequestEnabled')} network={body.get('networkRequestEnabled')}")

rv = recheck("recheck-validators.json")
if rv is None:
    check("live admin-method block re-check fetched", False)
else:
    check("live admin methods still 403", rv["http_status"] == 403, rv["http_status"])

fails = [c for c in checks if not c[1]]
print(f"\n{len(checks) - len(fails)}/{len(checks)} checks passed, {len(fails)} failed")
sys.exit(0 if not fails else 1)
