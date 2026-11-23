# ssr-panel

A Claude Code skill that runs a synthetic buyer panel on a product idea, a concept, a web page or a copy variant. It works conversationally: from a paragraph and a hunch at the idea stage, to a finished page.

Claude role-plays the buyers you define and writes a free-text reaction to the page. A local embedding model maps each reaction onto a 1–5 purchase-intent scale with **Semantic Similarity Rating (SSR)**. Each reaction also returns the buyer's main objection, the event that would make them buy this month, and a one-line restatement of the offer. Those are often more useful than the score.

Use it to:
- **At the idea stage:** test a concept before it can be researched, choose which buyer to interview first, find the assumptions most likely to break, and get an interview guide.
- **With a page or pitch:** compare two versions, find objections before shipping copy, or check whether readers can tell what you sell.

## Two modes

**Concept mode**, for ideas that don't exist yet. The skill interviews you, one or two questions at a time, to build a concept brief (`examples/concept-brief.md`):
- the problem and who has it;
- what the product does;
- what people do today instead;
- a rough price;
- anything you've heard from real people;
- the assumptions that would sink it.

Only the buyer-facing paragraph goes to the panel. What you've heard from real people becomes first-hand grounding for the matching personas. Each assumption becomes a yes, no or unsure question.

Each persona answers:
- reaction;
- what they think the product does;
- what they do today;
- their main objection;
- what must be true to pay;
- who else must agree;
- what would make them look for it this month.

**Page mode**, for anything a buyer already reads: landing pages, pitches, service pages. Personas answer: reaction, restatement, objection, trigger.

Either way the skill reports back in conversation. It leads with the decision you named, and offers to revise and rerun, or to write an interview guide built from the assumptions that broke and the recurring objections.

## Method and sources

The scoring follows Maier et al. (2025). They found that asking an LLM for a 1–5 rating directly gives narrow, skewed distributions. Having it answer in free text and projecting that text onto five anchor statements by embedding cosine similarity reproduced human purchase-intent distributions. Across 57 personal-care product surveys with 9,300 human responses, SSR reached 90% of human test-retest reliability.

- Maier, B. F., Aslak, U., Fiaschi, L., Rismal, N., Fletcher, K., Luhmann, C. C., Dow, R., Pappas, K., & Wiecki, T. V. (2025). *LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings.* arXiv:2510.08338. https://arxiv.org/abs/2510.08338
- Embeddings: [`sentence-transformers/all-mpnet-base-v2`](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) (Apache-2.0), via the Sentence-Transformers library: Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.* EMNLP 2019. https://arxiv.org/abs/1908.10084

**Where this differs from the paper:**
- The three anchor sets in `scripts/score.py` are new. They are worded for hiring a firm or buying a product, not taken from the paper.
- The paper's own SSR implementation is not used. `score.py` is a short reimplementation of the same idea: subtract the minimum similarity, normalise to a distribution, average the anchor sets, take the expected value.
- The paper validated SSR on consumer goods. Using it for B2B services and web pages, as this skill does, is not validated. Treat the score as a structured comparison, and the objections and triggers as the main output.

## Confidentiality

Unreleased ideas are sensitive, and for inventors a leak can cost more than embarrassment.

- **Patent confidentiality is the first issue.** In many countries, Europe included, disclosing an invention before filing can destroy its novelty. Whether sending text to an AI provider counts as disclosure is not settled. If you plan to patent, file a priority or provisional application before describing the invention to any outside party or service. This is not legal advice.
- **Purely digital products.** For many software and service ideas, formal IP isn't a realistic option either way, since software and business methods are hard to patent in many jurisdictions. The risk is a competitor learning your approach, and the same rule below protects it.
- **Test the what, never the how.** Buyers judge outcomes, not mechanisms. The skill writes the panel's text in buyer terms (problem, user, outcome, form, price). Before a run, it checks every file and flags anything that shouldn't be disclosed, proposing rewrites:
  - how it works (principle, sensing method, algorithm, formulation);
  - how it is built (circuits, mechanics, materials, architecture, drawings);
  - what makes it better (test data, accuracy figures, the key insight);
  - for digital products, data sources, model or prompt design, and copyable pricing mechanics;
  - real people's identities.
- **Know what leaves your machine.** Before each run the skill states which files go where and waits for a yes.

  | Backend | Reactions generated by | What leaves the machine |
  |---|---|---|
  | `claude` (default) | Claude via `claude -p` | The panel text, personas, evidence and assumptions, in every call, under your Claude plan's data terms |
  | `ollama` (`SSR_BACKEND=ollama`) | A local model via [Ollama](https://ollama.com) | Nothing |

  Scoring always runs locally.
- **Keep files out of repos.** Runs live in a codenamed folder outside any git repository (default `~/ssr-runs/<codename>/`). `mkjobs.py` warns if the folder is inside one, and `.gitignore` excludes run inputs.
- **Anonymize evidence.** Names, emails and company names in your notes are replaced with roles before they reach any persona.
- **Clean up.** `purge.py <run_folder>` deletes the inputs after the report, and `--all` deletes the outputs too.

## Install

```bash
git clone https://github.com/yoelf22/ssr-panel ~/.claude/skills/ssr-panel
python3 -m venv ~/.cache/ssr-venv && ~/.cache/ssr-venv/bin/pip install sentence-transformers
```

It needs the [Claude Code](https://claude.com/claude-code) CLI (`claude -p`) for the reactions. Scoring runs locally; the embedding model downloads on first use.

**Fully local option:** install [Ollama](https://ollama.com), pull a model (`ollama pull llama3.1:8b`, or a larger one for better personas), and set `SSR_BACKEND=ollama` (optionally `SSR_OLLAMA_MODEL`, `OLLAMA_HOST`). The Ollama path is tested against a stub of the Ollama API, not yet against a real model.

## Use

In Claude Code, say "I want to test an idea", "run a synthetic panel on <url>" or "ask the panel". `SKILL.md` holds the conversation flow:
1. Work out which phase you're in.
2. Build the concept brief, or extract the page text.
3. Gather what's known, the assumptions and the decision.
4. Define the buyers.
5. Run the reactions.
6. Talk the results through.

The scripts also work without Claude Code's skill loader:

```bash
S=~/.claude/skills/ssr-panel/scripts
python3 $S/page2text.py https://example.com pageA.txt
python3 $S/mkjobs.py personas.json jobs.json pageA --samples 2 --extra examples/extra.example.json
# or, for an idea: concept.txt next to jobs.json
python3 $S/mkjobs.py personas.json jobs.json concept --mode concept \
  --evidence examples/evidence.example.json --assumptions examples/assumptions.example.json
seq 0 7 | xargs -P 8 -I{} python3 $S/react.py {} jobs.json out
~/.cache/ssr-venv/bin/python $S/score.py out scored.json
python3 $S/tally.py out objection 'price=price|budget' 'proof=no evidence|no proof'
python3 $S/tally.py out --assumptions
```

| Script | Does |
|---|---|
| `page2text.py` | URL or HTML file → plain text, from the first `<h1>` to the `<footer>` |
| `mkjobs.py` | personas × stimuli × samples → `jobs.json`; `--mode concept`, `--evidence`, `--assumptions`, `--extra` |
| `react.py` | one in-character reaction as JSON, in page or concept mode; skips finished jobs so reruns resume |
| `score.py` | SSR scores per reaction and a summary per page × segment |
| `tally.py` | per segment: theme counts, categorical answers, or yes/no/unsure per assumption |
| `purge.py` | deletes a run's confidential inputs (and with `--all`, its outputs) after confirming |

## Reading the results

- Scores bunch up between about 3.2 and 3.8. Treat gaps under about 0.2 as noise.
- Personas overweight a missing price and missing proof in their own sector. `SKILL.md` lists the known biases.
- This is not a demand forecast. Real buyer conversations and live A/B tests outrank it.

## License

MIT. See `LICENSE`. The cited paper and model keep their own licenses.
