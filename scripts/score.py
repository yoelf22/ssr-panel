#!/usr/bin/env python3
"""Semantic Similarity Rating: map each free-text reaction onto a 1-5 purchase-intent
scale by cosine similarity to three sets of five anchor statements, then average.
Usage: score.py <outdir> <scored.json>   (needs sentence-transformers)"""
import sys, json, glob, collections, numpy as np
from sentence_transformers import SentenceTransformer
m = SentenceTransformer("all-mpnet-base-v2")
ANCHORS = [
    ["I would definitely not buy from this company.", "I probably would not buy from this company.", "I might or might not buy from this company.", "I would probably buy from this company.", "I would definitely buy from this company."],
    ["There is no chance I'd contact or pay them.", "It's unlikely I'd engage them.", "I'm unsure whether I'd engage them; it could go either way.", "It's likely I'd engage them soon.", "I'm ready to sign with them now."],
    ["Not for us, I'd pass.", "Interesting, but I doubt we'd spend money on it.", "Maybe, I'd need to know more before deciding.", "This looks like a good fit and I'd likely buy.", "This is exactly what we need, I'd buy it."],
]
E = [m.encode(a, normalize_embeddings=True) for a in ANCHORS]
R = [json.load(open(f)) for f in glob.glob(sys.argv[1] + "/*.json")]
X = m.encode([r["reaction"] for r in R], normalize_embeddings=True)
for r, x in zip(R, X):
    ps = []
    for e in E:
        s = e @ x; p = s - s.min(); p = p / p.sum(); ps.append(p)
    p = np.mean(ps, 0); r["pmf"] = p.round(3).tolist(); r["score"] = float(p @ np.arange(1, 6))
json.dump(R, open(sys.argv[2], "w"), indent=1)
g = collections.defaultdict(list)
for r in R: g[(r["concept"], r["kind"])].append(r)
for (c, k), v in sorted(g.items()):
    sc = [r["score"] for r in v]; pm = np.mean([r["pmf"] for r in v], 0)
    print(f"{c:30} {k:20} n={len(v):3} mean={np.mean(sc):.2f} sd={np.std(sc):.2f} pmf={pm.round(2).tolist()}")
