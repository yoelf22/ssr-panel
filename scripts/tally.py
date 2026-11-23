#!/usr/bin/env python3
"""Count answers per persona segment.
  tally.py <outdir> <field>                      categorical: counts each distinct answer
  tally.py <outdir> <field> --first              counts the first word only (yes / no / unsure)
  tally.py <outdir> <field> 'label=w1|w2' ...    theme counts: answers containing any of the words
  tally.py <outdir> --assumptions                yes/no/unsure for every a1, a2, ... field"""
import sys, json, glob, re, collections
R = [json.load(open(f)) for f in glob.glob(sys.argv[1] + "/*.json")]
kinds = sorted({r["kind"] for r in R})
first = lambda v: re.sub(r"[^a-z]", "", str(v).strip().lower().split()[0]) if str(v).strip() else ""
def cat(field, fn):
    for k in kinds:
        print(f"  {k:22}", dict(collections.Counter(fn(r.get(field, "")) for r in R if r["kind"] == k)))
args = sys.argv[2:]
if args == ["--assumptions"]:
    for f in sorted({k for r in R for k in r if re.fullmatch(r"a\d+", k)}, key=lambda x: int(x[1:])):
        print(f); cat(f, first)
    sys.exit()
field, rest = args[0], args[1:]
if not rest: cat(field, lambda v: str(v).strip().lower())
elif rest == ["--first"]: cat(field, first)
else:
    for t in rest:
        label, words = t.split("=", 1); ws = words.lower().split("|")
        row = {k: sum(any(w in str(r.get(field, "")).lower() for w in ws) for r in R if r["kind"] == k) for k in kinds}
        n = {k: sum(r["kind"] == k for r in R) for k in kinds}
        print(f"{label:25}", "  ".join(f"{k}: {row[k]}/{n[k]}" for k in kinds))
