---
name: ssr-panel
description: Run a synthetic buyer panel on a product idea, a concept, a web page or a copy variant, using Semantic Similarity Rating (SSR): Claude role-plays the buyers you describe, writes free-text reactions, and a local embedding model maps them onto a 1-5 purchase-intent scale. Works conversationally from the earliest idea stage (a paragraph and a hunch) through to finished pages. Use when the user asks to "test an idea", "test acceptance", "ask the panel", "run a synthetic panel", "SSR", "how would buyers react", "who should I interview first", or wants to compare two versions before building or shipping.
---

# SSR synthetic buyer panel

Method from Maier et al. (2025), "LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings" (arXiv:2510.08338): asking an LLM for a 1-5 number gives a narrow, skewed answer, but asking for a free-text reaction and mapping it onto anchor statements by embedding similarity reproduces human Likert distributions much better. The anchor statements in `scripts/score.py` are this skill's own, worded for buying a service or product; they are not the paper's.

One run = personas x stimuli x samples. Each reaction also yields an objection, a buying trigger and a restatement, which are usually worth more than the score.

## How to run this skill: a conversation, not a form

Work with the user in short turns. Ask one or two questions at a time, reflect back what you heard in a sentence, and move on. Use their words in the files you write. Don't ask for something you can infer from what they already said; propose it and let them correct it. Before any run, show a one-screen summary of what the panel will read and who will read it, and get a yes.

## Step 0. Which phase are they in?

Ask what they have. The answer picks the mode:

- **Idea stage** ("I have an idea / a technology / a sketch", nothing a buyer reads yet) → **concept mode**. Go to Step 1.
- **Something written for buyers** (a landing page, pitch, deck text, service page) → **page mode**. Skip to Step 4.

If unsure, ask: "Does a buyer read this today, or is it still in your head and your notes?"

## Step 0.5. Confidentiality, before anything is written down

Inventors and early founders are rightly protective of unreleased ideas. Settle this first, briefly and without alarm:

1. **Patents.** If the idea may be patentable, say: "If you plan to patent this, file a priority or provisional application before you describe it to anyone outside your control: people or online services. In many countries, Europe included, disclosure before filing can destroy novelty. Whether sending text to an AI provider counts as disclosure is not settled; I'm not giving legal advice, so check with a patent attorney." Then continue only in the way they choose.
2. **Where the reactions are generated.** Explain the choice:
   - **Claude (default):** best persona quality. Everything the panel reads, the personas and any evidence go to Anthropic in every reaction call, under the data terms of the user's Claude plan. Ask them to check their plan's data settings if this matters.
   - **Local (`SSR_BACKEND=ollama`):** nothing leaves the machine. Needs Ollama and a downloaded model; personas are less realistic with small models.
   Scoring always runs locally either way.
3. **A codename and a safe folder.** Ask for a codename and use it in folder and file names. Create the run folder outside any git repository, default `~/ssr-runs/<codename>/`. `mkjobs.py` warns if the folder is inside a repo; treat that warning as a stop.

## Step 1. Concept mode: build the concept brief together

Walk through `examples/concept-brief.md` conversationally, roughly in this order. Accept "don't know"; note it as an open question rather than inventing an answer.

1. "Tell me the idea the way you'd tell a friend." Then draw out: the problem and the moment it happens, who has it (a person, not a market), what the product does, how and where it's used, what changes for them.
2. "What do people do about this today?" The status quo is what every persona compares against. If the answer is "nothing", ask what that costs them.
3. "Any rough idea of price or who pays?" A guess is fine; say it will be tested, not held against them.
4. "Is there more than one version of the idea, or more than one way to pitch it?" Each becomes a separate stimulus.

Then write `concept.txt` (one file per version; see `examples/concept.example.txt`): a short plain paragraph covering problem, who, what it does, how it's used, what changes, rough price. **Only what a buyer would be told**: no assumptions, no evidence, no internal doubts. Read it back and ask "is that how you'd describe it?"

**Test the what, never the how.** Buyers judge outcomes, not mechanisms. Describe the problem, the user, the outcome, the form and the price, and leave out how it works: sensing method, materials, algorithms, circuits, chemistry, architecture, part numbers, test data. A buyer doesn't need "60 GHz radar with a micro-Doppler classifier"; "detects a fall without a camera or a wearable" is enough, and the mechanism is what a patent protects.

## Step 2. Concept mode: what is actually known

Ask for real-world input, however thin. It is what keeps the panel from being pure model guesswork:

- "Have you spoken to anyone who has this problem? What did they say or do?" Quotes, observations, reviews of similar products, forum posts, a support inbox.
- **Ask for files explicitly:** "If you have interview notes, call transcripts, survey exports, reviews or a deck, give me the file paths and I'll pull out what's relevant." Read them, then summarise per segment; don't paste whole documents into the evidence.
- **Anonymise as you summarise.** Replace names, emails, phone numbers and company names with roles and descriptions ("a night manager at a 60-bed home"). Real people's details never go into the evidence, whichever backend is used.
- Put it in `evidence.json`, keyed by segment (see `examples/evidence.example.json`). `mkjobs.py --evidence` adds it to those personas as first-hand experience.
- If there is none, say so plainly in the report: the panel then reflects general model knowledge only.

## Step 3. Concept mode: the risky assumptions and the decision

- "What would have to be true for this to work? Which of those worries you most?" Collect 3-5 into `assumptions.json` (see `examples/assumptions.example.json`), each a plain statement a buyer could agree or disagree with ("The home, not the family, would pay").
- "What decision should this panel help you make?" (which segment to interview first, which version to pursue, whether to keep going). Keep it; the report answers it.

## Step 4. The buyers

Ask who might buy or use it, then propose segments and let the user correct them. Ask who is explicitly not a target. For each segment write about 8-12 personas in `personas.json` (see `examples/personas.example.json`): one concrete sentence each with role, organisation size, location, money situation and a current problem. Vary situations inside a segment. `kind` is the segment label, and must match the keys in `evidence.json`.

At the idea stage, include at least one segment the user is unsure about; the panel is cheap and a surprise here is the most useful result. If a version or offer has no natural buyer on the panel, add one, or a zero will mean nothing.

## Step 5. Run

Setup (once): `python3 -m venv ~/.cache/ssr-venv && ~/.cache/ssr-venv/bin/pip install sentence-transformers`

```bash
S=<this skill's folder>/scripts
# page mode only: turn a URL or HTML file into text (check the first lines include the hero)
python3 $S/page2text.py https://example.com page.txt
# build jobs (concept mode shown; page mode: --mode page, no --evidence/--assumptions needed)
python3 $S/mkjobs.py personas.json jobs.json concept --mode concept --samples 2 \
  --evidence evidence.json --assumptions assumptions.json [--extra extra.json]
# run reactions, 8 in parallel (react.py skips finished jobs, so reruns resume)
N=$(python3 -c "import json;print(len(json.load(open('jobs.json'))))")
seq 0 $((N-1)) | xargs -P 8 -I{} python3 $S/react.py {} jobs.json out
# score
~/.cache/ssr-venv/bin/python $S/score.py out scored.json
```

**Before running, do a disclosure check and get a yes.**
1. Re-read every file the panel will see: the stimulus texts, `evidence.json`, `assumptions.json`, `personas.json`. Flag anything that reveals how the invention works or identifies a real person, quote the line, and propose a buyer-terms rewrite. Change nothing without the user's agreement.
2. Show a short summary: which files, how many reactions, which backend, and in one line what leaves the machine. For example: "4 files go to Anthropic in 48 calls; the scoring stays on this machine." Or, with Ollama: "Nothing leaves this machine."
3. Run only after an explicit yes.

- `SSR_BACKEND=ollama` (with optional `SSR_OLLAMA_MODEL`, `OLLAMA_HOST`) runs the reactions on a local model.
- **Concept mode** asks each persona for: reaction, restatement, what they do today, objection, what must be true to pay, who else must agree, trigger, plus a yes/no/unsure answer with a reason per assumption.
- **Page mode** asks for reaction, restatement, objection and trigger.
- `--extra` adds your own questions in either mode (see `examples/extra.example.json`).

## Step 6. Read it, then talk it through

Tally first, then read the actual answers: keyword counts miss phrasings.

```bash
python3 $S/tally.py out --assumptions          # yes / no / unsure per assumption and segment
python3 $S/tally.py out first_buy              # any categorical extra question
python3 $S/tally.py out objection 'price=price|cost|budget' 'trust=trust|proof|evidence'
```

Report conversationally, leading with the answer to the user's decision:

1. **The decision**: which segment leaned in, which version read best, or whether the idea drew polite indifference everywhere.
2. **Did they understand it?** Compare restatements with the user's intent; quote one that missed.
3. **The status quo** (concept mode): what personas do today, and whether the idea beats it in their eyes.
4. **The assumptions**: which held, which broke, by segment, with one quoted reason each.
5. **Who else must agree** (concept mode): the people a real sale would have to reach.
6. **Objections and triggers**, with 1-2 persona quotes.
7. **Scores** last, with the caveats below.

Then ask what they want next:
- **Revise and rerun**: change the text where it was misread, same personas, same samples, and compare.
- **Write an interview guide** (`interview-guide.md`): who to recruit (the segment and situation that leaned in, found through its trigger), then one question per broken or uncertain assumption and per recurring objection, asked about past behaviour ("Walk me through the last time…"), never "would you buy".
- **Stop here**: say what the panel cannot tell them and what the first real conversation should test.

Keep a `README.md` in the run folder: one entry per run with the stimulus, files, scores and the 3-4 findings.

**When the user is done**, offer to clear the confidential inputs: `python3 $S/purge.py <run_folder>` deletes the stimulus, evidence, assumptions, personas and jobs after listing them; `--all` also deletes reactions, scores and the guide. It asks before deleting.

## Reading the numbers

- **Gaps under about 0.2 on the 1-5 scale are noise.** Scores bunch between about 3.2 and 3.8. Say "tie" plainly.
- A wording change can fix a misreading or an objection without moving intent. Report that as the result.

## Known biases (say them when they matter)

- **No ground truth.** Unless `evidence.json` holds real input, personas know only what the model knows. Scores are not calibrated against the user's market; use them to compare versions on the same panel.
- **Price:** personas ask for a price more often than real buyers do.
- **Proof in my exact sector:** every persona notices examples are not from its own field.
- **Generalist doubt:** "one person / small team" objections usually travel with missing domain proof.
- **The panel only contains the buyers you wrote.** A buyer nobody imagined cannot appear.
- **Validity:** SSR was validated on 57 personal-care product surveys (9,300 human responses). For new concepts, B2B and services, treat the panel as a structured way to surface misreadings, objections, triggers and assumptions to test, not as a demand forecast. Real conversations and observation outrank it.

## Don'ts

- Don't run before the user has confirmed the stimulus text and the segments.
- Don't put assumptions or evidence in the text the panel reads.
- Don't put mechanisms, technical detail or real people's identities in anything the panel reads.
- Don't create run files inside a git repository.
- Don't present a 0.05 difference as a win.
- Don't write personas that name real people or companies as if they were customers.
