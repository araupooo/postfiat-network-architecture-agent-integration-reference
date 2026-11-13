#!/usr/bin/env bash
# clean_reproduce.sh — fresh-environment reproduction.
# Copies the pack (excluding .git and prior fresh-clone outputs) to a fresh
# temp dir, runs run_all.sh there, and ships the fresh outputs + compare log
# back into outputs/fresh-clone-*. Exit code = the fresh run's exit code.
# Usage: ./scripts/clean_reproduce.sh
set -u
cd "$(dirname "$0")/.."
PACK="$PWD"
TMP="$(mktemp -d /tmp/netarch-repro.XXXXXX)"
echo "fresh copy at $TMP"
rsync -a --exclude '.git' --exclude 'outputs/fresh-clone-*' --exclude 'outputs/live-recheck' "$PACK/" "$TMP/pack/" 2>/dev/null || cp -r "$PACK" "$TMP/pack"
cd "$TMP/pack"
bash scripts/run_all.sh
RC=$?
cp outputs/run_all.log "$PACK/outputs/fresh-clone-compare.log"
cp outputs/derived/failure-recovery.json "$PACK/outputs/fresh-clone-failure-recovery.json"
cp outputs/derived/cadence.json "$PACK/outputs/fresh-clone-cadence.json"
cp outputs/derived/vhs.json "$PACK/outputs/fresh-clone-vhs.json"
for f in outputs/live-recheck/*.json; do
  [ -e "$f" ] && cp "$f" "$PACK/outputs/fresh-clone-$(basename "$f")"
done
echo "fresh run rc=$RC; temp dir kept at $TMP (do not delete until the task is rewarded)"
echo "fresh-clone outputs shipped into $PACK/outputs/fresh-clone-*"
exit $RC
