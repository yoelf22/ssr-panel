#!/usr/bin/env python3
"""Delete a run's confidential inputs once you have the report.
Usage: purge.py <run_folder> [--all] [--yes]
Default: deletes the files that describe the idea or real people (stimulus .txt files,
evidence, assumptions, personas, jobs). --all also deletes reactions (out*/), scores and
any interview guide. Lists the files and asks before deleting unless --yes."""
import sys, glob, os, shutil
if len(sys.argv) < 2: sys.exit(__doc__)
d = sys.argv[1]; every = "--all" in sys.argv; yes = "--yes" in sys.argv
pats = ["*.txt", "evidence*.json", "assumptions*.json", "personas*.json", "jobs*.json", "extra*.json"]
if every: pats += ["out*", "scored*.json", "interview-guide.md", "README.md"]
hits = sorted({p for pat in pats for p in glob.glob(os.path.join(d, pat))})
if not hits: sys.exit("nothing to delete")
print("\n".join(hits))
if not yes and input(f"Delete these {len(hits)} items? [y/N] ").strip().lower() != "y": sys.exit("kept")
for p in hits: shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
print(f"deleted {len(hits)} items")
