---
name: ssr-panel
description: Run a synthetic buyer panel on a web page, offer or copy variant using Semantic Similarity Rating (SSR): Claude role-plays target buyers, writes free-text reactions, and a local embedding model maps them onto a 1-5 purchase-intent scale. Use when the user asks to "test acceptance", "ask the panel", "run a synthetic panel", "SSR", "how would buyers react to this page", compare two page versions, or find objections and buying triggers before shipping copy.
---

# SSR synthetic buyer panel

Method from Maier et al. (2025), "LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings" (arXiv:2510.08338): asking an LLM for a 1-5 number gives a narrow, skewed answer, but asking for a free-text reaction and mapping it onto anchor statements by embedding similarity reproduces human Likert distributions much better. The anchor statements in `scripts/score.py` are this skill's own, worded for buying a service or product; they are not the paper's.

One panel run = personas x stimuli x samples. Each reaction also yields an objection, a buying trigger and a restatement, which are usually worth more than the score.

## Setup (once)

```bash
python3 -m venv ~/.cache/ssr-venv && ~/.cache/ssr-venv/bin/pip install sentence-transformers
```

`react.py` calls `claude -p --model sonnet` (override with `SSR_MODEL`). Scripts are in this skill's `scripts/` folder; refer to them by absolute path. No API key or network access is needed for scoring: the embedding model runs locally.

## 1. Ask before building the panel

Use AskUserQuestion. Don't guess the buyer; a panel of the wrong people produces confident, wrong advice.
- Who buys each offer (segments), and who is explicitly NOT a target.
- Geography and stage/size mix.
- What to measure: purchase intent, objections and triggers, offer clarity ("what is the main offering?"), which offer they'd buy first.

## 2. Build the panel

Write `personas.json` in a run folder (see `examples/personas.example.json`): 8-12 personas per segment, each one concrete sentence with role, company size, location, money situation and a current problem. Vary sector and situation within a segment. `kind` is the segment label used in every tally.

If the page has an offer for a buyer type the panel lacks, add personas for it. A zero for an offer often means "nobody on the panel is that buyer", not "nobody wants it".

## 3. Get the stimulus

Each stimulus is plain text in `<concept>.txt` in the run folder.
- Live or local page: `page2text.py <url|file.html> <concept>.txt`. It keeps from the first `<h1>` to the `<footer>`. **Read the first lines of the output and check the hero is included**: a stimulus that starts a section too late silently drops the hero and audience sections.
- A variant not yet built: copy the text file and edit it. Fine for wording tests; build the real page before the final run.

## 4. Run

```bash
S=~/.claude/skills/ssr-panel/scripts
python3 $S/mkjobs.py personas.json jobs.json pageA pageB --samples 2 [--extra extra.json]
seq 0 $(( $(python3 -c "import json;print(len(json.load(open('jobs.json'))))") - 1 )) | xargs -P 8 -I{} python3 $S/react.py {} jobs.json out
~/.cache/ssr-venv/bin/python $S/score.py out scored.json
```

`--extra` adds answer fields (see `examples/extra.example.json`: main offering, first buy). Two samples per persona per stimulus is the minimum; average them per persona before comparing. `react.py` skips finished jobs, so rerunning resumes.

## 5. Analyse

- Scores: `score.py` prints mean, sd and the average distribution per stimulus x segment. Compare per persona as well as in total; one persona moving 0.4 explains more than the mean.
- Themes: `tally.py out objection 'proof=no evidence|no proof|case' 'price=price|pricing|budget'` counts per segment. `tally.py out first_buy` counts categorical answers. Then **read the actual objections**: keyword counts miss phrasings and miscount (e.g. "no evidence" vs "nothing on the page").
- For an A/B, keep the same personas and samples, change only the stimulus.

## 6. Report

- Lead with the decision-relevant finding, not the table. Give scores, then what moved and why, quoting 1-2 persona lines.
- **Gaps under ~0.2 on the 1-5 scale are noise.** Scores are compressed (most land 3.2-3.8). Say "tie" plainly.
- A copy change can fix an objection without moving intent. Report the objection shift as the result when that happens.
- Keep a `README.md` in the run folder: one entry per run with the stimulus, files, scores and the 3-4 findings.

## Known biases (say them when they matter)

- **Price:** personas are told to weigh spend against their situation, so "no price on the page" is over-represented. For B2B services, buyers who need a price before a call are often not real prospects; don't let this drive the page.
- **Proof in my exact sector:** every persona finds the gap between the page's cases and its own sector. One general page can't close it for every segment; a segment-specific page or outreach can.
- **Generalist doubt:** "one person / small team" objections usually come paired with missing domain proof. Fix the proof, not the team size.
- **Validity:** SSR was validated on 57 personal-care product surveys (9,300 human responses). For B2B and services, treat it as a structured way to surface objections, triggers and clarity problems, not as a demand forecast. Real conversations or a live A/B test outrank it.

## Don'ts

- Don't run without confirming the target segments.
- Don't present a 0.05 difference as a win.
- Don't publish persona text that names real people or companies as if they were customers.
