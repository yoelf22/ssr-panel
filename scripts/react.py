#!/usr/bin/env python3
"""Run ONE synthetic-buyer reaction. Usage: react.py <job_index> <jobs.json> <outdir>
Each job: {"persona": {"id","kind","text"[, "grounding"]}, "concept": "<name>", "sample": n,
           "mode": "page"|"concept", "extra": {"key": "instruction", ...}}
The stimulus is read from <dir of jobs.json>/<concept>.txt.
mode "page" (default): the persona reads a web page or pitch from a company.
mode "concept": the persona hears a product idea that does not exist yet.
Skips jobs already done, so a rerun resumes."""
import json, sys, subprocess, os
i, J, O = int(sys.argv[1]), sys.argv[2], sys.argv[3]
j = json.load(open(J))[i]
out = f"{O}/{i}.json"
if os.path.exists(out): sys.exit()
os.makedirs(O, exist_ok=True)
stim = open(os.path.join(os.path.dirname(os.path.abspath(J)), j["concept"] + ".txt")).read()
p = j["persona"]
who = p["text"] + (f"\nWhat you know from your own experience: {p['grounding']}" if p.get("grounding") else "")
extra = "".join(f'\n"{k}": {v}' for k, v in j.get("extra", {}).items())

if j.get("mode", "page") == "concept":
    prompt = f"""{who}
Stay fully in this role. Someone describes a product idea to you. It does not exist yet; judge it as an idea.

<idea>
{stim}
</idea>

Reply ONLY with a JSON object, no code fence, with these keys:
"reaction": 3-5 sentences in your own first-person voice, as you'd say it to a colleague, on whether you would use and pay for this in the next 12 months if it existed, and why. Be candid and specific to your situation; do not give a number.
"restate": one sentence: what you think the product does, and for whom.
"today": one or two sentences: what you do about this problem today, and what it costs you.
"objection": your single biggest reason not to buy or use it.
"must_be_true": what would have to be true for you to pay for it.
"who_else": who else in your organisation or household would have to agree, or "nobody".
"trigger": the specific event or condition that would make you look for something like this this month.{extra}"""
else:
    prompt = f"""{who}
Stay fully in this role. You are seeing the following page for the first time.

<page>
{stim}
</page>

Reply ONLY with a JSON object, no code fence, with these keys:
"reaction": 3-5 sentences in your own first-person voice, as you'd say it to a colleague, on whether you would contact and pay this company in the next 12 months and why. Be candid and specific to your situation; do not give a number.
"restate": one sentence: what exactly you would get from them and for what kind of customer.
"objection": your single biggest reason not to buy.
"trigger": the specific event or condition that would make you contact them this month.{extra}"""

model = os.environ.get("SSR_MODEL", "sonnet")
d = None
for _ in range(3):
    r = subprocess.run(["claude", "-p", "--model", model, prompt], capture_output=True, text=True, timeout=300, cwd="/tmp")
    t = r.stdout.strip(); t = t[t.find("{"):t.rfind("}") + 1]
    try:
        d = json.loads(t); break
    except Exception:
        pass
if d is None: sys.exit(f"job {i}: no JSON after 3 tries")
d.update(id=p["id"], kind=p["kind"], concept=j["concept"], sample=j["sample"], mode=j.get("mode", "page"))
json.dump(d, open(out, "w"))
