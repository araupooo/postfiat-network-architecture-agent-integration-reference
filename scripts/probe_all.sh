#!/usr/bin/env bash
# probe_all.sh — re-run the live observation suite into a target directory.
# All probes are anonymous and unauthenticated. Usage: bash scripts/probe_all.sh [pack_dir] [out_dir]
set -u
PACK="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
OUT="${2:-$PACK/outputs/live-recheck}"
mkdir -p "$OUT"
H="rpc.testnet.postfiat.org"
fail=0
echo "probing into $OUT"
python3 "$PACK/scripts/probe_rpc.py" "$H" server_info '{}' > "$OUT/recheck-server_info.json" || fail=1
python3 "$PACK/scripts/probe_rpc.py" "$H" ledger '{"ledger_index":"validated"}' > "$OUT/recheck-ledger.json" || fail=1
python3 "$PACK/scripts/probe_rpc.py" "$H" fee '{}' > "$OUT/recheck-fee.json" || fail=1
python3 "$PACK/scripts/probe_rpc.py" "$H" validators '{}' > "$OUT/recheck-validators.json" || fail=1
python3 "$PACK/scripts/probe_http.py" "https://vhs.testnet.postfiat.org/v1/network/validators" "$OUT/recheck-vhs-validators.json" || fail=1
python3 "$PACK/scripts/probe_http.py" "https://vhs.testnet.postfiat.org/v1/network/topology/nodes" "$OUT/recheck-vhs-nodes.json" || fail=1
python3 "$PACK/scripts/probe_http.py" "https://explorer.testnet.postfiat.org/api/v1/metrics" "$OUT/recheck-explorer-metrics.json" || fail=1
python3 "$PACK/scripts/probe_http.py" "https://explorer.testnet.postfiat.org/api/v1/health" "$OUT/recheck-explorer-health.json" || fail=1
python3 "$PACK/scripts/probe_http.py" "https://tasknode.postfiat.org/api/health" "$OUT/recheck-tn-health.json" || fail=1
python3 "$PACK/scripts/probe_http.py" "https://tasknode.postfiat.org/api/tasks" "$OUT/recheck-tn-tasks.json" || fail=1
echo "probe_all done (fail=$fail)"
exit $fail
