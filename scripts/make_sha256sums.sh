#!/usr/bin/env bash
# make_sha256sums.sh — regenerate SHA256SUMS over all pack files except
# SHA256SUMS itself, the .git directory, and the shipped-copy markers.
# Usage: ./scripts/make_sha256sums.sh
set -u
cd "$(dirname "$0")/.."
find . -type f ! -path './.git/*' ! -name 'SHA256SUMS' ! -name '*.shipped' -print0 \
  | sort -z | xargs -0 sha256sum > SHA256SUMS
wc -l SHA256SUMS
