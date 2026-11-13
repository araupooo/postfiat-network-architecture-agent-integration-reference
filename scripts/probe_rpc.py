#!/usr/bin/env python3
"""probe_rpc.py — call a PostFiat rippled JSON-RPC method over public HTTPS and print raw JSON.
Usage: probe_rpc.py <host> <method> [json-params] [timeout-s]
No auth, no credentials. Records wall-clock time and HTTP status in the output envelope."""
import json, sys, time, urllib.request, urllib.error

def main():
    host, method = sys.argv[1], sys.argv[2]
    params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 30
    body = json.dumps({"method": method, "params": [params]}).encode()
    req = urllib.request.Request(f"https://{host}/", data=body,
                                 headers={"Content-Type": "application/json", "User-Agent": "postfiat-arch-probe/1.0"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            status = r.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        status = e.code
    except Exception as e:
        print(json.dumps({"probe_error": str(e), "method": method, "host": host,
                          "fetched_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}))
        return 1
    dt = time.time() - t0
    try:
        parsed = json.loads(raw) if raw.strip() else None
    except Exception:
        parsed = {"_unparsable_body": raw[:500]}
    print(json.dumps({"host": host, "method": method, "params": params,
                      "http_status": status, "rtt_s": round(dt, 3),
                      "fetched_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      "raw_body_bytes": len(raw),
                      "response": parsed}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
