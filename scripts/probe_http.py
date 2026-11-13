#!/usr/bin/env python3
"""probe_http.py — anonymous GET (or HEAD) of a public URL; record status, timing, headers, body.
Usage: probe_http.py <url> <out_file> [method] [body_file] — never sends credentials."""
import json, sys, time, urllib.request, urllib.error
url, out, method = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "GET")
data = None
if len(sys.argv) > 4:
    data = open(sys.argv[4], "rb").read()
req = urllib.request.Request(url, data=data, method=method,
    headers={"User-Agent": "postfiat-arch-probe/1.0", "Accept": "*/*"})
t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
        status, headers = r.status, dict(r.headers)
except urllib.error.HTTPError as e:
    body = e.read(); status, headers = e.code, dict(e.headers)
except Exception as e:
    rec = {"url": url, "method": method, "probe_error": str(e),
           "fetched_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    open(out, "w").write(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2)); sys.exit(1)
dt = time.time() - t0
rec = {"url": url, "method": method, "http_status": status, "rtt_s": round(dt, 3),
       "content_type": headers.get("Content-Type"), "content_length": headers.get("Content-Length"),
       "body_bytes": len(body), "fetched_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "body_head": body[:600].decode("utf-8", "replace")}
open(out, "w").write(json.dumps(rec, indent=2) + "\n")
open(out + ".body", "wb").write(body)
print(json.dumps(rec, indent=2))
