#!/usr/bin/env bash
# verify_digests.sh — verify SHA256SUMS against the pack files.
# Usage: ./scripts/verify_digests.sh
set -u
cd "$(dirname "$0")/.."
if [ ! -f SHA256SUMS ]; then echo "SHA256SUMS missing — run scripts/make_sha256sums.sh first"; exit 1; fi
sha256sum -c SHA256SUMS
