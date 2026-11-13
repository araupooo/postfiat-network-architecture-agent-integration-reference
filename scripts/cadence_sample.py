#!/usr/bin/env python3
"""Poll server_info every N seconds for M minutes; log validated seq + time.
Usage: cadence_sample.py <host> <interval_s> <samples> <out_jsonl>"""
import json, subprocess, sys, time
host, interval, n, out = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
probe = sys.argv[0].rsplit("/", 1)[0] + "/probe_rpc.py"
with open(out, "a") as f:
    for i in range(n):
        t0 = time.time()
        r = subprocess.run(["python3", probe, host, "server_info", "{}"],
                           capture_output=True, text=True, timeout=60)
        try:
            d = json.loads(r.stdout)
            info = d["response"]["result"]["info"]
            rec = {"sample": i, "wall_utc": d["fetched_at_utc"], "rtt_s": d["rtt_s"],
                   "validated_seq": info["validated_ledger"]["seq"],
                   "validated_age": info["validated_ledger"]["age"],
                   "peers": info["peers"], "proposers": info["last_close"]["proposers"],
                   "converge_time_s": info["last_close"]["converge_time_s"],
                   "complete_ledgers": info["complete_ledgers"],
                   "validation_quorum": info["validation_quorum"],
                   "load_factor": info["load_factor"]}
        except Exception as e:
            rec = {"sample": i, "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "error": str(e), "stdout_tail": r.stdout[-300:], "stderr_tail": r.stderr[-300:]}
        f.write(json.dumps(rec) + "\n"); f.flush()
        print(json.dumps(rec), flush=True)
        dt = time.time() - t0
        if i < n - 1 and dt < interval:
            time.sleep(interval - dt)
