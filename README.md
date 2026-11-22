# ssr-panel

A Claude Code skill that runs a synthetic buyer panel on a web page, an offer or a copy variant.

Claude role-plays the buyers you define and writes a free-text reaction to the page. A local embedding model maps each reaction onto a 1–5 purchase-intent scale with **Semantic Similarity Rating (SSR)**. Each reaction also returns the buyer's main objection, the event that would make them buy this month, and a one-line restatement of the offer. Those are often more useful than the score.

Use it to compare two versions of a page, to find objections before shipping copy, or to check whether readers can tell what you sell.

## Method and sources

The scoring follows Maier et al. (2025). They found that asking an LLM for a 1–5 rating directly gives narrow, skewed distributions. Having it answer in free text and projecting that text onto five anchor statements by embedding cosine similarity reproduced human purchase-intent distributions. Across 57 personal-care product surveys with 9,300 human responses, SSR reached 90% of human test-retest reliability.

- Maier, B. F., Aslak, U., Fiaschi, L., Rismal, N., Fletcher, K., Luhmann, C. C., Dow, R., Pappas, K., & Wiecki, T. V. (2025). *LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings.* arXiv:2510.08338. https://arxiv.org/abs/2510.08338
- Embeddings: [`sentence-transformers/all-mpnet-base-v2`](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) (Apache-2.0), via the Sentence-Transformers library: Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.* EMNLP 2019. https://arxiv.org/abs/1908.10084

**Where this differs from the paper:**
- The three anchor sets in `scripts/score.py` are new. They are worded for hiring a firm or buying a product, not taken from the paper.
- The paper's own SSR implementation is not used. `score.py` is a short reimplementation of the same idea: subtract the minimum similarity, normalise to a distribution, average the anchor sets, take the expected value.
- The paper validated SSR on consumer goods. Using it for B2B services and web pages, as this skill does, is not validated. Treat the score as a structured comparison, and the objections and triggers as the main output.

## Install

```bash
git clone https://github.com/yoelf22/ssr-panel ~/.claude/skills/ssr-panel
python3 -m venv ~/.cache/ssr-venv && ~/.cache/ssr-venv/bin/pip install sentence-transformers
```

It needs the [Claude Code](https://claude.com/claude-code) CLI (`claude -p`) for the reactions. Scoring runs locally; the embedding model downloads on first use.

## Use

In Claude Code, say "run a synthetic panel on <url>" or "ask the panel". `SKILL.md` holds the full workflow:
1. Confirm who the buyers are.
2. Build the personas.
3. Extract the page text.
4. Run the reactions.
5. Score them.
6. Tally the themes.
7. Report.

The scripts also work without Claude Code's skill loader:

```bash
S=~/.claude/skills/ssr-panel/scripts
python3 $S/page2text.py https://example.com pageA.txt
python3 $S/mkjobs.py personas.json jobs.json pageA --samples 2 --extra examples/extra.example.json
seq 0 7 | xargs -P 8 -I{} python3 $S/react.py {} jobs.json out
~/.cache/ssr-venv/bin/python $S/score.py out scored.json
python3 $S/tally.py out objection 'price=price|budget' 'proof=no evidence|no proof'
```

| Script | Does |
|---|---|
| `page2text.py` | URL or HTML file → plain text, from the first `<h1>` to the `<footer>` |
| `mkjobs.py` | personas × pages × samples → `jobs.json`, with optional extra questions |
| `react.py` | one in-character reaction as JSON; skips finished jobs so reruns resume |
| `score.py` | SSR scores per reaction and a summary per page × segment |
| `tally.py` | theme counts or categorical answers per segment |

## Reading the results

- Scores bunch up between about 3.2 and 3.8. Treat gaps under about 0.2 as noise.
- Personas overweight a missing price and missing proof in their own sector. `SKILL.md` lists the known biases.
- This is not a demand forecast. Real buyer conversations and live A/B tests outrank it.

## License

MIT. See `LICENSE`. The cited paper and model keep their own licenses.
