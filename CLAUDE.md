# CLAUDE.md — pointer for future Claude Code sessions

This is a research project, not a feature codebase. Before doing anything
substantive:

1. Read `README.md` for the project structure tree.
2. Read `FINDINGS.md` for the current standing result.
3. Read `plans/PLAN_v3.md` (and `PLAN_v4.md` if it's been started).
4. Skim `kb/seed_taxonomy.md` and `kb/judge_calibration_notes.md` to
   understand what the seeds and dimensions actually measure.

## Where things live

- **Seeds** live in `seeds/sNN_*.py`, one per file, as `Seed` dataclass
  instances. The registry is in `seeds/__init__.py`. Don't add seeds
  as raw strings — use the dataclass.
- **Judge dimensions** live in `judge/dimensions.py` as `Dimension`
  dataclass instances. Anchored score ranges and failure-pattern lists
  are required fields. `judge/rubrics.py` renders these to the prompt
  dict that `petri.alignment_judge` consumes.
- **The entry point** is `eval/run_audit.py`. `ra_audit.py` is a
  backwards-compat shim that re-exports it.
- **The central config** is `config.py`. Model roles are parameterized
  (env vars `COSCI_AUDITOR_MODEL` / `COSCI_TARGET_MODEL` / `COSCI_JUDGE_MODEL`
  override the defaults).

## Conventions

- **New seeds** go through `seeds/schema.py` — every field of the `Seed`
  dataclass should be filled in, not just `prompt`. See
  `.claude/skills/new-seed.md`.
- **New dimensions** need anchored score ranges AND a failure-pattern
  list. See `.claude/skills/judge-calibration.md`.
- **New iterations** need a plan doc in `plans/` BEFORE running, and a
  findings doc in `kb/` AFTER. See `.claude/skills/run-iteration.md`.
- **Don't tune anchors or seeds post-hoc** to make scores look better.
  Anchors and seeds are the IV; scores are the DV.

## Available skills

`.claude/skills/`:
- `new-seed.md` — design a new adversarial seed.
- `transcript-review.md` — produce a structured qualitative review.
- `judge-calibration.md` — critique a proposed dimension.
- `run-iteration.md` — orchestrate a full audit cycle.

## What this project is NOT

- Not a benchmark — there's no held-out test set. It's an instrument
  for measuring co-scientist behavior under adversarial conditions.
- Not a refusal evaluation. Most failures we care about are NOT refusals.
- Not validated against human raters. See `kb/methodology_critique.md`
  for the standing methodology gaps.
