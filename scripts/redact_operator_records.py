#!/usr/bin/env python3
"""redact_operator_records.py — redact per-user identifiers from Task Node
public-directory probe outputs before publication.

The Task Node directory/leaderboard endpoints are public and unauthenticated,
but their responses embed per-user records (internal account IDs, wallet
addresses, handles, display names). Validator-topology addresses (VHS) and
the public genesis account are public ledger infrastructure and are NOT
touched by this script — it only targets the six Task Node directory files
listed in TARGETS.

Redactions (value replaced, structure/counts preserved):
  accountId  -> acct_REDACTED
  wallet / walletAddress (r-address value) -> rREDACTED
  handle / displayName -> REDACTED
  any other bare acct_* token -> acct_REDACTED
  any other bare XRPL r-address in these files -> rREDACTED

Handles both plain JSON ("accountId": "acct_...") and JSON-escaped text
inside body_head strings (\\"accountId\\":\\"acct_...\\").
Idempotent: running it twice changes nothing the second time.
Usage: python3 scripts/redact_operator_records.py [pack_dir]
Prints per-file replacement counts. Exit 0 iff no identifier remains in
the target files afterwards.
"""
import json
import os
import re
import sys

PACK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
OUT = os.path.join(PACK, "outputs")

TARGETS = [
    "tn-api-directory-leaderboard.json",
    "tn-api-directory-leaderboard.json.body",
    "tn-api-directory-rewarded-tasks.json",
    "tn-api-directory-rewarded-tasks.json.body",
    "tn-api-hive-projects.json.body",
    "tn-api-system-status.json.body",
]

# Field rules: match "field": "value" in plain or backslash-escaped JSON text.
FIELD_PATTERNS = [
    (re.compile(r'(accountId)(\\*"\s*:\s*\\*")([^"\\]+)'), "acct_REDACTED"),
    (re.compile(r'(walletAddress)(\\*"\s*:\s*\\*")([^"\\]+)'), "rREDACTED"),
    (re.compile(r'(wallet)(\\*"\s*:\s*\\*")([^"\\]+)'), "rREDACTED"),
    (re.compile(r'(handle)(\\*"\s*:\s*\\*")([^"\\]+)'), "REDACTED"),
    (re.compile(r'(displayName)(\\*"\s*:\s*\\*")([^"\\]+)'), "REDACTED"),
]
BARE_ACCT = re.compile(r"acct_[A-Za-z0-9_]+")
# XRPL base58 address (excludes 0, O, I, l so camelCase words do not match).
BARE_ADDR = re.compile(r"r[1-9A-HJ-NP-Za-km-z]{25,34}")


def redact_text(text):
    counts = {}
    for pat, repl in FIELD_PATTERNS:
        text, n = pat.subn(lambda m: m.group(1) + m.group(2) + repl, text)
        if n:
            counts[pat.pattern[:20]] = counts.get(pat.pattern[:20], 0) + n
    text, n = BARE_ACCT.subn("acct_REDACTED", text)
    if n:
        counts["bare acct_"] = counts.get("bare acct_", 0) + n
    text, n = BARE_ADDR.subn("rREDACTED", text)
    if n:
        counts["bare r-address"] = counts.get("bare r-address", 0) + n
    return text, counts


def main():
    total = {}
    for name in TARGETS:
        path = os.path.join(OUT, name)
        if not os.path.exists(path):
            print(f"SKIP (missing): {name}")
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        new_text, counts = redact_text(text)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"{name}: {counts if counts else 'no identifiers found'}")
        for k, v in counts.items():
            total[k] = total.get(k, 0) + v
    # Verify: no identifier remains in the target files.
    leftovers = []
    for name in TARGETS:
        path = os.path.join(OUT, name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        # The placeholder itself (acct_REDACTED) is not an identifier.
        if re.search(r"acct_(?!REDACTED\b)[A-Za-z0-9_]+", text):
            leftovers.append((name, "acct_"))
        # rREDACTED itself is too short to match the base58 pattern; a real
        # address still would.
        if re.search(r"r[1-9A-HJ-NP-Za-km-z]{25,34}", text):
            leftovers.append((name, "r-address"))
        # Allowed values after redaction: the placeholders, "" or null.
        for field in ("handle", "displayName", "wallet", "walletAddress",
                      "accountId"):
            if re.search(
                field + r'\\*"\s*:\s*\\*"(?!REDACTED|acct_REDACTED|rREDACTED'
                r'|"|null)',
                text,
            ):
                leftovers.append((name, field))
    if leftovers:
        print(f"LEFTOVER IDENTIFIERS: {leftovers}")
        return 1
    print(f"TOTAL replacements: {total}")
    print("OK: no per-user identifiers remain in the target files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
