#!/usr/bin/env bash
# run_all.sh — single reproduction entry point.
# 1. Recompute derived aggregates from the shipped outputs (deterministic).
# 2. Re-run the failure-recovery demos.
# 3. Rebuild the topology map from the shipped VHS outputs.
# 4. Take a fresh live re-check (server_info, ledger, fee, VHS validators,
#    explorer metrics, Task Node health/tasks) into outputs/live-recheck/.
# 5. Compare: exact equality for deterministic recomputations; ranges and
#    structural invariants for live values (they drift).
# Exit 0 only if every check passes. Usage: ./scripts/run_all.sh
set -u
cd "$(dirname "$0")/.."
PACK="$PWD"
LOG="outputs/run_all.log"
mkdir -p outputs/live-recheck
exec > >(tee "$LOG") 2>&1
echo "=== run_all started $(date -u +%Y-%m-%dT%H:%M:%SZ) pack=$PACK ==="
cp outputs/derived/cadence.json outputs/derived/cadence.json.shipped 2>/dev/null || true
cp outputs/derived/vhs.json outputs/derived/vhs.json.shipped 2>/dev/null || true
cp outputs/derived/ledger.json outputs/derived/ledger.json.shipped 2>/dev/null || true
cp outputs/derived/failure-recovery.json outputs/derived/failure-recovery.json.shipped 2>/dev/null || true
cp outputs/derived/topology.md outputs/derived/topology.md.shipped 2>/dev/null || true
echo "--- analyze.py ---"
python3 scripts/analyze.py "$PACK" || exit 1
echo "--- failure_recovery_demo.py ---"
python3 scripts/failure_recovery_demo.py "$PACK" > outputs/derived/failure-recovery.stdout 2>&1 || { echo "DEMO FAILED"; exit 1; }
echo "--- topology.py ---"
python3 src/topology.py "$PACK" || exit 1
echo "--- probe_all.sh (live re-check) ---"
bash scripts/probe_all.sh "$PACK" outputs/live-recheck || echo "WARNING: live re-check had failures (network); continuing to compare"
echo "--- compare_reproduce.py ---"
python3 scripts/compare_reproduce.py "$PACK"
RC=$?
rm -f outputs/derived/*.shipped
echo "=== run_all finished rc=$RC $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
exit $RC
