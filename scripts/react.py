#!/usr/bin/env python3
"""Run ONE synthetic-buyer reaction. Usage: react.py <job_index> <jobs.json> <outdir>
Each job: {"persona": {"id","kind","text"}, "concept": "<name>", "sample": n}
The stimulus is read from <dir of jobs.json>/<concept>.txt.
Optional job/top-level key "extra": {"key": "instruction", ...} adds answer fields.
Skips jobs already done, so a rerun resumes."""
import json, sys, subprocess, os
i, J, O = int(sys.argv[1]), sys.argv[2], sys.argv[3]
jobs = json.load(open(J)); j = jobs[i]
out = f"{O}/{i}.json"
if os.path.exists(out): sys.exit()
os.makedirs(O, exist_ok=True)
stim = open(os.path.join(os.path.dirname(os.path.abspath(J)), j["concept"] + ".txt")).read()
extra = j.get("extra", {})
extra_lines = "".join(f'\n"{k}": {v}' for k, v in extra.items())
prompt = f"""{j['persona']['text']}
Stay fully in this role. You are seeing the following web page for the first time.

<page>
{stim}
</page>

Reply ONLY with a JSON object, no code fence, with these keys:
"reaction": 3-5 sentences in your own first-person voice, as you'd say it to a colleague, on whether you would contact and pay this company in the next 12 months and why. Be candid and specific to your situation; do not give a number.
"restate": one sentence: what exactly you would get from them and for what kind of customer.
"objection": your single biggest reason not to buy.
"trigger": the specific event or condition that would make you contact them this month.{extra_lines}"""
model = os.environ.get("SSR_MODEL", "sonnet")
for attempt in range(3):
    r = subprocess.run(["claude", "-p", "--model", model, prompt], capture_output=True, text=True, timeout=300, cwd="/tmp")
    t = r.stdout.strip(); t = t[t.find("{"):t.rfind("}") + 1]
    try:
        d = json.loads(t); break
    except Exception:
        d = None
if d is None: sys.exit(f"job {i}: no JSON after 3 tries")
d.update(id=j["persona"]["id"], kind=j["persona"]["kind"], concept=j["concept"], sample=j["sample"])
json.dump(d, open(out, "w"))
