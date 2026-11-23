#!/usr/bin/env python3
"""Build jobs.json = personas x stimuli x samples.
Usage: mkjobs.py <personas.json> <jobs.json> <stimulus> [stimulus ...]
         [--samples 2] [--mode page|concept] [--extra extra.json]
         [--evidence evidence.json] [--assumptions assumptions.json]
personas.json: [{"id": "A1", "kind": "segment", "text": "You are ..."}, ...]
evidence.json: {"segment": "what real people in this segment have said or done", ...}
  -> added to every persona of that segment as first-hand grounding.
assumptions.json: ["Care homes have a budget line for fall response.", ...]
  -> each becomes a question a1, a2, ... answered "yes", "no" or "unsure" plus a reason.
Each stimulus name must have a matching <stimulus>.txt next to jobs.json."""
import json, argparse, os, subprocess
ap = argparse.ArgumentParser()
ap.add_argument("personas"); ap.add_argument("jobs"); ap.add_argument("stimuli", nargs="+")
ap.add_argument("--samples", type=int, default=2); ap.add_argument("--mode", default="page", choices=["page", "concept"])
ap.add_argument("--extra"); ap.add_argument("--evidence"); ap.add_argument("--assumptions")
a = ap.parse_args()
P = json.load(open(a.personas))
extra = json.load(open(a.extra)) if a.extra else {}
if a.evidence:
    ev = json.load(open(a.evidence))
    for p in P:
        if ev.get(p["kind"]): p["grounding"] = ev[p["kind"]]
if a.assumptions:
    for n, s in enumerate(json.load(open(a.assumptions)), 1):
        extra[f"a{n}"] = f'is this true for you: "{s}"? Start with exactly one word, yes, no or unsure, then one sentence why.'
jobs = [dict(persona=p, concept=c, sample=s, mode=a.mode, **({"extra": extra} if extra else {}))
        for p in P for c in a.stimuli for s in range(1, a.samples + 1)]
json.dump(jobs, open(a.jobs, "w"), indent=1)
print(f"{len(jobs)} jobs: {len(P)} personas x {len(a.stimuli)} stimuli x {a.samples} samples, mode={a.mode}"
      + (f", {len([k for k in extra if k.startswith('a') and k[1:].isdigit()])} assumptions" if a.assumptions else ""))
# Confidentiality guard: an idea's files should not sit inside a git repository.
d = os.path.dirname(os.path.abspath(a.jobs))
inside = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
if inside.returncode == 0:
    print(f"WARNING: {d} is inside the git repository {inside.stdout.strip()}. Concept, evidence and "
          "persona files could be committed and pushed. Use a folder outside any repo, e.g. ~/ssr-runs/<codename>/.")
