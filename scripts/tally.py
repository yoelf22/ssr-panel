#!/usr/bin/env python3
"""Count how often themes appear in a field, per persona kind.
Usage: tally.py <outdir> <field> 'label=word1|word2' ['label=...' ...]
Also tallies any extra categorical field, e.g.: tally.py out first_buy"""
import sys, json, glob, collections
R = [json.load(open(f)) for f in glob.glob(sys.argv[1] + "/*.json")]
field, themes = sys.argv[2], sys.argv[3:]
kinds = sorted({r["kind"] for r in R})
if not themes:
    for k in kinds:
        print(k, dict(collections.Counter(str(r.get(field, "")).strip().lower() for r in R if r["kind"] == k)))
for t in themes:
    label, words = t.split("=", 1); ws = words.lower().split("|")
    row = {k: sum(any(w in str(r.get(field, "")).lower() for w in ws) for r in R if r["kind"] == k) for k in kinds}
    n = {k: sum(r["kind"] == k for r in R) for k in kinds}
    print(f"{label:25}", "  ".join(f"{k}: {row[k]}/{n[k]}" for k in kinds))
