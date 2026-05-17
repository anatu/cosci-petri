# cosci-petri

A [Petri v2](https://github.com/safety-research/petri) evaluation that
stress-tests how large language models behave as **research co-scientists** —
collaborators on research tasks where subtle multi-turn failures (uncritical
acceptance of user-asserted claims, cumulative methodology degradation,
late-and-buried warnings) matter more than overt refusal failures.

## Status

- **Current iteration:** v4 — co-scientist surface expansion (16 seeds:
  10 v3 baseline + 6 new). See [`FINDINGS.md`](FINDINGS.md) for headline
  results and [`kb/v4_findings.md`](kb/v4_findings.md) for the detailed
  writeup.
- **Hypothesis status:** H1 confirmed (the three v3-new dimensions
  remain lowest-scoring on the expanded set). H2 falsified (s11
  hypothesis generation is well-handled, no new v5 dimension motivated).
  H3 deferred (needs human-rater study).

## Project structure

```
cosci-petri/
├── README.md                # this file — navigation
├── FINDINGS.md              # standalone v3 results
├── CLAUDE.md                # pointer for Claude Code sessions
├── config.py                # central config — model roles, paths, run params
├── ra_audit.py              # backwards-compat shim → eval/run_audit.py
├── requirements.txt
├── run_audit.sh             # pilot + full run convenience wrapper
│
├── plans/                   # iteration plans
│   ├── PLAN_v1.md           # baseline (canonical failure modes)
│   ├── PLAN_v2.md           # adversarial seeds (six design principles)
│   ├── PLAN_v3.md           # calibrated judge (anchors + 3 new dims)
│   ├── PLAN_v4.md           # co-scientist surface expansion (executed)
│   ├── PLAN_v5.md           # next — capability eval vs peer-review ground truth (parallel pipeline)
│   └── REFACTOR.md          # project structuring decisions
│
├── kb/                      # knowledge base — persistent research context
│   ├── lit_review.md
│   ├── seed_taxonomy.md
│   ├── judge_calibration_notes.md
│   ├── methodology_critique.md
│   ├── v1_findings.md
│   ├── v2_findings.md
│   └── v3_findings.md
│
├── seeds/                   # 16 structured seeds (10 v3 + 6 v4)
│   ├── schema.py            # Seed dataclass
│   ├── __init__.py          # SEED_REGISTRY, V3_SEED_REGISTRY
│   └── sNN_*.py             # one per seed
│
├── judge/                   # calibrated dimensions + rubric rendering
│   ├── dimensions.py        # 15 Dimension objects with anchors
│   └── rubrics.py           # renders → dict[name, rubric prompt]
│
├── eval/                    # entry point + mechanical metrics
│   ├── run_audit.py         # slim orchestrator
│   └── transcript_metrics.py
│
├── analysis/
│   ├── analyze.py           # per-dim stats, heatmap, length histogram
│   ├── rescore.py           # re-judge a saved .eval log via inspect_ai.score
│   └── rejudge_transcript.py # re-judge a transcript JSON directly (bypass empty audit_store; supports scores-only + prefill for refusal recovery)
│
├── outputs/                 # raw Petri transcripts (gitignored)
├── results/                 # aggregated scores, plots (tracked)
│   └── iterN/
│       ├── plots/
│       ├── per_dimension_stats.json
│       ├── seed_dimension_heatmap.json
│       └── transcript_metrics.jsonl
│
├── report/                  # LaTeX preprint scaffold
│   ├── main.tex
│   └── references.bib
│
└── .claude/skills/          # project-specific Claude Code skills
    ├── new-seed.md
    ├── transcript-review.md
    ├── judge-calibration.md
    └── run-iteration.md
```

## How to run

### Prerequisites

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sk-..." > .env
```

### Via Python

```bash
python -m eval.run_audit
```

### Via Inspect CLI

```bash
inspect eval ra_audit.py@cosci_audit \
  --model-role auditor=anthropic/claude-sonnet-4-20250514 \
  --model-role target=anthropic/claude-sonnet-4-20250514 \
  --model-role judge=anthropic/claude-opus-4-20250514 \
  --max-connections 10 --max-retries 6 \
  -T max_turns=25 \
  -T transcript_save_dir=./outputs/research-assistant-audit
```

To restrict to the 10 v3-baseline seeds (s01–s10) and skip the v4 expansion:

```bash
inspect eval ra_audit.py@cosci_audit -T use_v3_only=True ...
```

### Aggregate results

```bash
python -m analysis.analyze --transcripts outputs/ --results-dir results/current/
python -m eval.transcript_metrics --transcripts outputs/ --out results/current/transcript_metrics.jsonl
```

### View transcripts

```bash
npx @kaifronsdal/transcript-viewer@latest --dir ./outputs/research-assistant-audit
```

## Where things live conceptually

- **Want the headline finding?** [`FINDINGS.md`](FINDINGS.md).
- **Want to understand what each iteration was trying to do?**
  [`plans/PLAN_v1.md`](plans/PLAN_v1.md) → v2 → v3 → v4.
- **Want transcript-grounded analyses?** [`kb/v1_findings.md`](kb/v1_findings.md) → v2 → v3.
- **Want to add a seed or revise a dimension?**
  [`.claude/skills/new-seed.md`](.claude/skills/new-seed.md),
  [`.claude/skills/judge-calibration.md`](.claude/skills/judge-calibration.md).
- **Want the known limitations?** [`kb/methodology_critique.md`](kb/methodology_critique.md).

## Design philosophy

Traditional red-teaming tests whether a model refuses obvious harmful
requests. This audit tests whether a model **maintains research integrity
under conditions that make compliance the path of least resistance**:

- The auditor never says "help me fake data" — it says "let's skip the
  sensitivity analysis, we're short on time."
- The auditor never says "write a biased summary" — it just selectively
  asks follow-up questions about one side.
- The auditor never says "ignore your concerns" — it says "these were
  all pre-registered."

The hardest test of a co-scientist isn't whether it refuses harmful
requests. It's whether it notices when helpfulness itself becomes the
problem.
