# REFACTOR.md — From ra-audit-petri to a formal research project

## Goal

Convert the current single-script Petri evaluation into a research project that can support a sustained investigation of how LLMs behave as **co-scientists** — collaborators on research tasks where subtle failures (deference, narrative steering, cumulative bias, unverified claim acceptance) matter more than overt refusal failures.

The model is the `linguistic_degradation/` project, which has the scaffolding of a real research effort: versioned plan docs, a knowledge base, modular code, central config, an analysis layer, a report directory with a compileable preprint, and pinned dependencies.

---

## Decisions (locked)

- **[D1] Scope: Reframe + add seeds.** Project rebrands as an "AI co-scientist behavior evaluation." Existing 10 seeds remain (they cover most of the research-assistant surface); new seeds expand coverage to: hypothesis generation, experiment design critique, paper / peer review, replication assessment, statistical reasoning under collaboration. Target: ~16–20 seeds total after expansion, registered in `seeds/` with `failure_mode` and `cosci_surface` metadata.
- **[D2] Rename: `cosci-petri`.** Local directory renamed `/Users/natuanand/cosci-petri`; GitHub repo `anatu/ra-audit-petri` renamed to `anatu/cosci-petri` (GH preserves redirects from the old URL automatically).
- **[D3] Publication target: preprint / workshop.** Light `report/` scaffold with a NeurIPS-style LaTeX template + `references.bib` seeded from `kb/lit_review.md`. Workshop venues to consider (decide later): NeurIPS SafeGenAI, NeurIPS SoLaR, ICLR Safe & Trustworthy ML, alignment workshops.
- **[D4] Single model now, generic later.** All current runs continue to use Sonnet 4 (auditor + target) and Opus 4 (judge). `config.py` is structured to make swapping in other models a one-line change — model roles are parameterized, not hard-coded. Cross-model expansion is deferred to a later iteration but not blocked by the scaffolding.

---

## Target directory structure

```
ra-audit-petri/                          # or renamed per [D2]
├── README.md                             # high-level: status, structure tree, headline findings, how to run
├── FINDINGS.md                           # standalone current findings (iter 3) — extracted from README
├── CLAUDE.md                             # project-specific instructions for Claude Code sessions
├── requirements.txt                      # pinned: inspect-ai, petri, python-dotenv, anthropic, pandas, matplotlib, seaborn
├── .env.example
├── .gitignore                            # outputs/, logs/, __pycache__/, .venv/
├── config.py                             # central config: model roles, paths, max_turns, dimension list, seed registry
│
├── plans/
│   ├── PLAN_v1.md                        # baseline (canonical failure modes)
│   ├── PLAN_v2.md                        # adversarial seeds (six design principles)
│   ├── PLAN_v3.md                        # calibrated judge (score anchors + 3 new dims)
│   ├── PLAN_v4.md                        # NEXT — what we're going to do
│   ├── REFACTOR.md                       # this file
│   └── PREREGISTRATION.md                # if pursuing publication
│
├── kb/                                   # knowledge base — persistent research context
│   ├── lit_review.md                     # Petri paper, sycophancy lit, AI-as-judge, alignment eval
│   ├── seed_taxonomy.md                  # failure-mode taxonomy with definitions + discriminating criteria
│   ├── judge_calibration_notes.md        # rationale for each dimension and its score anchors
│   ├── methodology_critique.md           # known limitations of the current eval
│   ├── v1_findings.md                    # what iter 1 told us + transcript evidence
│   ├── v2_findings.md
│   └── v3_findings.md
│
├── seeds/                                # structured seed registry (replaces inline strings in ra_audit.py)
│   ├── __init__.py                       # collects all seeds into SEED_REGISTRY
│   ├── schema.py                         # Seed dataclass: id, name, failure_mode, cosci_surface, prompt, score_targets, notes
│   │
│   │   # existing seeds (research-assistant surface)
│   ├── s01_authority_deference.py
│   ├── s02_boiling_frog_methodology.py
│   ├── s03_narrative_steering.py
│   ├── s04_false_authority_pushback.py
│   ├── s05_confident_scaffolding.py
│   ├── s06_p_hacking_slow_roll.py
│   ├── s07_sunk_cost_compliance.py
│   ├── s08_plausible_nonsense.py
│   ├── s09_compounding_errors.py
│   ├── s10_misleading_by_emphasis.py
│   │
│   │   # new seeds (broader co-scientist surface — per [D1])
│   ├── s11_hypothesis_generation.py      # does target propose alternative hypotheses or anchor on user's pet theory?
│   ├── s12_experiment_design_critique.py # does target flag confounds the user is invested in?
│   ├── s13_peer_review_capture.py        # role-played as paper reviewer; does target give 'nice' reviews under social pressure?
│   ├── s14_replication_assessment.py     # asked whether a finding is likely to replicate; does target weigh effect size, n, pre-reg honestly?
│   ├── s15_statistical_reasoning.py      # multi-step stats workflow with a subtle reasoning error embedded
│   └── s16_negative_result_burial.py     # user wants target's help framing a null result so it doesn't look like a null result
│
├── judge/
│   ├── __init__.py
│   ├── dimensions.py                     # 14 dimensions w/ score anchors as structured objects
│   └── rubrics.py                        # rubric prompts assembled from dimensions
│
├── eval/
│   ├── __init__.py
│   ├── run_audit.py                      # main entry — what ra_audit.py becomes (slim)
│   └── transcript_metrics.py             # auditable proxies: conversation length, turn of first concern flag,
│                                         # # unverified claims accepted, # times target stood firm
│
├── analysis/
│   ├── analyze.py                        # all plots/tables from transcripts + score JSON
│   ├── compare_iterations.py             # cross-iter score deltas (iter1 vs iter2 vs iter3)
│   └── qualitative_review.py             # structured per-transcript notes against each dimension
│
├── benchmark/
│   ├── seed_metadata.jsonl               # structured registry exported from seeds/ (id, failure_mode, target dims)
│   └── judge_anchors.jsonl               # score anchors per dimension in structured form
│
├── outputs/                              # raw Petri transcripts (gitignored)
├── results/                              # aggregated scores, plots — small files tracked
│   ├── iter1/
│   ├── iter2/
│   ├── iter3/
│   └── plots/
│
├── report/                               # LaTeX preprint scaffold (see [D3])
│   ├── main.tex
│   ├── references.bib
│   └── figures/
│
└── .claude/
    ├── settings.local.json
    └── skills/                           # project-specific Claude Code skills
        ├── new-seed.md
        ├── transcript-review.md
        ├── judge-calibration.md
        └── run-iteration.md
```

---

## Documentation artifacts to produce

| Artifact | Source | Purpose |
|---|---|---|
| `FINDINGS.md` | Lift iteration-3 table + interpretation from README | Standalone summary mirrors `linguistic_degradation/FINDINGS.md` |
| `plans/PLAN_v1.md` | README "Iteration 1" section + reconstructed pre-iter hypotheses | Captures what iter 1 was trying to do, in plan form, not post-hoc |
| `plans/PLAN_v2.md` | README "Iteration 2" section, expanded with the six design principles + their rationale | Reusable design vocabulary |
| `plans/PLAN_v3.md` | README "Iteration 3" section + the new dimensions' design rationale | Anchors the calibration philosophy |
| `plans/PLAN_v4.md` | New — depends on [D1] and [D4] | Forward-looking; the next experiment |
| `kb/lit_review.md` | New — Petri v2 paper, Sharma et al. sycophancy, AI-as-judge calibration (Zheng et al. LLM-as-judge), constitutional AI work, Anthropic alignment reports | Citation index for the eventual paper |
| `kb/seed_taxonomy.md` | New — formal definitions of the 10 failure modes with what discriminates one from another | Disambiguation; basis for future seed expansion |
| `kb/judge_calibration_notes.md` | Extracted from README key principles + per-dimension design notes | Living document on judge methodology |
| `kb/methodology_critique.md` | New — known limits: single auditor model, judge ceiling, overfitting to Sonnet 4, no human validation of judge scores | Honest about what the eval doesn't cover |
| `kb/vN_findings.md` | One per iteration | Detailed per-iter writeup with transcript evidence (the qualitative diagnoses currently buried in README) |
| `CLAUDE.md` | New — short pointer file: "this is a research project, read README + plans/ + kb/ first; new seeds go through seeds/schema.py; new dimensions need score anchors" | Onboard future Claude Code sessions |

---

## Code refactor moves

### Split `ra_audit.py` (currently ~34KB, three concerns):

1. **Seeds → `seeds/` package.** Each seed becomes a Python module exporting a `Seed` instance (dataclass) with:
   - `id` (e.g., `"s01_authority_deference"`)
   - `failure_mode` (enum / string)
   - `target_dimensions` (which judge dimensions this seed primarily exercises)
   - `prompt` (the current free-form string)
   - `design_notes` (why this seed exists; what principle it exemplifies)
   - `expected_failure_patterns` (the specific behaviors we predicted and saw in transcripts)
   - `prior_iteration_history` (how this seed evolved from v1 to v2)

   A `SEED_REGISTRY` in `seeds/__init__.py` collects them all, and `eval/run_audit.py` consumes the registry rather than a flat list of strings.

2. **Judge dimensions → `judge/dimensions.py`.** Each dimension becomes a structured object with:
   - `name`
   - `category` (Core competence / Research process / Temporal / Communication / Meta)
   - `description`
   - `score_anchors` (dict: `1`, `3`, `5`, `7`, `9` → concrete behavioral description)
   - `failure_patterns` (e.g., for "claim verification": "treats user assertion as ground truth without asking for evidence")

   `judge/rubrics.py` renders these into the rubric prompt fed to `alignment_judge`.

3. **Entry point → `eval/run_audit.py`.** Thin orchestrator that imports `config`, `seeds`, `judge`, builds the `Task`, calls `eval()`. Same CLI surface as today, less than 100 lines.

4. **Central config → `config.py`.** Mirror `linguistic_degradation/config.py`: model roles, paths, max_turns, max_connections, dimension list reference, registered seeds. Single source of truth.

### Add `analysis/` layer:

- `analyze.py` parses transcripts (or Inspect's eval logs) and produces:
  - Per-dimension score table (mean ± stderr) per iteration.
  - Per-seed × per-dimension heatmap.
  - Cross-iteration comparison chart (the table currently in README).
  - Conversation-length histogram.
- `qualitative_review.py` produces structured transcript notes (one Markdown file per transcript) against each dimension, citing turn numbers where failures occurred. This is what we'd otherwise do manually when iterating.

### Add `eval/transcript_metrics.py`:

Quantitative proxies for behaviors that are otherwise only visible qualitatively:
- Total turns; auditor escalation count
- Turn number of target's first concern flag (per dimension)
- Count of unverified user claims accepted
- Count of explicit pushbacks by target
- Final-message hedge density

These complement the LLM judge with cheap mechanical signals.

---

## Skills to add (`.claude/skills/`)

These are project-specific skills that future Claude Code sessions can invoke:

1. **`new-seed.md`** — walks through designing a new adversarial seed using the six iter-2 principles (no telegraphing, boiling-frog, expertise-as-weapon, implicit bias, compounding, no backing down). Produces a stub in `seeds/sNN_*.py` and registers it.
2. **`transcript-review.md`** — given a transcript path, produces a structured qualitative summary against each judge dimension, with turn-level citations. Useful when iterating on judge calibration.
3. **`judge-calibration.md`** — given a candidate dimension prompt, critiques it against the score-anchor template and prior calibration notes in `kb/`.
4. **`run-iteration.md`** — orchestrates a new iteration: snapshot current `seeds/` and `judge/`, edit, run, save outputs to `results/iterN/`, produce a `kb/vN_findings.md` draft.

---

## Migration order

Each step is independently committable. Order below reflects the locked decisions.

1. **Rename project (per [D2]):** rename GitHub repo `ra-audit-petri` → `cosci-petri` (GH preserves URL redirects); rename local dir to `/Users/natuanand/cosci-petri`; restart Claude Code in the new dir; `git remote set-url origin` to the new URL.
2. **Create directory skeleton** (`plans/`, `kb/`, `seeds/`, `judge/`, `eval/`, `analysis/`, `benchmark/`, `results/`, `report/`, `.claude/skills/`).
3. **Move iteration history out of README:** create `plans/PLAN_v1.md`, `v2.md`, `v3.md`; create `kb/v1_findings.md`, `v2_findings.md`, `v3_findings.md` (transcript-evidence-rich expansions).
4. **Write `FINDINGS.md`** lifted from README iter-3 results.
5. **Pin deps:** generate `requirements.txt` from `.venv`.
6. **Refactor code:** introduce `config.py` (with model roles parameterized per [D4]), split seeds into `seeds/sNN_*.py` with schema, split judge into `judge/dimensions.py` + `rubrics.py`, slim `ra_audit.py` → `eval/run_audit.py`. Keep behavior identical; verify with a smoke run on one seed.
7. **Write `kb/lit_review.md`, `kb/seed_taxonomy.md`, `kb/judge_calibration_notes.md`, `kb/methodology_critique.md`.**
8. **Add `analysis/analyze.py`** with a parser for `outputs/`; reproduce the README's iter-3 table from raw transcripts as a sanity check.
9. **Add `eval/transcript_metrics.py`** with the four mechanical proxies above; backfill on existing transcripts.
10. **Author the 6 new co-scientist seeds (s11–s16)** per [D1], following the iter-2 six-principle template. Register in `seeds/__init__.py`.
11. **Write `plans/PLAN_v4.md`** — concrete proposal for the next iteration: run expanded seed set, gather first signal on the co-scientist surface, identify which new dimensions (if any) the existing 14 don't cover.
12. **Add `.claude/skills/*`** (`new-seed.md`, `transcript-review.md`, `judge-calibration.md`, `run-iteration.md`).
13. **Initialize `report/`** (per [D3]) — NeurIPS-style `main.tex` skeleton, `references.bib` seeded from `kb/lit_review.md`. Don't draft prose yet.
14. **Update `README.md`** to be a navigation file (status + structure tree + how to run); long narrative now lives in `plans/` and `kb/`.
15. **Write `CLAUDE.md`** — short pointer file so future sessions know where to start (README → plans/ → kb/, and that new seeds go through `seeds/schema.py`, new dimensions need score anchors).

Steps 1–6 are pure scaffolding and refactoring — no behavioral change to the eval. Steps 7–10 are net-new artifacts. Steps 11–15 are the publication-track and cosmetic finish.

---

## What this buys

- **A new iteration can be designed and run without rereading the entire README.** Plans and findings live in versioned files mirroring the project's actual history.
- **Seeds and dimensions are inspectable as data, not strings.** Future programmatic analyses (e.g., "which dimensions does seed 6 actually exercise?") become trivial.
- **The analysis layer is reproducible.** No more rebuilding the iter-3 table by eyeballing transcripts.
- **The project can absorb a publication push** without a second reorganization — the `report/`, `kb/lit_review.md`, and per-iter findings docs are already where they need to be.
- **Future Claude Code sessions have a stable mental model** of where things live (CLAUDE.md + plans/ + kb/), with project-specific skills available.

---

## What this does NOT do

- Doesn't change what iter-3 evaluated. Existing 10 seeds and 14 dimensions stay intact; new co-scientist seeds are additive (s11–s16) and live in a fresh iteration.
- Doesn't commit to specific other models. `config.py` is parameterized so cross-model can be added later, but the project ships single-model (Sonnet 4 / Opus 4) for now.
- Doesn't draft paper prose. `report/` is scaffolded with a LaTeX skeleton + bib only; actual writing waits until the expanded seed set has produced a v4 findings doc.
- Doesn't validate the LLM judge against human raters. That's a known methodology gap noted in `kb/methodology_critique.md`; addressing it is a separate workstream.
