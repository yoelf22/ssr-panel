#!/usr/bin/env python3
"""Build jobs.json = personas x concepts x samples.
Usage: mkjobs.py <personas.json> <jobs.json> <concept> [concept ...] [--samples 2] [--extra extra.json]
personas.json: [{"id": "A1", "kind": "segment-name", "text": "You are ..."}, ...]
Each concept name must have a matching <concept>.txt next to jobs.json."""
import json, sys, argparse
ap = argparse.ArgumentParser()
ap.add_argument("personas"); ap.add_argument("jobs"); ap.add_argument("concepts", nargs="+")
ap.add_argument("--samples", type=int, default=2); ap.add_argument("--extra")
a = ap.parse_args()
P = json.load(open(a.personas)); extra = json.load(open(a.extra)) if a.extra else {}
jobs = [dict(persona=p, concept=c, sample=s, **({"extra": extra} if extra else {}))
        for p in P for c in a.concepts for s in range(1, a.samples + 1)]
json.dump(jobs, open(a.jobs, "w"), indent=1)
print(f"{len(jobs)} jobs: {len(P)} personas x {len(a.concepts)} concepts x {a.samples} samples")
