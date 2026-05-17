# PLAN_v5 — Capability eval against peer-review ground truth

## Status

Drafted 2026-05-17 (post-v4). Not yet executed. This iteration is a
**directional pivot**, not an incremental extension of v1–v4. It
introduces a parallel evaluation pipeline alongside the Petri-based
behavioral audit, not a replacement for it.

## Goal

v1–v4 measured **behavioral failure modes** under adversarial prompts —
whether the target slips into uncritical acceptance, cumulative bias,
late warnings, etc. None of that tells us whether the target can
actually *produce novel scientific contributions* of the kind a real
co-scientist would.

v5 measures the latter, against external ground truth: peer-reviewed
ICLR 2026 OpenReview submissions, where each paper carries a structured
review (novelty/contribution/soundness scores) and an accept/reject
decision the model couldn't have seen during pretraining.

Task: **predict-the-contribution**. Given a paper's introduction +
related work (with the explicit contribution-claim sentence redacted),
the target proposes the paper's main contribution. We score the
proposal against (i) the actual contribution by embedding similarity,
(ii) accept/reject as a coarse novelty proxy, (iii) OpenReview
reviewer novelty/contribution scores as a finer-grained signal.

## Hypotheses

- **H1 (discrimination).** Target model's predicted contributions for
  *accepted* ICLR 2026 papers will have measurably higher
  embedding-similarity to the ground-truth contribution than its
  predictions for *rejected* papers. If true, the eval has signal: the
  model is better at predicting what good-novelty papers do.
- **H2 (contamination magnitude).** Target model's predictions on
  ICLR 2024 papers (pre-cutoff, demonstrably in training) will score
  meaningfully higher than on ICLR 2026 papers (post-cutoff, filtered
  by contamination probe). The delta quantifies how much of any
  predict-the-contribution capability is memorization vs. inference.
  The ICLR 2024 set also serves as the **task-ability floor check**:
  if the target scores low even on contaminated papers, the model is
  bad at the prediction shape itself and the v5 headline number means
  much less. This is why retrofitting predict-contribution onto v3/v4
  seeds wouldn't be a useful sanity check — those seeds don't define
  a verifiable contribution to score against. The 2024 control set is
  the appropriate "is the model generally capable of this task" probe.
- **H3 (proxy validity).** Embedding similarity between predicted and
  actual contributions correlates with mean reviewer novelty score
  on the same paper at ρ ≥ 0.3 (Spearman, on the uncontaminated
  ICLR 2026 subset). If correlation is below this, embedding
  similarity is not a usable proxy and we need an LLM-judge scoring
  pass instead.

## Design

### What changes

- **Task shape.** No auditor/target multi-turn loop. Single-shot:
  prompt → predicted contribution → score. Closer to a benchmark
  than to a behavioral audit.
- **Ground truth.** Replaces LLM-as-judge anchored dimensions with
  external peer-review signal: OpenReview reviewer scores + decisions.
- **New corpus.** ICLR 2026 OpenReview submissions (target ~50–100
  papers after contamination filtering). Plus a matched ICLR 2024
  control set of similar size and field distribution for the
  contamination measurement.
- **New pipeline.** Parallel to the Petri-based eval. Lives under a
  new top-level subdir (`novelty/`) with its own data fetcher, prompt
  builder, scorer, and aggregator. Does **not** retrofit `eval/run_audit.py`.

### What stays fixed

- **Project structure conventions.** plans/ → kb/ → results/iter5/
  pattern carries over.
- **Target model.** Opus 4.5 (`claude-opus-4-5-20251101`) — the
  strongest frontier model whose training cutoff plausibly predates
  the ICLR 2026 submission window (Sept–Oct 2025). Selection
  rationale, since this is the obvious-critique surface:

  | Candidate | Cutoff | ICLR 2026 status |
  |---|---|---|
  | `claude-opus-4-7` | Jan 2026 | Submissions and most reviews predate cutoff — corpus likely contaminated |
  | `claude-opus-4-5-20251101` | ≈ Aug 2025 (released Nov 2025) | Sept–Oct 2025 submissions postdate cutoff — clean |
  | `claude-opus-4-1-20250805` | ≈ early 2025 | Cleanly post-cutoff but weaker capability |
  | `claude-sonnet-4-20250514` | ≈ early 2025 | Cleanly post-cutoff, but Sonnet-tier invites "why not Opus" |

  Picking the strongest model (opus-4-7) re-introduces the exact
  contamination problem v5 was designed to control for. Picking a
  cleaner-cutoff but weaker model invites a capability-ceiling
  critique. opus-4-5 is the best resolution of that tradeoff for the
  ICLR 2026 corpus. Verify the exact cutoff date with Anthropic's
  documentation and the contamination probe filter rate in
  `kb/v5_setup_notes.md` before scaling; if filter rate is anomalously
  high (>50%), fall back to opus-4-1.
- **No Petri.** Petri-based v1–v4 stays as-is. v5 is parallel, not a
  successor.

## Corpus and decontamination

### Source

- **Primary.** ICLR 2026 submissions via the OpenReview API
  (`openreview-py`). Pull metadata, paper PDFs, official reviews,
  meta-reviews, and final decisions.
- **Control.** ICLR 2024 submissions, stratified to match the 2026
  subset on (a) primary area, (b) accept/reject split, (c) abstract
  length quartile.

### Decontamination protocol

For each candidate paper:

1. **Title-only recall probe.** Show target the paper title and ask
   "Are you familiar with this paper? If so, summarize its main
   contribution." Coherent, paper-matching answer → flag contaminated.
2. **Setup-only recall probe.** Show target the abstract's first
   sentence + author list and re-ask. Same scoring.
3. **Score the probe responses** by embedding similarity to the
   actual contribution sentence. Drop if either probe response
   exceeds the calibrated threshold (see below).

Papers passing both probes form the uncontaminated subset. The
*rate* at which papers get filtered is itself a finding — it
estimates leakage of post-cutoff content.

### Threshold calibration (run before the main probe pass)

The cosine threshold is calibrated empirically on a 20-paper
hand-labeled set, not picked from gut:

1. **Build the calibration set.** Sample 10 papers from ICLR 2024
   (expected contaminated) + 10 from ICLR 2026 (expected
   uncontaminated). Stratify on accept/reject and area within each
   year.
2. **Hand-label each as contaminated / uncontaminated.** For each
   paper, manually read the model's probe response and judge: does
   the response describe what the paper actually does, beyond what
   could be inferred from the title alone? Yes → contaminated. Use
   this as the ground-truth label for calibration only.
3. **Sweep the cosine threshold.** Compute the threshold that
   maximizes F1 on the calibration labels (or accuracy if the set
   is balanced). Report the precision/recall tradeoff at the chosen
   threshold so the main run's filter rate is interpretable.
4. **Sanity check.** Expected outcome: most of the 10 ICLR 2024
   papers cross the threshold; most of the 10 ICLR 2026 papers don't.
   If the calibration set doesn't separate cleanly (>3 misclassified
   in either direction), the probes themselves are weak — pause and
   redesign before scaling. Probes might need to ask more specific
   questions (e.g., "what dataset did this paper introduce" rather
   than "summarize the contribution").
5. **Pin the threshold.** Lock the value before running the full
   probe pass. Do NOT retune the threshold after seeing main-run
   results.

The hand-labeled set is also retained as a permanent calibration
artifact so future v5+ runs (different target model, later cutoff)
can re-derive a threshold without redoing the labeling.

### Sample size

Aim for n ≥ 50 uncontaminated ICLR 2026 papers across accept/reject.
The OpenReview pool is ~5K submissions, so even at 90% contamination
filtering there's headroom. n=50 supports detecting an H1 effect of
~0.3 in embedding similarity at α=0.05 power 0.8.

## Scoring

Each paper produces three scores:

1. **Embedding similarity.** Cosine between model's predicted-
   contribution paragraph and the paper's actual contribution sentence
   (extracted by the data pipeline). Encoder:
   `text-embedding-3-large` (OpenAI) for baseline; consider
   `voyage-3-large` as a sensitivity check.
2. **Accept/reject classification accuracy.** Treat embedding
   similarity as a continuous score, sweep a threshold, report AUC
   for predicting acceptance.
3. **Reviewer-novelty correlation.** Mean OpenReview novelty score
   (where the form includes one — ICLR uses "originality" /
   "contribution" / "soundness" 1–4). Spearman vs. similarity score.

Optional fourth: **LLM-judge grading.** Use Opus 4.5 to grade
"how close is the predicted contribution to the actual contribution"
on a 1–9 scale (anchored). Cross-check against embedding similarity.
Only worth running if H3 falsifies and embedding similarity proves
to be a bad proxy.

## Pipeline / concrete next steps

1. **`novelty/fetch_openreview.py`** — script to pull ICLR 2026 + 2024
   submissions, reviews, decisions. Write to `data/iclr2026.jsonl`
   and `data/iclr2024.jsonl` with one row per paper.
2. **`novelty/parse_pdfs.py`** — extract per paper: title, abstract,
   introduction, related-work section, contribution sentence,
   author list. Use `pdfplumber` or `unstructured`. Output augments
   the JSONL with section-segmented text.
3. **`novelty/contamination_probe.py`** — run both probes on each
   paper, score, write contamination flags back to JSONL. First runs
   the calibration set + manual labeling step (writes
   `data/contamination_calibration.jsonl` and a pinned threshold to
   `data/contamination_threshold.json`); then the main probe pass
   reads that threshold.
4. **`novelty/predict_contribution.py`** — for each uncontaminated
   paper, build the prompt (intro + related-work with contribution
   sentence redacted), call the target model, write the
   predicted-contribution to `outputs/iter5/predictions.jsonl`.
5. **`novelty/score.py`** — compute embedding similarity, AUC vs.
   accept/reject, Spearman vs. reviewer scores. Write to
   `results/iter5/scores.jsonl` and a summary stats JSON.
6. **`novelty/control_run.sh`** — run steps 3–5 on ICLR 2024 too.
   Produce side-by-side comparison.
7. **Write `kb/v5_findings.md`** — H1/H2/H3 verdicts with confidence
   intervals, decontamination filter rate, examples of good/bad
   predictions, comparison with v1–v4 (different question, but the
   joint picture is the point of the project).

## Success criteria

- ≥50 uncontaminated ICLR 2026 papers after filtering, both accept
  and reject represented.
- H1, H2, H3 each resolve to "confirmed", "falsified", or
  "underpowered" with reported effect sizes, not a binary p-value.
- The contamination filter rate is itself reported as a finding —
  the project learns something either way (high rate = leakage
  concern for current models; low rate = clean eval surface).
- The pipeline runs end-to-end reproducibly from a fresh OpenReview
  pull.

## What this iteration is NOT

- **Not a behavioral audit.** No adversarial seeds, no multi-turn
  steering. v1–v4 keep doing that job.
- **Not a benchmark in the leaderboard sense.** The aim is to measure
  capability under verifiable decontamination, not to compare models.
  Single-model run; multi-model comes if v5 is informative.
- **Not a novelty oracle.** Peer-review novelty scores are noisy
  (inter-reviewer r ≈ 0.2–0.3). v5 uses them as a coarse, aggregated
  signal — not a ground-truth label.
- **Not validated against human-rated predictions.** The same standing
  gap from `kb/methodology_critique.md` applies here: a human-rater
  pass on a 20-paper subset would dramatically increase confidence,
  but is left as v6 follow-up.

## If results don't match predictions

- **If H1 falsifies (no discrimination accept vs. reject).** Either
  the task is too hard (model can't predict contributions of strong
  papers any better than weak ones — interesting!) or the embedding
  similarity metric is too coarse (try the LLM-judge alternative).
- **If H2 doesn't show a contamination effect.** Could mean the
  control set really is in pretraining and the post-cutoff set
  surprisingly isn't, OR the model is bad enough at this task that
  memorization doesn't help. Falsifies the assumption that
  predict-contribution is leak-dependent.
- **If H3 falsifies (no correlation with reviewer novelty).** Embedding
  similarity isn't measuring novelty as humans see it. Pivot to
  LLM-as-judge scoring; treat embedding as a sanity check only.
- **If the contamination probe filters >95% of papers.** Pretraining
  leaks more recent content than expected; the eval surface is
  smaller than planned. Consider switching to an even-more-recent
  source (arXiv preprints from the last 30 days) and accept the
  loss of structured peer-review scores.

## Open design questions (resolve before executing)

- **Section extraction reliability.** OpenReview PDFs aren't
  uniformly structured. Need to validate the parser on ~10 papers
  manually before scaling.
- **Contribution-sentence extraction.** "We propose X" sentences are
  not always present or are spread across multiple sentences. Decide
  whether to use the first paragraph of the conclusion as a
  fallback, or to have the LLM extract the contribution from the
  full paper as a preprocessing step.
- **Reviewer novelty score availability.** ICLR's review form has
  evolved year-to-year. Confirm 2026 reviews include a usable
  novelty/originality field; if not, fall back to overall
  recommendation score.
- **Cost.** ~50 papers × probe + prediction calls × embeddings ≈
  cheap on Anthropic API; OpenReview API has rate limits. Should not
  exceed a few hours of wall time.
- **Opus 4.5 cutoff verification.** Anthropic's documented cutoff for
  opus-4-5-20251101 should be confirmed before running. If it turns
  out to extend past Sept 2025 (and we discover this via
  high probe filter rate), the fallback is opus-4-1-20250805.
